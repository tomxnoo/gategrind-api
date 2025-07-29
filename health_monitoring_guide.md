# Health Monitoring Implementation Guide

## 🚀 Immediate Health Monitoring Setup

SuperClaude has implemented comprehensive health endpoints that are **ready to use right now**! Here's how to start monitoring your system immediately.

## 📍 Available Health Endpoints

Your RoS-TRAE application now has these monitoring endpoints available at `/api/v2/health/`:

### 1. **Basic Health Check**
```
GET /api/v2/health/
```
**Purpose**: Quick service availability check  
**Use Case**: Load balancer health checks, basic monitoring  
**Response Time**: ~5ms

### 2. **Detailed Health Check**
```
GET /api/v2/health/detailed
```
**Purpose**: Comprehensive system health with all components  
**Includes**:
- Database connectivity & response time
- Redis/Cache health & performance metrics
- System resources (CPU, Memory, Disk)
- Overall service status

### 3. **Database Health**
```
GET /api/v2/health/database
```
**Purpose**: Dedicated database monitoring  
**Includes**:
- Connection test
- Query performance
- Record counts
- Response times

### 4. **Cache Health**
```
GET /api/v2/health/cache
```
**Purpose**: Redis/Cache system monitoring  
**Includes**:
- Cache operations test (set/get/delete)
- Hit/miss rates
- Performance metrics
- Fallback status

### 5. **System Metrics**
```
GET /api/v2/health/metrics
```
**Purpose**: Application and system performance metrics  
**Includes**:
- Cache statistics
- System resource usage
- API version info
- Uptime tracking

### 6. **Kubernetes Probes**
```
GET /api/v2/health/readiness  # Ready to handle requests
GET /api/v2/health/liveness   # Service is alive
```
**Purpose**: Container orchestration health checks

## 🛠️ How to Start Using Immediately

### Step 1: Start Your Application
```bash
# If not already running
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Test Basic Health Check
```bash
# Using curl
curl http://localhost:8000/api/v2/health/

# Using PowerShell (Windows)
Invoke-RestMethod -Uri "http://localhost:8000/api/v2/health/" -Method GET
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "2.0.0",
    "environment": "development"
  },
  "message": "Service is healthy"
}
```

### Step 3: Check Detailed Health
```bash
curl http://localhost:8000/api/v2/health/detailed
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "overall_status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "2.0.0",
    "environment": "development",
    "checks": {
      "database": {
        "status": "healthy",
        "response_time_ms": 12.5,
        "details": "Database connection successful"
      },
      "cache": {
        "status": "healthy",
        "response_time_ms": 8.2,
        "redis_available": true,
        "hit_rate": 0.85,
        "details": "Cache operations successful"
      },
      "system": {
        "status": "healthy",
        "cpu_percent": 15.2,
        "memory_percent": 45.8,
        "disk_percent": 32.1,
        "details": "System metrics collected"
      }
    },
    "total_response_time_ms": 25.7
  }
}
```

## 📊 Setting Up Monitoring Dashboard

### Option 1: Simple Browser Monitoring
Create a simple HTML dashboard to monitor your endpoints:

```html
<!DOCTYPE html>
<html>
<head>
    <title>RoS-TRAE Health Dashboard</title>
    <meta http-equiv="refresh" content="30">
</head>
<body>
    <h1>RoS-TRAE Health Status</h1>
    <div id="health-status">
        <!-- Auto-refreshes every 30 seconds -->
        <iframe src="http://localhost:8000/api/v2/health/detailed" width="100%" height="400"></iframe>
    </div>
</body>
</html>
```

### Option 2: PowerShell Monitoring Script
```powershell
# health_monitor.ps1
while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] Checking health..." -ForegroundColor Green
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v2/health/detailed" -Method GET
        $status = $response.data.overall_status
        $dbTime = $response.data.checks.database.response_time_ms
        $cacheTime = $response.data.checks.cache.response_time_ms
        
        Write-Host "Status: $status | DB: ${dbTime}ms | Cache: ${cacheTime}ms" -ForegroundColor Cyan
    }
    catch {
        Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 30
}
```

### Option 3: Python Monitoring Script
```python
# health_monitor.py
import requests
import time
import json
from datetime import datetime

def check_health():
    try:
        response = requests.get("http://localhost:8000/api/v2/health/detailed")
        data = response.json()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = data['data']['overall_status']
        
        print(f"[{timestamp}] Status: {status}")
        
        # Check individual components
        checks = data['data']['checks']
        for component, details in checks.items():
            comp_status = details['status']
            response_time = details.get('response_time_ms', 'N/A')
            print(f"  {component}: {comp_status} ({response_time}ms)")
            
    except Exception as e:
        print(f"Health check failed: {e}")

if __name__ == "__main__":
    while True:
        check_health()
        print("-" * 50)
        time.sleep(30)
```

## 🔔 Setting Up Alerts

### Basic Alert Script (PowerShell)
```powershell
# alert_monitor.ps1
$webhookUrl = "YOUR_SLACK_WEBHOOK_URL"  # Optional: Slack notifications

while ($true) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v2/health/detailed"
        $status = $response.data.overall_status
        
        if ($status -ne "healthy") {
            $message = "🚨 RoS-TRAE Health Alert: Status is $status"
            Write-Host $message -ForegroundColor Red
            
            # Optional: Send to Slack
            if ($webhookUrl) {
                $payload = @{ text = $message } | ConvertTo-Json
                Invoke-RestMethod -Uri $webhookUrl -Method POST -Body $payload -ContentType "application/json"
            }
        }
    }
    catch {
        Write-Host "🚨 Health check failed completely!" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 60
}
```

## 📈 Monitoring Best Practices

### 1. **Regular Health Checks**
- Basic health: Every 30 seconds
- Detailed health: Every 2-5 minutes
- Metrics collection: Every 5-10 minutes

### 2. **Alert Thresholds**
- Database response time > 100ms: Warning
- Database response time > 500ms: Critical
- Cache hit rate < 70%: Warning
- System memory > 85%: Warning
- System memory > 95%: Critical

### 3. **Log Health Metrics**
```python
# Add to your monitoring script
import logging

logging.basicConfig(
    filename='health_monitoring.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log health status
logging.info(f"Health Status: {status}, DB: {db_time}ms, Cache: {cache_time}ms")
```

## 🎯 Next Steps

1. **Start with basic monitoring** using the provided scripts
2. **Set up automated alerts** for critical issues
3. **Integrate with monitoring tools** like Grafana, Prometheus, or DataDog
4. **Create dashboards** for visual monitoring
5. **Set up log aggregation** for historical analysis

## 🔧 Troubleshooting

### Common Issues:
- **404 errors**: Ensure your app is running and health router is included
- **Database unhealthy**: Check database connection and credentials
- **Cache degraded**: Redis might be down, but app continues with memory fallback
- **High response times**: Check system resources and database performance

Your health monitoring system is **production-ready** and can be used immediately! 🚀