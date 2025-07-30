# Overcast SDK

🌩️ **Simple monitoring and incident management for startups**

The Overcast SDK provides an easy way to add monitoring, logging, and incident management to your application without complex infrastructure setup. Perfect for startups that need observability but don't have dedicated DevOps teams or complex logging infrastructure.

## Features

✅ **Simple Integration** - Just 3 lines of code to get started  
✅ **Self-Contained** - Uses SQLite database, no external dependencies  
✅ **Real-time Dashboard** - Web UI for monitoring incidents and metrics  
✅ **CLI Tools** - Command-line interface for incident management  
✅ **Smart Correlation** - Automatic incident detection and correlation  
✅ **Lightweight** - Minimal performance impact on your application  

## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Basic Usage

```python
import overcast

# Initialize the SDK
overcast.init(
    api_key="your-api-key-here", 
    customer_name="Your Startup"
)

# Log events
overcast.log("User login successful", level="INFO", service="auth")

# Record metrics
overcast.metric("response_time", 0.23, tags={"endpoint": "/api/users"})

# Send alerts
overcast.alert("Database connection failed", severity="high", service="db")

# Shutdown when done
overcast.shutdown()
```

### 3. Context Manager (Recommended)

```python
import overcast

with overcast.OvercastContext(api_key="your-key", customer_name="Your Startup"):
    overcast.log("Application started", service="web-app")
    overcast.metric("startup_time", 1.2, service="web-app")
    
    # Your business logic here
    do_business_logic()
    
    # Overcast automatically shuts down when exiting context
```

## Dashboard & CLI

### Web Dashboard

Start the dashboard to monitor your incidents in real-time:

```bash
python -m sdk.server --api-key your-key --customer-name "Your Startup"
```

Visit `http://localhost:5000` to see:
- Real-time incident overview
- Service health metrics
- Interactive charts and analytics
- Incident timeline and history

### Command Line Interface

Use the CLI for incident management:

```bash
# Start interactive CLI
python -m sdk.server --api-key your-key --cli-only

# Available commands:
overcast list          # Show recent incidents
overcast triage        # Auto-triage incidents 
overcast logs [service] # Show recent logs
overcast metrics [service] # Show recent metrics
overcast status        # System status
```

## API Reference

### Core Functions

#### `overcast.init(api_key, customer_name, server_url)`
Initialize the Overcast SDK.

**Parameters:**
- `api_key` (str): Your Overcast API key
- `customer_name` (str): Your organization name  
- `server_url` (str, optional): Server URL (default: localhost)

#### `overcast.log(message, level, service, **kwargs)`
Log a message with context.

**Parameters:**
- `message` (str): Log message
- `level` (str): Log level (DEBUG, INFO, WARN, ERROR, CRITICAL)
- `service` (str): Service name (default: "default")
- `**kwargs`: Additional metadata

#### `overcast.metric(name, value, tags, service)`
Record a metric value.

**Parameters:**
- `name` (str): Metric name
- `value` (float): Metric value
- `tags` (dict, optional): Key-value tags
- `service` (str): Service name (default: "default")

#### `overcast.alert(message, severity, service, **kwargs)`
Send an alert for immediate attention.

**Parameters:**
- `message` (str): Alert message
- `severity` (str): Alert severity (low, medium, high, critical)
- `service` (str): Service name (default: "default")
- `**kwargs`: Additional metadata

#### `overcast.shutdown()`
Shutdown the SDK and clean up resources.

## Integration Examples

### Web Application (Flask/Django)

```python
from flask import Flask
import overcast

app = Flask(__name__)

# Initialize Overcast
overcast.init(api_key="your-key", customer_name="Your Web App")

@app.route('/api/users')
def get_users():
    start_time = time.time()
    
    try:
        overcast.log("Fetching users", level="INFO", service="web-api")
        
        # Your business logic
        users = fetch_users_from_db()
        
        # Record response time
        response_time = time.time() - start_time
        overcast.metric("response_time", response_time, 
                       tags={"endpoint": "/api/users"})
        
        return jsonify(users)
        
    except Exception as e:
        overcast.log(f"Failed to fetch users: {e}", level="ERROR", service="web-api")
        overcast.alert(f"API error: {e}", severity="high", service="web-api")
        return jsonify({"error": "Internal server error"}), 500

# Shutdown on app teardown
@app.teardown_appcontext
def shutdown_overcast(error):
    overcast.shutdown()
```

### Background Jobs

```python
import overcast

def process_user_data(user_id):
    with overcast.OvercastContext(api_key="your-key", customer_name="Background Jobs"):
        try:
            overcast.log(f"Processing user {user_id}", service="background-worker")
            
            # Process data
            result = expensive_data_processing(user_id)
            
            # Record success
            overcast.metric("job_success", 1, tags={"user_id": user_id})
            overcast.log(f"User {user_id} processed successfully", service="background-worker")
            
            return result
            
        except Exception as e:
            overcast.log(f"Failed to process user {user_id}: {e}", 
                        level="ERROR", service="background-worker")
            overcast.alert(f"Background job failed: {e}", 
                          severity="medium", service="background-worker")
            raise
```

### Database Operations

