"""
Configuration management for Overcast SDK
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class OvercastConfig:
    """Configuration for Overcast SDK"""
    
    api_key: str
    customer_name: str = "Default Customer"
    server_url: str = "http://localhost:8001"
    
    # Database settings
    db_path: str = "overcast_data.db"
    
    # Agent settings
    polling_interval: int = 30  # seconds
    batch_size: int = 100
    
    # Log settings
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Dashboard settings
    dashboard_port: int = 5000
    dashboard_host: str = "0.0.0.0"
    
    # CLI settings
    cli_enabled: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.api_key:
            raise ValueError("API key is required")
        
        # Ensure db_path is absolute
        if not os.path.isabs(self.db_path):
            self.db_path = os.path.abspath(self.db_path) 
    
    @classmethod
    def from_env(cls) -> 'OvercastConfig':
        """Create configuration from environment variables"""
        return cls(
            api_key=os.getenv("OVERCAST_API_KEY", ""),
            customer_name=os.getenv("OVERCAST_CUSTOMER_NAME", "Default Customer"),
            server_url=os.getenv("OVERCAST_SERVER_URL", "http://localhost:8001"),
            db_path=os.getenv("OVERCAST_DB_PATH", "overcast_data.db"),
            polling_interval=int(os.getenv("OVERCAST_POLLING_INTERVAL", "30")),
            batch_size=int(os.getenv("OVERCAST_BATCH_SIZE", "100")),
            log_level=os.getenv("OVERCAST_LOG_LEVEL", "INFO"),
            dashboard_port=int(os.getenv("OVERCAST_DASHBOARD_PORT", "5000")),
            dashboard_host=os.getenv("OVERCAST_DASHBOARD_HOST", "0.0.0.0"),
        )
    
    def print_summary(self):
        """Print configuration summary"""
        print("=== Overcast SDK Configuration ===")
        print(f"Customer: {self.customer_name}")
        print(f"API Key: {self.api_key[:10]}***")
        print(f"Server URL: {self.server_url}")
        print(f"Database: {self.db_path}")
        print(f"Dashboard: {self.dashboard_host}:{self.dashboard_port}")
        print("==================================") 