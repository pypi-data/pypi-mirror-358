# 🏢 MULTI-TENANT OVERCAST SETUP GUIDE

Transform your Overcast SDK into a **multi-tenant SaaS platform** that can serve multiple customers from a centralized infrastructure.

---

## 🎯 WHAT THIS GIVES YOU

✅ **Centralized Infrastructure** - One server, one database, multiple customers  
✅ **Customer Isolation** - Each customer sees only their data  
✅ **Identical Experience** - Same dashboard and features as single-tenant  
✅ **Easy Customer Onboarding** - Just provide API key  
✅ **Scalable Architecture** - Handle hundreds of customers  

---

## 🏗️ ARCHITECTURE OVERVIEW

```
Customer Apps (Multiple)          Your Infrastructure
     ↓                                   ↓
┌─────────────┐                ┌─────────────────┐
│ Customer A  │─────────────→  │   API Server    │
│ overcast.   │  HTTP/JSON     │  (port 8001)    │
│ init(api_key│                │                 │
└─────────────┘                │  ┌───────────┐  │
                               │  │ Database  │  │
┌─────────────┐                │  │ Multi-    │  │
│ Customer B  │─────────────→  │  │ Tenant    │  │
│ overcast.   │  HTTP/JSON     │  └───────────┘  │
│ init(api_key│                └─────────────────┘
└─────────────┘                         ↓
                               ┌─────────────────┐
┌─────────────┐                │   Dashboard     │
│ Customer C  │─────────────→  │  (port 5000)    │
│ overcast.   │  HTTP/JSON     │ Customer        │
│ init(api_key│                │ Selector        │
└─────────────┘                └─────────────────┘
```

---

## 🚀 QUICK START (3 Steps)

### Step 1: Start the API Server
```bash
cd sdk
python start_api_server.py
```
*This starts the centralized server on port 8001*

### Step 2: Start the Dashboard
```bash
cd sdk
python start_multi_tenant_dashboard.py
```
*This starts the dashboard on port 5000*

### Step 3: Test with Example Customer
```bash
cd sdk
python example_customer_app.py
```
*This simulates a customer using your SDK*

**🎉 That's it!** Visit `http://localhost:5000` to see the multi-tenant dashboard.

---

## 👥 CUSTOMER ONBOARDING PROCESS

### For You (SaaS Provider):
1. Generate a unique API key for the customer
2. Give customer the API key and your server URL
3. Customer integrates in 3 lines of code:

### For Customer:
```python
import overcast

overcast.init(
    api_key="customer-api-key-123",      # ← You provide this
    customer_name="Customer Company",
    server_url="https://your-server.com:8001"  # ← Your server
)

# Same API as before - no changes needed!
overcast.log("App started", service="web-app")
overcast.metric("response_time", 0.25, service="api")
overcast.alert("High CPU usage", severity="high", service="server")
```

---

## 🖥️ DASHBOARD FEATURES

The multi-tenant dashboard works **EXACTLY** like the single-tenant version:

✅ **Customer Selector** - Dropdown to switch between customers  
✅ **Same UI** - Identical interface and functionality  
✅ **Same API** - All endpoints work the same  
✅ **Same CLI** - Terminal commands work per customer  
✅ **Same AI Analysis** - Full incident analysis per customer  

### Switching Customers:
- Use the dropdown in the header
- Each customer sees only their data
- All features work identically

---

## 📊 MONITORING YOUR SAAS

### Server Statistics
Visit: `http://localhost:8001/api/stats`
```json
{
  "customers": 3,
  "incidents": 42,
  "logs": 1521,
  "metrics": 3204,
  "active_agents": 3
}
```

### Customer List
Visit: `http://localhost:8001/api/customers`
```json
{
  "customers": [
    {
      "id": "abc123...",
      "name": "Demo Store Inc",
      "api_key": "demo-customer-123",
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

---

## 🔧 PRODUCTION DEPLOYMENT

### Environment Variables
```bash
export OVERCAST_DB_PATH="/var/lib/overcast/central.db"
export OVERCAST_API_HOST="0.0.0.0"
export OVERCAST_API_PORT="8001"
export OVERCAST_DASHBOARD_HOST="0.0.0.0" 
export OVERCAST_DASHBOARD_PORT="5000"
```

### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY sdk/ ./
RUN pip install -r requirements.txt

# Start both services
CMD python start_api_server.py & python start_multi_tenant_dashboard.py
```