```python
import overcast

class Database:
    def __init__(self, connection_string):
        overcast.init(api_key="your-key", customer_name="Database Layer")
        self.connection = create_connection(connection_string)
    
    def execute_query(self, query, params=None):
        start_time = time.time()
        
        try:
            overcast.log(f"Executing query: {query[:50]}...", service="database")
            
            result = self.connection.execute(query, params)
            
            # Record query performance
            query_time = time.time() - start_time
            overcast.metric("query_duration", query_time, 
                           tags={"query_type": query.split()[0].upper()})
            
            return result
            
        except Exception as e:
            overcast.log(f"Query failed: {e}", level="ERROR", service="database")
            
            # Alert for critical database errors
            if "connection" in str(e).lower():
                overcast.alert(f"Database connection error: {e}", 
                              severity="critical", service="database")
            else:
                overcast.alert(f"Database query error: {e}", 
                              severity="high", service="database")
            raise
```

## Configuration

### Environment Variables

You can use environment variables instead of hardcoding configuration:

```bash
export OVERCAST_API_KEY="your-api-key"
export OVERCAST_CUSTOMER_NAME="Your Startup"
export OVERCAST_DB_PATH="./data/overcast.db"
export OVERCAST_DASHBOARD_PORT="5000"
```

```python
from sdk.core.config import OvercastConfig

# Load from environment
config = OvercastConfig.from_env()
```

### Advanced Configuration

```python
from sdk.core.config import OvercastConfig

config = OvercastConfig(
    api_key="your-key",
    customer_name="Your Startup",
    db_path="./data/overcast.db",          # Database location
    polling_interval=30,                    # Agent polling interval (seconds)
    batch_size=100,                        # Batch size for processing
    log_level="INFO",                      # SDK log level
    dashboard_port=5000,                   # Dashboard port
    dashboard_host="0.0.0.0"              # Dashboard host
)
```

## How It Works

1. **Data Collection**: The SDK collects logs, metrics, and alerts from your application
2. **Local Storage**: Data is stored in a local SQLite database (no external dependencies)
3. **Background Processing**: A background agent analyzes patterns and correlates incidents
4. **Smart Alerting**: The system automatically detects anomalies and actionable incidents
5. **Visualization**: The dashboard provides real-time visibility into system health

## Architecture

```
Your Application
       ↓
   Overcast SDK
       ↓
   SQLite Database  →  Background Agent  →  Dashboard & CLI
       ↓                      ↓                    ↓
   Logs, Metrics,      Pattern Analysis,     Real-time UI,
   Alerts              Incident Correlation  Incident Management
```

## Best Practices

### 1. Service Organization
Organize your logging by service/component:

```python
# Good: Organized by service
overcast.log("User authenticated", service="auth")
overcast.log("Order processed", service="orders") 
overcast.log("Payment completed", service="payments")

# Avoid: Everything in default service
overcast.log("Something happened")  # service="default"
```

### 2. Meaningful Metrics
Use descriptive metric names and relevant tags:

```python
# Good: Descriptive with context
overcast.metric("http_request_duration", 0.25, 
               tags={"method": "POST", "endpoint": "/api/orders", "status": "200"})

# Avoid: Generic metrics without context
overcast.metric("duration", 0.25)
```

### 3. Appropriate Alert Levels
Use severity levels appropriately:

```python
# Critical: System is down, immediate action required
overcast.alert("Database connection lost", severity="critical")

# High: Significant impact, investigate promptly  
overcast.alert("API error rate > 10%", severity="high")

# Medium: Monitor closely, may need attention
overcast.alert("Slow response times detected", severity="medium")

# Low: Informational, routine monitoring
overcast.alert("Cache miss rate increased", severity="low")
```

### 4. Resource Management
Always clean up resources:

```python
# Recommended: Use context manager
with overcast.OvercastContext(api_key="key", customer_name="app"):
    # Your code here
    pass  # Automatic cleanup

# Alternative: Manual cleanup
overcast.init(api_key="key", customer_name="app")
try:
    # Your code here
    pass
finally:
    overcast.shutdown()
```

## Troubleshooting

### Common Issues

**Q: SDK not capturing logs/metrics**
- Ensure `overcast.init()` is called before logging
- Check that the database file is writable
- Verify the API key is correct

**Q: Dashboard not accessible**
- Check if the port is available and not blocked by firewall
- Ensure the dashboard is started with correct host/port settings
- Try accessing via `http://localhost:5000` instead of `0.0.0.0`

**Q: High memory usage**
- Check the `batch_size` configuration (default: 100)
- Ensure old data is being cleaned up (automatic after 30 days)
- Consider reducing log verbosity for high-volume applications

**Q: Performance impact**
- The SDK uses background processing to minimize impact
- Adjust `polling_interval` to reduce CPU usage if needed
- Use appropriate log levels (avoid DEBUG in production)

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
from sdk.core.config import OvercastConfig

config = OvercastConfig(
    api_key="your-key",
    customer_name="Your Startup",
    log_level="DEBUG"  # Enable debug logging
)
```

## Support

For questions or issues:

1. Check this README and the example code
2. Review the troubleshooting section
3. Check the logs in your database or console output
4. Contact support with specific error messages and configuration details

## License

This SDK is part of the Overcast platform. Please refer to your service agreement for license terms.

---

**Ready to get started?** Check out `example_usage.py` for a complete working example! 