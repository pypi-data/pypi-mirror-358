#!/usr/bin/env python3
"""
DEMO APP - Simple E-commerce Application for Overcast Demo
This simulates a customer's production application with controlled failures
"""

import time
import random
import sys
import os
from datetime import datetime

# Add SDK to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import __init__ as overcast

# Demo configuration
DEMO_MODE = True
FAILURE_ENABLED = False  # Set to True to trigger failures

class EcommerceApp:
    """Simple e-commerce application with monitoring"""
    
    def __init__(self):
        self.running = False
        self.order_count = 0
        self.payment_issues = 0
        
    def start(self):
        """Start the e-commerce application"""
        print("🛍️  Starting E-commerce Application...")
        print("=" * 50)
        
        # Initialize Overcast monitoring with correct database path
        overcast.init(
            api_key="demo-customer-123",
            customer_name="Demo E-commerce Store",
            db_path="sdk/overcast_data.db"  # Use the same database as the dashboard
        )
        
        # Log application startup
        overcast.log("E-commerce application started successfully", 
                    level="INFO", service="web-app")
        
        # Record startup metric
        overcast.metric("app_startup_time", 1.8, 
                       tags={"version": "2.1.0", "environment": "production"}, 
                       service="web-app")
        
        self.running = True
        print("✅ Application started successfully!")
        print("📊 Monitoring enabled with Overcast SDK")
        print()
        
        # Run the main business loop
        self.run_business_operations()
    
    def run_business_operations(self):
        """Run the main business operations"""
        print("🔄 Running business operations...")
        print("   (Press Ctrl+C to stop)")
        print()
        
        try:
            cycle = 0
            while self.running:
                cycle += 1
                print(f"📅 Cycle {cycle} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Process orders
                self.process_orders()
                
                # Handle payments
                self.process_payments()
                
                # Check inventory
                self.check_inventory()
                
                # Update analytics
                self.update_analytics()
                
                print(f"   ✅ Cycle {cycle} completed")
                print()
                
                time.sleep(5)  # Wait 5 seconds between cycles
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping application...")
            self.shutdown()
    
    def process_orders(self):
        """Process customer orders"""
        # Simulate order processing
        orders_this_cycle = random.randint(1, 5)
        
        for i in range(orders_this_cycle):
            self.order_count += 1
            order_id = f"ORD-{self.order_count:04d}"
            
            # Log order processing
            overcast.log(f"Processing order {order_id}", 
                        level="INFO", service="order-service")
            
            # Simulate processing time
            processing_time = random.uniform(0.5, 2.0)
            time.sleep(processing_time)
            
            # Record order metrics
            overcast.metric("order_processing_time", processing_time,
                           tags={"order_id": order_id}, service="order-service")
            
            # CONTROLLED FAILURE POINT 1: Order Processing
            if FAILURE_ENABLED and random.random() < 0.3:
                error_msg = f"Order {order_id} failed - inventory lookup timeout"
                overcast.log(error_msg, level="ERROR", service="order-service")
                overcast.alert(f"Order processing failure: {error_msg}", 
                              severity="high", service="order-service")
                continue
            
            overcast.log(f"Order {order_id} processed successfully", 
                        level="INFO", service="order-service")
    
    def process_payments(self):
        """Process payments"""
        # Simulate payment processing
        payment_id = f"PAY-{random.randint(1000, 9999)}"
        
        overcast.log(f"Processing payment {payment_id}", 
                    level="INFO", service="payment-service")
        
        # Simulate payment processing time
        payment_time = random.uniform(1.0, 3.0)
        time.sleep(payment_time)
        
        # CONTROLLED FAILURE POINT 2: Payment Processing (CRITICAL)
        if FAILURE_ENABLED and random.random() < 0.4:
            self.payment_issues += 1
            error_msg = f"Payment {payment_id} failed - external gateway timeout"
            
            overcast.log(error_msg, level="CRITICAL", service="payment-service")
            overcast.log("Payment gateway returning 503 errors", 
                        level="ERROR", service="payment-service")
            overcast.log("Customer payment confirmations not received", 
                        level="CRITICAL", service="payment-service")
            
            # Send critical alert
            overcast.alert(f"CRITICAL: Payment system failure - {error_msg}", 
                          severity="critical", service="payment-service")
            
            # Record failure metrics
            overcast.metric("payment_failure_rate", self.payment_issues / max(self.order_count, 1),
                           tags={"gateway": "stripe"}, service="payment-service")
            overcast.metric("payment_response_time", 30.0,  # Timeout
                           tags={"status": "timeout"}, service="payment-service")
            return
        
        # Successful payment
        overcast.metric("payment_processing_time", payment_time,
                       tags={"payment_id": payment_id}, service="payment-service")
        overcast.log(f"Payment {payment_id} processed successfully", 
                    level="INFO", service="payment-service")
    
    def check_inventory(self):
        """Check inventory levels"""
        # Simulate inventory check
        items_checked = random.randint(10, 50)
        
        for _ in range(items_checked):
            stock_level = random.randint(0, 100)
            
            # Record inventory metrics
            overcast.metric("inventory_level", stock_level,
                           tags={"item_id": f"ITEM-{random.randint(1, 500)}"}, 
                           service="inventory-service")
            
            # CONTROLLED FAILURE POINT 3: Low Inventory
            if FAILURE_ENABLED and stock_level < 5:
                overcast.log(f"Low inventory alert - item has {stock_level} units left", 
                            level="WARN", service="inventory-service")
                
                if stock_level == 0:
                    overcast.alert("Product out of stock - affecting customer orders", 
                                  severity="medium", service="inventory-service")
    
    def update_analytics(self):
        """Update business analytics"""
        # Record business metrics
        overcast.metric("total_orders", self.order_count,
                       tags={"period": "current_session"}, service="analytics")
        
        overcast.metric("active_users", random.randint(50, 200),
                       tags={"period": "current_hour"}, service="analytics")
        
        # CONTROLLED FAILURE POINT 4: Database Issues
        if FAILURE_ENABLED and random.random() < 0.2:
            overcast.log("Database connection pool exhausted", 
                        level="ERROR", service="database")
            overcast.log("Analytics queries timing out after 30 seconds", 
                        level="CRITICAL", service="database")
            overcast.alert("Database performance critical - connection pool exhausted", 
                          severity="critical", service="database")
            
            # Record database metrics showing issues
            overcast.metric("db_connection_pool_usage", 1.0,
                           tags={"max_connections": "500"}, service="database")
            overcast.metric("db_query_time", 35.0,  # Very slow
                           tags={"query_type": "analytics"}, service="database")
    
    def shutdown(self):
        """Shutdown the application"""
        self.running = False
        
        overcast.log("Application shutting down", level="INFO", service="web-app")
        overcast.shutdown()
        
        print("✅ Application stopped successfully")

def main():
    """Main demo function"""
    global FAILURE_ENABLED
    
    print("🎯 OVERCAST DEMO - E-COMMERCE APPLICATION")
    print("=" * 60)
    print("This simulates a customer's production e-commerce application")
    print()
    
    # Ask about failure mode
    print("Demo modes:")
    print("1. 🟢 Normal operations (no failures)")
    print("2. 🔴 Failure simulation (triggers incidents)")
    
    choice = input("\nSelect mode (1 or 2): ").strip()
    
    if choice == "2":
        FAILURE_ENABLED = True
        print("🔴 FAILURE MODE ENABLED - Incidents will be triggered!")
    else:
        FAILURE_ENABLED = False
        print("🟢 NORMAL MODE - Application will run smoothly")
    
    print()
    
    # Start the demo app
    app = EcommerceApp()
    app.start()

if __name__ == '__main__':
    main() 