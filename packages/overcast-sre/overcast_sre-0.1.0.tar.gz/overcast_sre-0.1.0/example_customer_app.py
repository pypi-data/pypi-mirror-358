#!/usr/bin/env python3
"""
EXAMPLE CUSTOMER APPLICATION
This shows how a customer would use the Overcast SDK in SaaS mode
"""

import time
import random
import sys
import os
from datetime import datetime

# Add SDK to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import __init__ as overcast

class CustomerEcommerceApp:
    """Example customer e-commerce application"""
    
    def __init__(self, customer_name, api_key):
        self.customer_name = customer_name
        self.api_key = api_key
        self.running = False
        self.order_count = 0
        self.payment_issues = 0
        
    def start(self):
        """Start the customer application"""
        print(f"🛍️  Starting {self.customer_name} E-commerce Application...")
        print("=" * 60)
        
        # Initialize Overcast SDK in SaaS mode (default)
        overcast.init(
            api_key=self.api_key,
            customer_name=self.customer_name,
            server_url="http://localhost:8001"  # Points to your centralized server
        )
        
        # Log application startup
        overcast.log(f"{self.customer_name} application started successfully", 
                    level="INFO", service="web-app")
        
        # Record startup metric
        overcast.metric("app_startup_time", 1.8, 
                       tags={"version": "2.1.0", "environment": "production"}, 
                       service="web-app")
        
        self.running = True
        print(f"✅ {self.customer_name} application started successfully!")
        print("📡 Data is being sent to centralized Overcast server")
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
                print(f"📅 {self.customer_name} - Cycle {cycle} - {datetime.now().strftime('%H:%M:%S')}")
                
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
            print(f"\n🛑 Stopping {self.customer_name} application...")
            self.shutdown()
    
    def process_orders(self):
        """Process customer orders"""
        # Simulate order processing
        orders_this_cycle = random.randint(1, 3)
        
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
            
            # Simulate occasional failures
            if random.random() < 0.2:
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
        
        # Simulate occasional critical payment failures
        if random.random() < 0.15:
            self.payment_issues += 1
            error_msg = f"Payment {payment_id} failed - external gateway timeout"
            
            overcast.log(error_msg, level="CRITICAL", service="payment-service")
            overcast.log("Payment gateway returning 503 errors", 
                        level="ERROR", service="payment-service")
            
            # Send critical alert
            overcast.alert(f"CRITICAL: Payment system failure - {error_msg}", 
                          severity="critical", service="payment-service")
            
            # Record failure metrics
            overcast.metric("payment_failure_rate", self.payment_issues / max(self.order_count, 1),
                           tags={"gateway": "stripe"}, service="payment-service")
            return
        
        # Successful payment
        overcast.metric("payment_processing_time", payment_time,
                       tags={"payment_id": payment_id}, service="payment-service")
        overcast.log(f"Payment {payment_id} processed successfully", 
                    level="INFO", service="payment-service")
    
    def check_inventory(self):
        """Check inventory levels"""
        # Simulate inventory check
        items_checked = random.randint(5, 20)
        
        for _ in range(items_checked):
            stock_level = random.randint(0, 100)
            
            # Record inventory metrics
            overcast.metric("inventory_level", stock_level,
                           tags={"item_id": f"ITEM-{random.randint(1, 500)}"}, 
                           service="inventory-service")
            
            # Simulate low inventory alerts
            if stock_level < 5:
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
        
        # Simulate occasional database issues
        if random.random() < 0.1:
            overcast.log("Database connection pool exhausted", 
                        level="ERROR", service="database")
            overcast.alert("Database performance critical - connection pool exhausted", 
                          severity="critical", service="database")
            
            # Record database metrics showing issues
            overcast.metric("db_connection_pool_usage", 1.0,
                           tags={"max_connections": "500"}, service="database")
    
    def shutdown(self):
        """Shutdown the application"""
        self.running = False
        
        overcast.log(f"{self.customer_name} application shutting down", level="INFO", service="web-app")
        overcast.shutdown()
        
        print(f"✅ {self.customer_name} application stopped successfully")

def main():
    """Main function"""
    print("🎯 OVERCAST SDK - CUSTOMER EXAMPLE")
    print("=" * 60)
    print("This simulates how customers use the Overcast SDK in SaaS mode")
    print()
    
    # Ask which customer to simulate
    print("Available customers:")
    print("1. 🏪 Demo Store Inc (demo-customer-123)")
    print("2. 🛒 ShopFast LLC (shopfast-456)")
    print("3. 🎁 GiftBox Co (giftbox-789)")
    
    choice = input("\nSelect customer (1-3): ").strip()
    
    if choice == "1":
        customer_name = "Demo Store Inc"
        api_key = "demo-customer-123"
    elif choice == "2":
        customer_name = "ShopFast LLC"
        api_key = "shopfast-456"
    elif choice == "3":
        customer_name = "GiftBox Co"
        api_key = "giftbox-789"
    else:
        customer_name = "Demo Store Inc"
        api_key = "demo-customer-123"
    
    print(f"\n🚀 Starting {customer_name}...")
    print("📡 Make sure you have started:")
    print("   1. python start_api_server.py  (in terminal 1)")
    print("   2. python start_multi_tenant_dashboard.py  (in terminal 2)")
    print()
    
    # Start the customer app
    app = CustomerEcommerceApp(customer_name, api_key)
    app.start()

if __name__ == '__main__':
    main() 