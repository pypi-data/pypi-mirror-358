"""
SQLite database module for Overcast SDK
"""

import os
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import contextmanager

class Database:
    """SQLite database for Overcast SDK"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Ensure the directory for the database exists"""
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with automatic cleanup"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def initialize(self):
        """Initialize the database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                    name TEXT NOT NULL,
                    api_key TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create services table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS services (
                    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                    customer_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id),
                    UNIQUE(customer_id, name)
                )
            """)
            
            # Create alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                    customer_id TEXT NOT NULL,
                    service_id TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    alert_text TEXT NOT NULL,
                    severity REAL,
                    status TEXT DEFAULT 'open',
                    fingerprint TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id),
                    FOREIGN KEY (service_id) REFERENCES services(id)
                )
            """)
            
            # Create incidents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                    customer_id TEXT NOT NULL,
                    alert_id TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    score REAL,
                    status TEXT DEFAULT 'open',
                    google_doc_url TEXT,
                    is_alert_sent BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id),
                    FOREIGN KEY (alert_id) REFERENCES alerts(id)
                )
            """)
            
            # Create incident timeline table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incident_timeline (
                    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                    incident_id TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    description TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (incident_id) REFERENCES incidents(id)
                )
            """)
            
            # Create logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                    customer_id TEXT NOT NULL,
                    service_id TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id),
                    FOREIGN KEY (service_id) REFERENCES services(id)
                )
            """)
            
            # Create metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                    customer_id TEXT NOT NULL,
                    service_id TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id),
                    FOREIGN KEY (service_id) REFERENCES services(id)
                )
            """)
            
            # Create deployments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deployments (
                    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                    customer_id TEXT NOT NULL,
                    service_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    author TEXT,
                    description TEXT,
                    deployed_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id),
                    FOREIGN KEY (service_id) REFERENCES services(id)
                )
            """)
            
            # Create config changes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config_changes (
                    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                    customer_id TEXT NOT NULL,
                    service_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT NOT NULL,
                    changed_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id),
                    FOREIGN KEY (service_id) REFERENCES services(id)
                )
            """)
            
            # Create indices for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_customer_timestamp ON alerts(customer_id, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_customer_created ON incidents(customer_id, created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_customer_timestamp ON logs(customer_id, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_customer_timestamp ON metrics(customer_id, timestamp)")
            
            conn.commit()
    
    def ensure_customer(self, name: str, api_key: str) -> str:
        """Ensure customer exists and return ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if customer exists
            cursor.execute("SELECT id FROM customers WHERE api_key = ?", (api_key,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            
            # Create new customer
            customer_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO customers (id, name, api_key) VALUES (?, ?, ?)",
                (customer_id, name, api_key)
            )
            conn.commit()
            return customer_id
    
    def ensure_service(self, customer_id: str, name: str, description: str = None) -> str:
        """Ensure service exists and return ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if service exists
            cursor.execute(
                "SELECT id FROM services WHERE customer_id = ? AND name = ?",
                (customer_id, name)
            )
            result = cursor.fetchone()
            
            if result:
                return result[0]
            
            # Create new service
            service_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO services (id, customer_id, name, description) VALUES (?, ?, ?, ?)",
                (service_id, customer_id, name, description)
            )
            conn.commit()
            return service_id
    
    def create_alert(self, customer_id: str, service_id: str, timestamp: datetime, 
                    alert_text: str, severity: float = None, status: str = 'open', 
                    fingerprint: str = None) -> str:
        """Create a new alert"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            alert_id = str(uuid.uuid4())
            cursor.execute(
                """INSERT INTO alerts (id, customer_id, service_id, timestamp, alert_text, 
                                     severity, status, fingerprint) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (alert_id, customer_id, service_id, timestamp, alert_text, severity, status, fingerprint)
            )
            conn.commit()
            return alert_id
    
    def create_incident(self, customer_id: str, alert_id: str, summary: str, 
                       score: float = None, status: str = 'open', 
                       google_doc_url: str = None) -> str:
        """Create a new incident"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            incident_id = str(uuid.uuid4())
            cursor.execute(
                """INSERT INTO incidents (id, customer_id, alert_id, summary, score, 
                                        status, google_doc_url) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (incident_id, customer_id, alert_id, summary, score, status, google_doc_url)
            )
            conn.commit()
            return incident_id
    
    def store_log(self, customer_id: str, service_id: str, timestamp: datetime,
                  level: str, message: str, metadata: str = None):
        """Store a log entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            log_id = str(uuid.uuid4())
            cursor.execute(
                """INSERT INTO logs (id, customer_id, service_id, timestamp, level, 
                                   message, metadata) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (log_id, customer_id, service_id, timestamp, level, message, metadata)
            )
            conn.commit()
            return log_id
    
    def store_metric(self, customer_id: str, service_id: str, timestamp: datetime,
                     name: str, value: float, tags: str = None):
        """Store a metric"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            metric_id = str(uuid.uuid4())
            cursor.execute(
                """INSERT INTO metrics (id, customer_id, service_id, timestamp, name, 
                                      value, tags) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (metric_id, customer_id, service_id, timestamp, name, value, tags)
            )
            conn.commit()
            return metric_id
    
    def get_customer_incidents(self, customer_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent incidents for a customer"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT i.*, a.alert_text, s.name as service_name
                   FROM incidents i
                   LEFT JOIN alerts a ON i.alert_id = a.id
                   LEFT JOIN services s ON a.service_id = s.id
                   WHERE i.customer_id = ?
                   ORDER BY i.created_at DESC
                   LIMIT ?""",
                (customer_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_logs(self, customer_id: str, service_id: str = None, 
                       limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent logs for a customer"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if service_id:
                cursor.execute(
                    """SELECT l.*, s.name as service_name
                       FROM logs l
                       LEFT JOIN services s ON l.service_id = s.id
                       WHERE l.customer_id = ? AND l.service_id = ?
                       ORDER BY l.timestamp DESC
                       LIMIT ?""",
                    (customer_id, service_id, limit)
                )
            else:
                cursor.execute(
                    """SELECT l.*, s.name as service_name
                       FROM logs l
                       LEFT JOIN services s ON l.service_id = s.id
                       WHERE l.customer_id = ?
                       ORDER BY l.timestamp DESC
                       LIMIT ?""",
                    (customer_id, limit)
                )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_metrics(self, customer_id: str, service_id: str = None,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent metrics for a customer"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if service_id:
                cursor.execute(
                    """SELECT m.*, s.name as service_name
                       FROM metrics m
                       LEFT JOIN services s ON m.service_id = s.id
                       WHERE m.customer_id = ? AND m.service_id = ?
                       ORDER BY m.timestamp DESC
                       LIMIT ?""",
                    (customer_id, service_id, limit)
                )
            else:
                cursor.execute(
                    """SELECT m.*, s.name as service_name
                       FROM metrics m
                       LEFT JOIN services s ON m.service_id = s.id
                       WHERE m.customer_id = ?
                       ORDER BY m.timestamp DESC
                       LIMIT ?""",
                    (customer_id, limit)
                )
            return [dict(row) for row in cursor.fetchall()] 