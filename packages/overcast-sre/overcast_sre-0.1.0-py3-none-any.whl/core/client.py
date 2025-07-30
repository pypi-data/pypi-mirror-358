"""
Main client for Overcast SDK
"""

import os
import json
import time
import sqlite3
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List
from queue import Queue, Empty
from .config import OvercastConfig
from .database import Database
from .agent import BackgroundAgent

class OvercastClient:
    """Main client for Overcast SDK operations"""
    
    def __init__(self, config: OvercastConfig):
        self.config = config
        self.db = Database(config.db_path)
        self.agent: Optional[BackgroundAgent] = None
        self._running = False
        
        # Queues for buffering data
        self.log_queue = Queue()
        self.metric_queue = Queue()
        self.alert_queue = Queue()
        
        # Initialize database
        self.db.initialize()
        
        # Ensure customer exists
        self.customer_id = self.db.ensure_customer(config.customer_name, config.api_key)
        
        print(f"🔄 Overcast client initialized for customer: {config.customer_name}")
    
    def log(self, message: str, level: str = "INFO", service: str = "default", **kwargs):
        """Log a message"""
        timestamp = datetime.utcnow()
        
        log_entry = {
            'timestamp': timestamp.isoformat(),
            'level': level.upper(),
            'service': service,
            'message': message,
            'metadata': kwargs
        }
        
        # Add to queue for background processing
        self.log_queue.put(log_entry)
        
        # Immediate console output for debugging
        if self.config.log_level in ['DEBUG', 'INFO']:
            print(f"[{timestamp.strftime('%H:%M:%S')}] {level} {service}: {message}")
    
    def metric(self, name: str, value: float, tags: Dict[str, str], service: str = "default"):
        """Record a metric"""
        timestamp = datetime.utcnow()
        
        metric_entry = {
            'timestamp': timestamp.isoformat(),
            'service': service,
            'name': name,
            'value': value,
            'tags': tags
        }
        
        # Add to queue for background processing
        self.metric_queue.put(metric_entry)
        
        # Immediate console output for debugging
        if self.config.log_level == 'DEBUG':
            print(f"[{timestamp.strftime('%H:%M:%S')}] METRIC {service}.{name}: {value}")
    
    def alert(self, message: str, severity: str = "high", service: str = "default", **kwargs):
        """Send an alert"""
        timestamp = datetime.utcnow()
        
        # Convert severity to score for consistency
        severity_scores = {
            'low': 3,
            'medium': 5,
            'high': 7,
            'critical': 9
        }
        score = severity_scores.get(severity.lower(), 5)
        
        alert_entry = {
            'timestamp': timestamp.isoformat(),
            'service': service,
            'message': message,
            'severity': severity,
            'score': score,
            'metadata': kwargs,
            'fingerprint': self._generate_fingerprint(service, message)
        }
        
        # Add to queue for immediate processing (alerts are high priority)
        self.alert_queue.put(alert_entry)
        
        # Immediate console output
        print(f"🚨 [{timestamp.strftime('%H:%M:%S')}] ALERT {service}: {message} (severity: {severity})")
    
    def _generate_fingerprint(self, service: str, message: str) -> str:
        """Generate a unique fingerprint for deduplication"""
        import hashlib
        text = f"{service}:{message}"
        return hashlib.md5(text.encode()).hexdigest()[:16]
    
    def start_agent(self):
        """Start the background agent"""
        if self._running:
            return
        
        self._running = True
        self.agent = BackgroundAgent(self.config, self.db, self.customer_id)
        
        # Start background threads
        self._start_queue_processors()
        
        # Start the main agent
        self.agent.start()
        
        print("🤖 Background agent started")
    
    def _start_queue_processors(self):
        """Start threads to process queued data"""
        # Log processor
        log_thread = threading.Thread(target=self._process_logs, daemon=True)
        log_thread.start()
        
        # Metric processor
        metric_thread = threading.Thread(target=self._process_metrics, daemon=True)
        metric_thread.start()
        
        # Alert processor (high priority)
        alert_thread = threading.Thread(target=self._process_alerts, daemon=True)
        alert_thread.start()
    
    def _process_logs(self):
        """Process log queue"""
        batch = []
        while self._running:
            try:
                # Collect logs in batches
                while len(batch) < self.config.batch_size:
                    try:
                        log_entry = self.log_queue.get(timeout=1.0)
                        batch.append(log_entry)
                    except Empty:
                        break
                
                if batch:
                    self._store_logs(batch)
                    batch = []
                
            except Exception as e:
                print(f"❌ Error processing logs: {e}")
    
    def _process_metrics(self):
        """Process metric queue"""
        batch = []
        while self._running:
            try:
                # Collect metrics in batches
                while len(batch) < self.config.batch_size:
                    try:
                        metric_entry = self.metric_queue.get(timeout=1.0)
                        batch.append(metric_entry)
                    except Empty:
                        break
                
                if batch:
                    self._store_metrics(batch)
                    batch = []
                    
            except Exception as e:
                print(f"❌ Error processing metrics: {e}")
    
    def _process_alerts(self):
        """Process alert queue (high priority)"""
        while self._running:
            try:
                alert_entry = self.alert_queue.get(timeout=1.0)
                self._store_alert(alert_entry)
                
                # Trigger immediate processing for high severity alerts
                if alert_entry['score'] >= 7:
                    if self.agent:
                        self.agent.process_critical_alert(alert_entry)
                        
            except Empty:
                continue
            except Exception as e:
                print(f"❌ Error processing alerts: {e}")
    
    def _store_logs(self, logs: List[Dict[str, Any]]):
        """Store logs in database"""
        for log_entry in logs:
            try:
                # Ensure service exists
                service_id = self.db.ensure_service(
                    self.customer_id, 
                    log_entry['service'], 
                    f"Service for {log_entry['service']}"
                )
                
                # Store log
                self.db.store_log(
                    customer_id=self.customer_id,
                    service_id=service_id,
                    timestamp=datetime.fromisoformat(log_entry['timestamp']),
                    level=log_entry['level'],
                    message=log_entry['message'],
                    metadata=json.dumps(log_entry['metadata']) if log_entry['metadata'] else None
                )
                
            except Exception as e:
                print(f"❌ Error storing log: {e}")
    
    def _store_metrics(self, metrics: List[Dict[str, Any]]):
        """Store metrics in database"""
        for metric_entry in metrics:
            try:
                # Ensure service exists
                service_id = self.db.ensure_service(
                    self.customer_id, 
                    metric_entry['service'], 
                    f"Service for {metric_entry['service']}"
                )
                
                # Store metric
                self.db.store_metric(
                    customer_id=self.customer_id,
                    service_id=service_id,
                    timestamp=datetime.fromisoformat(metric_entry['timestamp']),
                    name=metric_entry['name'],
                    value=metric_entry['value'],
                    tags=json.dumps(metric_entry['tags']) if metric_entry['tags'] else None
                )
                
            except Exception as e:
                print(f"❌ Error storing metric: {e}")
    
    def _store_alert(self, alert_entry: Dict[str, Any]):
        """Store alert in database"""
        try:
            # Ensure service exists
            service_id = self.db.ensure_service(
                self.customer_id, 
                alert_entry['service'], 
                f"Service for {alert_entry['service']}"
            )
            
            # Store alert
            alert_id = self.db.create_alert(
                customer_id=self.customer_id,
                service_id=service_id,
                timestamp=datetime.fromisoformat(alert_entry['timestamp']),
                alert_text=alert_entry['message'],
                severity=float(alert_entry['score']),
                status='open',
                fingerprint=alert_entry['fingerprint']
            )
            
            # Create incident if score is high enough
            if alert_entry['score'] >= 5:
                incident_id = self.db.create_incident(
                    customer_id=self.customer_id,
                    alert_id=alert_id,
                    summary=alert_entry['message'],
                    score=float(alert_entry['score']),
                    status='open',
                    google_doc_url=None
                )
                
                alert_entry['_incident_id'] = incident_id
                alert_entry['_alert_id'] = alert_id
            
        except Exception as e:
            print(f"❌ Error storing alert: {e}")
    
    def shutdown(self):
        """Shutdown the client"""
        self._running = False
        
        if self.agent:
            self.agent.stop()
        
        # Wait for queues to empty
        time.sleep(2)
        
        print("🔒 Overcast client shutdown") 