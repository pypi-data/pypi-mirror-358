#!/usr/bin/env python3
"""
SIMPLE OVERCAST DEMO LAUNCHER
Direct import approach - no subprocess issues
"""

import os
import sys
import webbrowser
import time
import threading

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.config import OvercastConfig
    from core.database import Database
    from dashboard import OvercastDashboard
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("❌ Make sure you're in the sdk/ directory")
    input("Press Enter to exit...")
    sys.exit(1)

def print_banner():
    """Print welcome banner"""
    print("🎯" + "=" * 60)
    print("  OVERCAST SIMPLE DEMO LAUNCHER")
    print("  Direct dashboard startup (no subprocess)")
    print("=" * 60)
    print()

def start_dashboard_direct():
    """Start dashboard directly by importing"""
    print("🌐 Starting Overcast Dashboard directly...")
    print("   (Browser will open automatically)")
    
    try:
        # Create configuration
        config = OvercastConfig(
            api_key="demo-customer-123",
            customer_name="Demo E-commerce Store",
            dashboard_port=5000,
            dashboard_host="0.0.0.0",
            db_path="overcast_data.db"
        )
        
        # Initialize database
        db = Database(config.db_path)
        db.initialize()
        
        # Ensure customer exists
        customer_id = db.ensure_customer(config.customer_name, config.api_key)
        
        # Create dashboard
        dashboard = OvercastDashboard(config, db, customer_id)
        
        print("✅ Dashboard initialized successfully!")
        print("📊 Dashboard URL: http://localhost:5000")
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open('http://localhost:5000')
                print("🌐 Browser opened automatically")
            except:
                print("⚠️  Please open http://localhost:5000 manually")
        
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        return dashboard
        
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return None

def show_demo_instructions():
    """Show demo instructions"""
    print("\n📋 DEMO INSTRUCTIONS:")
    print("=" * 50)
    print("1. ✅ Dashboard is now running at http://localhost:5000")
    print("2. 🚀 Open a NEW terminal/command prompt")
    print("3. 📁 Navigate to this same directory (sdk/)")
    print("4. ▶️  Run: python demo_app.py")
    print("5. 🎯 Select option 2 (Failure simulation)")
    print("6. ⏱️  Wait for incidents to appear in dashboard")
    print("7. 🔍 Click on incident rows to see AI analysis")
    print()
    print("🎉 You're ready to demo Overcast!")
    print("=" * 50)

def main():
    """Main demo function"""
    print_banner()
    
    # Check requirements
    if not os.path.exists('__init__.py'):
        print("❌ Please run this from the sdk/ directory")
        input("Press Enter to exit...")
        return
    
    if not os.path.exists('demo_app.py'):
        print("❌ demo_app.py not found")
        input("Press Enter to exit...")
        return
    
    print("🔍 All requirements met!")
    
    # Start dashboard
    dashboard = start_dashboard_direct()
    
    if not dashboard:
        input("\nPress Enter to exit...")
        return
    
    # Show instructions
    show_demo_instructions()
    
    # Run dashboard
    try:
        print("\n🔄 Starting dashboard server...")
        print("   Press Ctrl+C to stop")
        dashboard.run(host="0.0.0.0", port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping dashboard...")
        print("✅ Dashboard stopped successfully")
        print("🎯 Demo complete!")
    except Exception as e:
        print(f"\n❌ Dashboard error: {e}")
        input("Press Enter to exit...")

if __name__ == '__main__':
    main() 