# 🚀 OVERCAST SDK - QUICK START GUIDE

**Get monitoring and AI-powered incident management in your app in under 5 minutes**

---

## ✨ What is Overcast?

Overcast automatically detects incidents in your application and provides:
- **🤖 AI Root Cause Analysis** - Know exactly what went wrong
- **🛠️ Actionable Resolution Steps** - Fix problems faster  
- **🛡️ Prevention Recommendations** - Stop problems from happening again
- **📊 Real-time Dashboard** - Monitor everything in one place

---

## 🎯 DEMO: Try it yourself

**Step 1:** Open terminal and navigate to the SDK folder
```bash
cd sdk
```

**Step 2:** Start the dashboard
```bash
python start_demo.py
```
*This opens the dashboard in your browser automatically*

**Step 3:** In a NEW terminal, run the demo app
```bash
cd sdk
python demo_app.py
```

**Step 4:** Select option `2` (Failure simulation)

**Step 5:** Watch incidents appear in the dashboard, then click on any incident row to see the AI analysis!

---

## 🔧 INTEGRATION: Add to your app

### 1. Install the SDK
```bash
pip install overcast-sdk  # (Coming soon - use local files for now)
```

### 2. Initialize in your application
```python
import overcast

# Initialize once at app startup
overcast.init(
    api_key="your-api-key-here",
    customer_name="Your Company Name"
)
```

### 3. Add monitoring to your code

**Log important events:**
```python
overcast.log("User logged in", level="INFO", service="auth")
overcast.log("Database connection failed", level="ERROR", service="database")
```

**Track business metrics:**
```python
overcast.metric("response_time", 1.2, service="api")
overcast.metric("orders_processed", 150, service="orders")
```

**Send alerts for critical issues:**
```python
overcast.alert("Payment gateway down", severity="critical", service="payments")
overcast.alert("High memory usage", severity="medium", service="server")
```

### 4. That's it! 🎉
Your incidents will automatically appear in the dashboard with full AI analysis.

---

## 🌐 View Your Dashboard

Once your app is running with Overcast, you can view your dashboard at:
**http://localhost:5000**

The dashboard shows:
- 📊 **Key Metrics** - Total incidents, severity scores, SLA tracking
- 🚨 **Live Incidents** - Real-time incident detection and scoring
- 🤖 **AI Analysis** - Click any incident to see root cause and resolution steps
- 📈 **Charts** - Visual breakdown by service and severity

---

## 🔥 Real-World Example

Here's how you'd monitor a payment processing function:

```python
import overcast

def process_payment(payment_data):
    # Log the start of payment processing
    overcast.log(f"Processing payment {payment_data['id']}", 
                level="INFO", service="payments")
    
    try:
        # Your payment logic here
        result = stripe.charge(payment_data)
        
        # Track successful payment
        overcast.metric("payment_success", 1, 
                       tags={"amount": payment_data['amount']}, 
                       service="payments")
        
        return result
        
    except stripe.CardError as e:
        # Log the error
        overcast.log(f"Payment failed: {e.user_message}", 
                    level="ERROR", service="payments")
        
        # Send alert if many failures
        overcast.alert(f"Payment processing error: {e.user_message}", 
                      severity="high", service="payments")
        
        raise
    
    except Exception as e:
        # Critical system error
        overcast.log(f"Payment system error: {str(e)}", 
                    level="CRITICAL", service="payments")
        
        overcast.alert("Payment system critical failure", 
                      severity="critical", service="payments")
        
        raise
```

**What happens:**
1. All logs and metrics are stored automatically
2. If multiple payment failures occur, Overcast creates an incident
3. The AI analyzes the logs and provides:
   - Root cause (e.g., "Stripe API timeout due to network issues")
   - Business impact (e.g., "40% payment failure rate affecting revenue")
   - Resolution steps (e.g., "Check network connectivity to Stripe")
   - Prevention measures (e.g., "Implement retry logic with exponential backoff")

---

## 📞 Support

**Questions?** Contact us at support@overcast.com

**Want to see this in your actual app?** We can help integrate Overcast with your existing infrastructure in under a day.

---

**🎯 Start monitoring smarter, not harder with Overcast!** 