### Production Checklist
- [ ] Use HTTPS/TLS for API endpoints
- [ ] Set up proper database backups
- [ ] Configure log rotation
- [ ] Set up monitoring for the API server itself
- [ ] Use a proper database (PostgreSQL/MySQL) instead of SQLite
- [ ] Set up authentication for dashboard access

---

## 🔑 API KEY MANAGEMENT

### Generate API Keys
```python
import uuid
api_key = f"customer-{uuid.uuid4().hex[:16]}"
print(f"API Key: {api_key}")
```

### Validate API Keys
API keys are automatically validated when customers send data. Invalid keys are rejected with 400 error.

### Customer Database
All customers are stored in the `customers` table:
```sql
SELECT id, name, api_key, created_at FROM customers;
```

---

## 📈 SCALING CONSIDERATIONS

### Database
- **SQLite**: Good for < 10 customers
- **PostgreSQL**: Recommended for production
- **MySQL**: Alternative for larger deployments

### Performance
- Each customer gets their own background agent
- HTTP connection pooling for efficiency
- Batch processing for logs and metrics
- Configurable batch sizes and intervals

### Storage
- Default: 30 days data retention
- Automatic cleanup of old data
- Configurable retention periods per customer

---

## 🛠️ DEVELOPMENT & TESTING

### Local Development
```bash
# Terminal 1: API Server
python start_api_server.py

# Terminal 2: Dashboard  
python start_multi_tenant_dashboard.py

# Terminal 3: Test Customer 1
python example_customer_app.py  # Choose option 1

# Terminal 4: Test Customer 2
python example_customer_app.py  # Choose option 2
```

### Testing Multiple Customers
The example app provides 3 different customers:
- Demo Store Inc (`demo-customer-123`)
- ShopFast LLC (`shopfast-456`) 
- GiftBox Co (`giftbox-789`)

### API Testing
```bash
# Test API health
curl http://localhost:8001/health

# Test server stats
curl http://localhost:8001/api/stats

# Test customer list
curl http://localhost:8001/api/customers
```

---

## 🔄 MIGRATION FROM SINGLE-TENANT

### Existing Customers
If you have customers using the old single-tenant SDK:

```python
# OLD (single-tenant)
overcast.init(
    api_key="key",
    customer_name="Company"
    # Data stored locally
)

# NEW (multi-tenant) - Just add server_url
overcast.init(
    api_key="key", 
    customer_name="Company",
    server_url="https://your-server.com:8001"  # ← Add this line
)

# For backwards compatibility, you can still use local mode:
overcast.init(
    api_key="key",
    customer_name="Company", 
    use_local_db=True  # ← Forces local storage
)
```

### Data Migration
To migrate existing customer data to your centralized server:
1. Export data from customer's local database
2. Import into your centralized database under their customer ID
3. Update their SDK configuration

---

## 📞 SUPPORT & TROUBLESHOOTING

### Common Issues

**Q: Customer can't connect to API server**
- Check server URL and port
- Verify API key is correct
- Check firewall settings

**Q: Dashboard shows no customers**
- Ensure API server is running
- Check database path is correct
- Verify customers have sent at least one request

**Q: Incidents not appearing**
- Confirm customer is sending alerts with severity ≥ medium
- Check background agents are running
- Verify database connectivity

### Debug Mode
```python
# Enable debug logging in customer SDK
overcast.init(
    api_key="key",
    customer_name="Company",
    server_url="http://localhost:8001",
    log_level="DEBUG"  # ← Shows HTTP requests
)
```

---

## 🎉 YOU'RE READY!

Your multi-tenant Overcast SaaS platform is now ready to serve multiple customers with:

✅ **Centralized infrastructure**  
✅ **Customer isolation**  
✅ **Identical user experience**  
✅ **Easy customer onboarding**  
✅ **Scalable architecture**  

**Next Steps:**
1. Set up production servers
2. Start onboarding customers
3. Monitor and scale as needed

**Questions?** Check the troubleshooting section or review the example code.

---

*Built with the same Overcast SDK you know and love - now serving multiple customers!* 🌩️ 