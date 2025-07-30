"""
Overcast SDK - Simple monitoring and incident management for startups
"""

import os
import json
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any

try:
    # Try relative imports first (when used as a module)
    from .core.http_client import OvercastHTTPClient
    from .core.client import OvercastClient
    from .core.config import OvercastConfig
except ImportError:
    # Fall back to absolute imports (when run directly)
    from core.http_client import OvercastHTTPClient
    from core.client import OvercastClient
    from core.config import OvercastConfig

# Global client instance
_client: Optional[OvercastHTTPClient] = None
_config: Optional[OvercastConfig] = None

def init(api_key: str, customer_name: str = "Default Customer", server_url: str = "http://localhost:8001", db_path: str = None, use_local_db: bool = False):
    """
    Initialize the Overcast SDK
    
    Args:
        api_key: Your Overcast API key
        customer_name: Your organization name
        server_url: Overcast server URL (default: localhost:8001 for SaaS mode)
        db_path: Database path (only used if use_local_db=True)
        use_local_db: Set to True to use local database instead of sending to server
    """
    global _client, _config
    
    _config = OvercastConfig(
        api_key=api_key,
        customer_name=customer_name,
        server_url=server_url,
        db_path=db_path or "overcast_data.db"
    )
    
    if use_local_db:
        # Use local database (original single-tenant mode)
        from .core.client import OvercastClient
        from .core.database import Database
        
        # If db_path is not specified, use the SDK directory
        if db_path is None:
            sdk_dir = os.path.dirname(os.path.abspath(__file__))
            _config.db_path = os.path.join(sdk_dir, "overcast_data.db")
        
        _client = OvercastClient(_config)
        print(f"✅ Overcast SDK initialized for {customer_name} (LOCAL MODE)")
        print(f"📊 Database: {_config.db_path}")
    else:
        # Use HTTP client (multi-tenant SaaS mode)
        _client = OvercastHTTPClient(_config)
        print(f"✅ Overcast SDK initialized for {customer_name} (SaaS MODE)")
        print(f"📡 Server: {server_url}")
    
    # Start background agent/sender
    _client.start_agent()

def log(message: str, level: str = "INFO", service: str = "default", **kwargs):
    """
    Log a message with Overcast
    
    Args:
        message: The log message
        level: Log level (DEBUG, INFO, WARN, ERROR, CRITICAL)
        service: Service name
        **kwargs: Additional metadata
    """
    if not _client:
        raise RuntimeError("Overcast SDK not initialized. Call overcast.init() first.")
    
    _client.log(message, level, service, **kwargs)

def metric(name: str, value: float, tags: Optional[Dict[str, str]] = None, service: str = "default"):
    """
    Record a metric with Overcast
    
    Args:
        name: Metric name
        value: Metric value
        tags: Optional tags/labels
        service: Service name
    """
    if not _client:
        raise RuntimeError("Overcast SDK not initialized. Call overcast.init() first.")
    
    _client.metric(name, value, tags or {}, service)

def alert(message: str, severity: str = "high", service: str = "default", **kwargs):
    """
    Send an alert to Overcast
    
    Args:
        message: Alert message
        severity: Alert severity (low, medium, high, critical)
        service: Service name
        **kwargs: Additional metadata
    """
    if not _client:
        raise RuntimeError("Overcast SDK not initialized. Call overcast.init() first.")
    
    _client.alert(message, severity, service, **kwargs)

def shutdown():
    """
    Shutdown the Overcast SDK
    """
    global _client
    if _client:
        _client.shutdown()
        _client = None
        print("🔒 Overcast SDK shutdown")

# Context manager support
class OvercastContext:
    def __init__(self, api_key: str, customer_name: str = "Default Customer", server_url: str = "http://localhost:8001", db_path: str = None, use_local_db: bool = False):
        self.api_key = api_key
        self.customer_name = customer_name
        self.server_url = server_url
        self.db_path = db_path
        self.use_local_db = use_local_db
    
    def __enter__(self):
        init(self.api_key, self.customer_name, self.server_url, self.db_path, self.use_local_db)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        shutdown()

# Aliases for convenience (plural forms)
def logs(message: str, level: str = "INFO", service: str = "default", **kwargs):
    """Alias for log() function"""
    return log(message, level, service, **kwargs)

def metrics(name: str, value: float, tags: Optional[Dict[str, str]] = None, service: str = "default"):
    """Alias for metric() function"""
    return metric(name, value, tags, service)

# Export main functions
__all__ = ['init', 'log', 'logs', 'metric', 'metrics', 'alert', 'shutdown', 'OvercastContext'] 