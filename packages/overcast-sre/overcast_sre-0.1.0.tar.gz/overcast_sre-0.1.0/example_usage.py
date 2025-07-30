#!/usr/bin/env python3
"""
Example usage of Overcast SDK - How startups can integrate monitoring
"""

import time
import random
import sys
import os

# Add current directory to path so we can import the SDK
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import __init__ as overcast

def main():
    """Example of how to use Overcast SDK in your application"""
    
    # Initialize Overcast SDK
    overcast.init(
        api_key="your-api-key-here",
        customer_name="Your Startup Name"
    )
    
    print("🚀 Starting example application with Overcast monitoring...")
    
    # Example business logic with monitoring
    try:
        # Log application startup
        overcast.log("Application started successfully", level="INFO", service="web-app")
        
        # Record startup metric
        overcast.metric("app_startup_time", 1.2, tags={"version": "1.0.0"}, service="web-app")
        
        # Simulate some business operations
        for i in range(10):
            simulate_business_operation(i)
            time.sleep(2)
    
    except Exception as e:
        # Log critical error
        overcast.log(f"Application crashed: {e}", level="CRITICAL", service="web-app")
        overcast.alert(f"Application crash: {e}", severity="critical", service="web-app")
    
    finally:
        # Shutdown Overcast
        overcast.shutdown()

def simulate_business_operation(iteration: int):
    """Simulate a business operation with monitoring"""
    
    operation_start = time.time()
    
    try:
        # Log operation start
        overcast.log(f"Starting operation {iteration}", level="INFO", service="business-logic")
        
        # Simulate some work
        work_time = random.uniform(0.1, 2.0)
        time.sleep(work_time)
        
        # Record operation metrics
        overcast.metric("operation_duration", work_time, 
                       tags={"operation_id": str(iteration)}, 
                       service="business-logic")
        
        # Simulate occasional errors
        if random.random() < 0.2:  # 20% chance of error
            raise Exception(f"Random error in operation {iteration}")
        
        # Log successful completion
        overcast.log(f"Operation {iteration} completed successfully", 
                    level="INFO", service="business-logic")
        
        # Record success metric
        overcast.metric("operation_success", 1, 
                       tags={"operation_id": str(iteration)}, 
                       service="business-logic")
    
    except Exception as e:
        # Log error
        overcast.log(f"Operation {iteration} failed: {e}", 
                    level="ERROR", service="business-logic")
        
        # Record failure metric
        overcast.metric("operation_failure", 1, 
                       tags={"operation_id": str(iteration), "error": str(e)}, 
                       service="business-logic")
        
        # Send alert for critical errors
        if "critical" in str(e).lower():
            overcast.alert(f"Critical error in operation {iteration}: {e}", 
                          severity="high", service="business-logic")

def example_web_endpoint():
    """Example of monitoring a web endpoint"""
    
    endpoint_start = time.time()
    
    try:
        # Log request
        overcast.log("Processing web request", level="INFO", service="web-api")
        
        # Simulate processing
        processing_time = random.uniform(0.1, 1.0)
        time.sleep(processing_time)
        
        # Record response time
        overcast.metric("response_time", processing_time, 
                       tags={"endpoint": "/api/data"}, 
                       service="web-api")
        
        # Simulate database query
        db_start = time.time()
        time.sleep(random.uniform(0.05, 0.3))
        db_time = time.time() - db_start
        
        overcast.metric("db_query_time", db_time, 
                       tags={"query": "select_user_data"}, 
                       service="database")
        
        # Log successful response
        overcast.log("Request processed successfully", level="INFO", service="web-api")
        
        return {"status": "success", "data": "example_data"}
    
    except Exception as e:
        # Log error
        overcast.log(f"Request failed: {e}", level="ERROR", service="web-api")
        
        # Send alert for API errors
        overcast.alert(f"API endpoint error: {e}", severity="medium", service="web-api")
        
        return {"status": "error", "message": str(e)}

def example_background_job():
    """Example of monitoring a background job"""
    
    job_id = random.randint(1000, 9999)
    
    try:
        overcast.log(f"Starting background job {job_id}", level="INFO", service="background-worker")
        
        # Simulate job processing
        for step in range(5):
            overcast.log(f"Job {job_id} step {step}", level="DEBUG", service="background-worker")
            
            # Record progress
            overcast.metric("job_progress", step / 5 * 100, 
                           tags={"job_id": str(job_id)}, 
                           service="background-worker")
            
            time.sleep(0.5)
        
        # Job completed
        overcast.log(f"Background job {job_id} completed", level="INFO", service="background-worker")
        overcast.metric("job_completion", 1, 
                       tags={"job_id": str(job_id)}, 
                       service="background-worker")
    
    except Exception as e:
        overcast.log(f"Background job {job_id} failed: {e}", 
                    level="ERROR", service="background-worker")
        overcast.alert(f"Background job failure: {e}", 
                      severity="medium", service="background-worker")

# Alternative: Using context manager
def example_with_context_manager():
    """Example using context manager for automatic cleanup"""
    
    with overcast.OvercastContext(
        api_key="your-api-key-here",
        customer_name="Your Startup Name"
    ):
        overcast.log("Using context manager", level="INFO", service="example")
        overcast.metric("context_usage", 1, service="example")
        
        # Do your business logic here
        time.sleep(1)
        
        overcast.log("Context manager example completed", level="INFO", service="example")
    
    # Overcast automatically shuts down when exiting the context

if __name__ == '__main__':
    print("""
    This is an example of how to integrate Overcast SDK into your application.
    
    To run this example:
    1. Replace 'your-api-key-here' with your actual API key
    2. Install dependencies: pip install -r requirements.txt
    3. Run: python example_usage.py
    
    For monitoring web applications, you would integrate similar logging and 
    metrics calls into your actual business logic, web routes, background jobs, etc.
    
    The SDK will automatically:
    - Store logs and metrics in a local SQLite database
    - Start a background agent for incident correlation
    - Provide a web dashboard for monitoring
    - Send alerts for high-severity incidents
    """)
    
    choice = input("Run example? (y/n): ")
    if choice.lower() == 'y':
        main()
    else:
        print("Example not run. Check the code above for integration patterns.") 