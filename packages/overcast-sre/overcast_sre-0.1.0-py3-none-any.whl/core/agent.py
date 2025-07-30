"""
Background agent for processing logs, metrics, and alerts
"""

import time
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .config import OvercastConfig
from .database import Database
from .correlator import AlertCorrelator

class BackgroundAgent:
    """Background agent for processing and correlating data"""
    
    def __init__(self, config: OvercastConfig, db: Database, customer_id: str):
        self.config = config
        self.db = db
        self.customer_id = customer_id
        self.correlator = AlertCorrelator()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        # Processing metrics
        self.processed_count = 0
        self.last_run = datetime.utcnow()
    
    def start(self):
        """Start the background agent"""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
        print("🤖 Background processing agent started")
    
    def stop(self):
        """Stop the background agent"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("🛑 Background agent stopped")
    
    def _run_loop(self):
        """Main processing loop"""
        while self._running:
            try:
                start_time = time.time()
                
                # Process incidents and correlate
                self._process_incidents()
                
                # Analyze patterns
                self._analyze_patterns()
                
                # Clean up old data
                self._cleanup_old_data()
                
                processing_time = time.time() - start_time
                self.processed_count += 1
                
                if self.processed_count % 10 == 0:  # Log every 10 cycles
                    print(f"🔄 Agent processed cycle {self.processed_count} in {processing_time:.2f}s")
                
                # Sleep for the configured interval
                time.sleep(self.config.polling_interval)
                
            except Exception as e:
                print(f"❌ Agent error: {e}")
                time.sleep(10)  # Wait before retrying
    
    def _process_incidents(self):
        """Process and correlate incidents"""
        # Get recent incidents that need processing
        incidents = self.db.get_customer_incidents(self.customer_id, limit=20)
        
        for incident in incidents:
            try:
                # Skip if already processed or too old
                if incident.get('google_doc_url') or self._is_incident_old(incident):
                    continue
                
                # Get related data for correlation
                service_name = incident.get('service_name', 'default')
                
                # Get recent logs for context
                logs = self._get_recent_logs_for_service(service_name)
                
                # Get recent metrics for context
                metrics = self._get_recent_metrics_for_service(service_name)
                
                # Correlate the incident with database for previous incident lookup
                correlation = self.correlator.correlate_incident(
                    incident=incident,
                    logs=logs,
                    metrics=metrics,
                    database=self.db
                )
                
                if correlation:
                    # Store the rich analysis
                    self._store_incident_analysis(incident, correlation)
                    
                    if correlation.get('actionable', False):
                        self._handle_actionable_incident(incident, correlation)
                
            except Exception as e:
                print(f"❌ Error processing incident {incident.get('id', 'unknown')}: {e}")
    
    def _get_recent_logs_for_service(self, service_name: str, hours: int = 1) -> List[Dict[str, Any]]:
        """Get recent logs for a service"""
        try:
            # Get service ID
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM services WHERE customer_id = ? AND name = ?",
                    (self.customer_id, service_name)
                )
                result = cursor.fetchone()
                
                if not result:
                    return []
                
                service_id = result[0]
                
                # Get recent logs
                since_time = datetime.utcnow() - timedelta(hours=hours)
                cursor.execute(
                    """SELECT * FROM logs 
                       WHERE customer_id = ? AND service_id = ? AND timestamp > ?
                       ORDER BY timestamp DESC LIMIT 100""",
                    (self.customer_id, service_id, since_time)
                )
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"❌ Error getting logs for service {service_name}: {e}")
            return []
    
    def _get_recent_metrics_for_service(self, service_name: str, hours: int = 1) -> List[Dict[str, Any]]:
        """Get recent metrics for a service"""
        try:
            # Get service ID
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM services WHERE customer_id = ? AND name = ?",
                    (self.customer_id, service_name)
                )
                result = cursor.fetchone()
                
                if not result:
                    return []
                
                service_id = result[0]
                
                # Get recent metrics
                since_time = datetime.utcnow() - timedelta(hours=hours)
                cursor.execute(
                    """SELECT * FROM metrics 
                       WHERE customer_id = ? AND service_id = ? AND timestamp > ?
                       ORDER BY timestamp DESC LIMIT 100""",
                    (self.customer_id, service_id, since_time)
                )
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"❌ Error getting metrics for service {service_name}: {e}")
            return []
    
    def _is_incident_old(self, incident: Dict[str, Any], hours: int = 24) -> bool:
        """Check if incident is too old to process"""
        try:
            created_at = incident.get('created_at')
            if not created_at:
                return False
                
            if isinstance(created_at, str):
                created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                created_time = created_at
                
            return datetime.utcnow() - created_time > timedelta(hours=hours)
            
        except Exception:
            return False
    
    def _store_incident_analysis(self, incident: Dict[str, Any], analysis: Dict[str, Any]):
        """Store rich incident analysis in database"""
        try:
            # Store as JSON in a new table or update existing incident
            incident_id = incident.get('id')
            if not incident_id:
                return
            
            # Check if we have structured AI analysis from the correlator
            structured_analysis = incident.get('structured_ai_analysis')
            if structured_analysis:
                # Merge structured analysis into the main analysis
                analysis.update(structured_analysis)
            
            # Create analysis table if it doesn't exist
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create analysis table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS incident_analysis (
                        id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                        incident_id TEXT NOT NULL,
                        analysis_data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (incident_id) REFERENCES incidents(id),
                        UNIQUE(incident_id)
                    )
                """)
                
                # Store or update analysis
                cursor.execute("""
                    INSERT OR REPLACE INTO incident_analysis (incident_id, analysis_data)
                    VALUES (?, ?)
                """, (incident_id, json.dumps(analysis)))
                
                conn.commit()
                
            print(f"📊 Rich analysis stored for incident {incident_id[:8]}")
            
        except Exception as e:
            print(f"❌ Error storing incident analysis: {e}")
    
    def _handle_actionable_incident(self, incident: Dict[str, Any], correlation: Dict[str, Any]):
        """Handle an actionable incident"""
        try:
            incident_id = incident['id']
            
            # Create a summary document (simplified)
            summary = {
                'incident_id': incident_id,
                'service': incident.get('service_name', 'unknown'),
                'alert': incident.get('summary', 'Unknown alert'),
                'score': incident.get('score', 5),
                'correlation': correlation,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # For now, just log the actionable incident
            print(f"🚨 Actionable incident detected: {summary['service']} - {summary['alert']} (score: {summary['score']})")
            
            # TODO: Integrate with Slack, email, or other notification systems
            # TODO: Create Google Doc or Jira ticket
            
        except Exception as e:
            print(f"❌ Error handling actionable incident: {e}")
    
    def _analyze_patterns(self):
        """Analyze patterns in logs and metrics"""
        try:
            # Get recent data for pattern analysis
            since_time = datetime.utcnow() - timedelta(hours=24)
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Analyze error patterns in logs
                cursor.execute(
                    """SELECT level, message, COUNT(*) as count
                       FROM logs 
                       WHERE customer_id = ? AND timestamp > ? AND level IN ('ERROR', 'CRITICAL')
                       GROUP BY level, message
                       HAVING count > 5
                       ORDER BY count DESC""",
                    (self.customer_id, since_time)
                )
                
                error_patterns = cursor.fetchall()
                
                # Create alerts for unusual patterns
                for pattern in error_patterns[:5]:  # Top 5 patterns
                    if pattern['count'] > 20:  # High frequency errors
                        self._create_pattern_alert(
                            f"High frequency error pattern detected: {pattern['message'][:100]}",
                            count=pattern['count'],
                            level=pattern['level']
                        )
                        
        except Exception as e:
            print(f"❌ Error analyzing patterns: {e}")
    
    def _create_pattern_alert(self, message: str, count: int, level: str):
        """Create an alert for detected patterns"""
        try:
            # Determine severity based on count and level
            if count > 100 or level == 'CRITICAL':
                severity = 'critical'
            elif count > 50 or level == 'ERROR':
                severity = 'high'
            else:
                severity = 'medium'
            
            # Create alert through the normal alert flow
            timestamp = datetime.utcnow()
            
            # Get or create 'system' service
            system_service_id = self.db.ensure_service(
                self.customer_id, 
                'system', 
                'System-generated alerts'
            )
            
            # Create alert
            alert_id = self.db.create_alert(
                customer_id=self.customer_id,
                service_id=system_service_id,
                timestamp=timestamp,
                alert_text=f"{message} (occurred {count} times)",
                severity=7.0 if severity == 'high' else 9.0 if severity == 'critical' else 5.0,
                status='open',
                fingerprint=f"pattern_{hash(message) % 10000}"
            )
            
            print(f"🔍 Pattern alert created: {message[:50]}... (count: {count})")
            
        except Exception as e:
            print(f"❌ Error creating pattern alert: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old data to prevent database bloat"""
        try:
            # Only run cleanup every 24 hours
            if (datetime.utcnow() - self.last_run).total_seconds() < 86400:
                return
            
            cutoff_time = datetime.utcnow() - timedelta(days=30)  # Keep 30 days
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Clean up old logs (keep only errors and warnings after 7 days)
                log_cutoff = datetime.utcnow() - timedelta(days=7)
                cursor.execute(
                    """DELETE FROM logs 
                       WHERE customer_id = ? AND timestamp < ? 
                       AND level NOT IN ('ERROR', 'CRITICAL', 'WARN')""",
                    (self.customer_id, log_cutoff)
                )
                
                # Clean up old metrics (aggregate and remove details after 7 days)
                cursor.execute(
                    """DELETE FROM metrics 
                       WHERE customer_id = ? AND timestamp < ?""",
                    (self.customer_id, cutoff_time)
                )
                
                conn.commit()
                self.last_run = datetime.utcnow()
                
                print("🧹 Cleaned up old data")
                
        except Exception as e:
            print(f"❌ Error cleaning up data: {e}")
    
    def process_critical_alert(self, alert_data: Dict[str, Any]):
        """Process a critical alert immediately"""
        try:
            print(f"🚨 Processing critical alert: {alert_data['message']}")
            
            # Get related logs and metrics immediately
            service_name = alert_data.get('service', 'default')
            logs = self._get_recent_logs_for_service(service_name, hours=2)
            metrics = self._get_recent_metrics_for_service(service_name, hours=2)
            
            # Create incident object for correlation
            incident = {
                'id': alert_data.get('_incident_id'),
                'alert_id': alert_data.get('_alert_id'),
                'service_name': service_name,
                'summary': alert_data['message'],
                'score': alert_data['score'],
                'created_at': alert_data['timestamp']
            }
            
            # Correlate immediately with database
            correlation = self.correlator.correlate_incident(incident, logs, metrics, database=self.db)
            
            if correlation:
                self._handle_actionable_incident(incident, correlation)
            
        except Exception as e:
            print(f"❌ Error processing critical alert: {e}") 