"""
HTTP-based client for Overcast SDK - sends data to centralized server
"""

import os
import json
import time
import requests
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List
from queue import Queue, Empty
from .config import OvercastConfig

class OvercastHTTPClient:
    """HTTP client for Overcast SDK - sends data to centralized server"""
    
    def __init__(self, config: OvercastConfig):
        self.config = config
        self._running = False
        
        # Queues for buffering data
        self.log_queue = Queue()
        self.metric_queue = Queue()
        self.alert_queue = Queue()
        
        # HTTP session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-Key': config.api_key,
            'X-Customer-Name': config.customer_name
        })
        
        print(f"🔄 Overcast HTTP client initialized for customer: {config.customer_name}")
        print(f"📡 Server: {config.server_url}")
    
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
        """Start the background HTTP sender"""
        if self._running:
            return
        
        self._running = True
        
        # Start background threads
        self._start_queue_processors()
        
        print("🤖 Background HTTP sender started")
    
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
        """Process log queue and send to server"""
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
                    self._send_logs(batch)
                    batch = []
                
            except Exception as e:
                print(f"❌ Error processing logs: {e}")
    
    def _process_metrics(self):
        """Process metric queue and send to server"""
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
                    self._send_metrics(batch)
                    batch = []
                    
            except Exception as e:
                print(f"❌ Error processing metrics: {e}")
    
    def _process_alerts(self):
        """Process alert queue and send to server"""
        while self._running:
            try:
                alert_entry = self.alert_queue.get(timeout=1.0)
                self._send_alert(alert_entry)
                        
            except Empty:
                continue
            except Exception as e:
                print(f"❌ Error processing alerts: {e}")
    
    def _send_logs(self, logs: List[Dict[str, Any]]):
        """Send logs to server"""
        try:
            response = self.session.post(
                f"{self.config.server_url}/api/ingest/logs",
                json={'logs': logs},
                timeout=10
            )
            response.raise_for_status()
            
            if self.config.log_level == 'DEBUG':
                print(f"📤 Sent {len(logs)} logs to server")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send logs: {e}")
            # TODO: Could implement retry logic or local fallback storage
    
    def _send_metrics(self, metrics: List[Dict[str, Any]]):
        """Send metrics to server"""
        try:
            response = self.session.post(
                f"{self.config.server_url}/api/ingest/metrics",
                json={'metrics': metrics},
                timeout=10
            )
            response.raise_for_status()
            
            if self.config.log_level == 'DEBUG':
                print(f"📤 Sent {len(metrics)} metrics to server")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send metrics: {e}")
    
    def _send_alert(self, alert_entry: Dict[str, Any]):
        """Send alert to server"""
        try:
            response = self.session.post(
                f"{self.config.server_url}/api/ingest/alerts",
                json={'alert': alert_entry},
                timeout=10
            )
            response.raise_for_status()
            
            if self.config.log_level == 'DEBUG':
                print(f"📤 Sent alert to server")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send alert: {e}")
    
    def shutdown(self):
        """Shutdown the client"""
        self._running = False
        
        # Wait for queues to empty
        time.sleep(2)
        
        # Close HTTP session
        self.session.close()
        
        print("🔒 Overcast HTTP client shutdown") 