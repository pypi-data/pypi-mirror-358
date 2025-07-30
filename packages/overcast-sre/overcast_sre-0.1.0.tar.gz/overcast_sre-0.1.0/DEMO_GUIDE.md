# 🎯 OVERCAST PRODUCT DEMO GUIDE
**Complete walkthrough for product demos with customers**

---

## 📋 DEMO OVERVIEW
This guide walks you through a complete Overcast demo showing:
1. **Customer Setup** - How to onboard a new customer
2. **SDK Integration** - How customers add monitoring to their apps  
3. **Incident Detection** - How Overcast catches failures automatically
4. **AI-Powered RCA** - How our AI provides root cause analysis and remediation

**Total Demo Time:** ~15 minutes

---

## 🚀 STEP 1: CUSTOMER SETUP

### What you'll tell the customer:
*"Let me show you how quick it is to get started with Overcast. First, we'll set up your account and get your monitoring key."*

### Steps to follow:

**1.1** Open a terminal/command prompt on your demo machine

**1.2** Navigate to the SDK folder:
```bash
cd sdk
```

**1.3** Tell the customer: *"Every customer gets a unique API key for security. This is how we identify your data."*

**1.4** Show them the customer is already configured in our demo:
- API Key: `demo-customer-123`  
- Company Name: `Demo E-commerce Store`

### What this demonstrates:
✅ **Simple onboarding** - No complex setup required  
✅ **Secure** - Each customer has their own isolated data  
✅ **Ready in seconds** - Not hours or days like other tools

---

## 🔧 STEP 2: SDK INTEGRATION

### What you'll tell the customer:
*"Now I'll show you how your developers would add Overcast monitoring to your application. It's just 3 lines of code."*

### Steps to follow:

**2.1** Open the demo app file to show the integration:
```bash
# Show them the file (don't run yet)
cat demo_app.py
```

**2.2** Point out the key integration parts:
```python
# 1. Import the SDK
import __init__ as overcast

# 2. Initialize monitoring (1 line)
overcast.init(
    api_key="demo-customer-123",
    customer_name="Demo E-commerce Store"
)

# 3. Add monitoring to your code (1 line each)
overcast.log("Order processed", level="INFO", service="orders")
overcast.metric("response_time", 1.2, service="api")
overcast.alert("Payment failed", severity="high", service="payments")
```

**2.3** Explain the business context:
*"This is a mock e-commerce application - just like what your company might have. It processes orders, handles payments, manages inventory, and tracks analytics."*

### What this demonstrates:
✅ **Easy integration** - 3 lines of code, not weeks of setup  
✅ **Non-intrusive** - Doesn't change existing business logic  
✅ **Comprehensive** - Logs, metrics, and alerts in one place

---

## 📊 STEP 3: START THE MONITORING DASHBOARD

### What you'll tell the customer:
*"Before we run your application, let's start the monitoring dashboard so you can see everything in real-time."*

### Steps to follow:

**3.1** Start the dashboard server:
```bash
python server.py
```

**3.2** Wait for this message:
```
🌐 Starting Overcast dashboard on http://0.0.0.0:5000
🤖 Background processing agent started
✅ Dashboard server started successfully!
```

**3.3** Open your web browser and go to: `http://localhost:5000`

**3.4** Show the customer the empty dashboard:
*"Right now it's empty because your application isn't running yet. Let's change that."*

### What this demonstrates:
✅ **Real-time visibility** - See everything as it happens  
✅ **Professional interface** - Clean, executive-friendly dashboard  
✅ **Always-on monitoring** - Background agent processes everything automatically

---

## 🛍️ STEP 4: RUN THE APPLICATION (NORMAL MODE)

### What you'll tell the customer:
*"Let's start with normal operations to show you how Overcast monitors your healthy application."*

### Steps to follow:

**4.1** Open a new terminal/command prompt (keep the dashboard running)

**4.2** Navigate to SDK folder:
```bash
cd sdk
```

**4.3** Start the demo application:
```bash
python demo_app.py
```

**4.4** When prompted, select: `1` (Normal operations)

**4.5** Let it run for 2-3 cycles, then show the customer the dashboard:
- Refresh the browser at `http://localhost:5000`
- Point out the **Services** appearing (order-service, payment-service, etc.)
- Show the **Metrics** being collected
- Show the **Recent Logs** appearing

**4.6** Stop the app with `Ctrl+C`

### What this demonstrates:
✅ **Automatic discovery** - Services appear automatically  
✅ **Rich data collection** - Logs, metrics, business KPIs  
✅ **Zero configuration** - Works out of the box

---

## 🚨 STEP 5: TRIGGER FAILURES & INCIDENTS

### What you'll tell the customer:
*"Now let me show you the real power of Overcast - what happens when things go wrong in production."*

### Steps to follow:

**5.1** Restart the demo application:
```bash
python demo_app.py
```

**5.2** This time select: `2` (Failure simulation)

**5.3** You'll see this message:
```
🔴 FAILURE MODE ENABLED - Incidents will be triggered!
```

**5.4** Let the application run and watch for failures:
- You'll see **RED** error messages in the terminal
- Critical failures like: *"CRITICAL: Payment system failure"*
- Database issues: *"Database connection pool exhausted"*

**5.5** Switch to the dashboard and refresh:
- Point out the **Incidents** section at the top
- Show the **High severity scores** (red numbers like 9.0/10)
- Point to **Recent Incidents** showing critical failures

### What this demonstrates:
✅ **Automatic incident detection** - No manual configuration needed  
✅ **Intelligent prioritization** - Critical issues scored higher  
✅ **Real business impact** - Payment failures, not just server metrics

---

## 🤖 STEP 6: AI ROOT CAUSE ANALYSIS

### What you'll tell the customer:
*"Here's where Overcast's AI really shines - it automatically analyzes every incident and provides actionable insights."*

### Steps to follow:

**6.1** In the dashboard, look for the **Recent Incidents** section

**6.2** Click on any incident row to **expand** it (look for arrows or plus signs)

**6.3** Point out the AI analysis sections:

**🎯 Root Cause Analysis:**
- *"Payment gateway connection timeout due to network latency issues"*
- *"Database connection pool exhausted due to query bottleneck"*

**💥 Impact Assessment:**  
- *"Critical business impact: 40% of customer transactions failing"*
- *"Revenue loss estimated at $2,400/hour based on transaction volume"*

**🛠️ Resolution Steps:**
1. *"Restart payment gateway connection pool"*
2. *"Scale database read replicas"*  
3. *"Contact Stripe support for gateway status"*

**🛡️ Prevention Measures:**
1. *"Implement circuit breaker pattern for payment calls"*
2. *"Add database connection monitoring alerts"*
3. *"Set up automated failover for payment gateway"*

**6.4** Show the **Timeline** of events leading to the incident

### What this demonstrates:
✅ **AI-powered insights** - Not just alerts, but actual solutions  
✅ **Business context** - Revenue impact, not just technical metrics  
✅ **Actionable guidance** - Your team knows exactly what to do  
✅ **Learning system** - Gets smarter with each incident

---

## 🎉 STEP 7: WRAP UP THE DEMO

### What you'll tell the customer:
*"In just 10 minutes, we've shown you how Overcast transforms your incident response from reactive firefighting to proactive problem-solving."*

### Key points to emphasize:

**Before Overcast:**
- ❌ Incidents discovered by customers calling
- ❌ Hours spent figuring out what went wrong  
- ❌ Guessing at solutions, hoping they work
- ❌ Same problems keep happening

**After Overcast:**
- ✅ Incidents detected automatically in seconds
- ✅ AI provides root cause analysis immediately
- ✅ Clear resolution steps prevent guessing
- ✅ Prevention measures stop repeat incidents

### Next Steps:
1. **"Would you like to see this running on your actual application?"**
2. **"I can have our team set up a pilot with your dev team this week"**  
3. **"What questions do you have about getting started?"**

---

## 🔧 TROUBLESHOOTING

### If the dashboard doesn't load:
- Make sure `python server.py` is running
- Try `http://127.0.0.1:5000` instead of localhost
- Check that port 5000 isn't blocked

### If no incidents appear:
- Make sure you selected option `2` (Failure simulation)
- Let the app run for at least 3-4 cycles
- Refresh the dashboard browser page

### If AI analysis is missing:
- Make sure OpenAI API key is configured
- Wait 30 seconds after incidents appear
- Check for any error messages in the server terminal

---

## 📱 DEMO SCRIPT (OPTIONAL)

*Use this script if you want more structure during customer calls:*

**Opening (2 min):**
*"I'm going to show you how Overcast helps companies like yours prevent outages and reduce downtime by 85%. This is our complete incident response platform in action."*

**Setup Demo (3 min):**
*"First, let's see how quick the setup is..." [Follow Steps 1-3]*

**Normal Operations (3 min):**
*"Here's your application running normally..." [Follow Step 4]*

**Incident Response (5 min):**  
*"Now when things go wrong..." [Follow Steps 5-6]*

**Close (2 min):**
*"Questions? Next steps?" [Follow Step 7]*

---

**🎯 That's it! You're ready to demo Overcast like a pro.** 