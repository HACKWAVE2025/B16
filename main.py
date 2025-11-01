# main.py: FastAPI server for Elevatech SmartLift Monitor
# Exposes REST APIs for sensor data, alerts, analytics, and more

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import uvicorn

# Import models
from models import (
    SensorData, StatusResponse, Alert, ElevatorInfo, 
    MaintenanceRecord, TechnicianProfile, ProcurementRequest,
    CostSavings, FleetAnalytics, PredictiveAnalysis,
    SystemHealth, RealTimeMetrics
)

# Import database functions
from db import (
    insert_sensor_data, get_latest_sensor_data, get_all_sensor_data,
    get_sensor_data_by_elevator, insert_alert, get_alerts, resolve_alert,
    insert_elevator_info, get_all_elevators, insert_maintenance_record,
    get_maintenance_history, insert_technician, get_technician,
    get_all_technicians, update_technician_points, insert_procurement_request,
    get_procurement_requests, update_procurement_status, insert_cost_savings,
    get_cost_savings, get_total_savings, get_fleet_summary, get_database_stats
)

# Import ML functions
from ml_model import (
    classify_rope_health, analyze_fleet, get_maintenance_priorities,
    compare_buildings, calculate_roi_report
)

# Initialize FastAPI app
app = FastAPI(
    title="Elevatech SmartLift Monitor API",
    description="Predictive Maintenance System for Elevator Ropes using IoT & ML",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ HEALTH CHECK ============

@app.get("/", tags=["System"])
def root():
    """API root endpoint"""
    return {
        "message": "Elevatech SmartLift Monitor API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", tags=["System"])
def health_check():
    """System health check"""
    try:
        stats = get_database_stats()
        return {
            "status": "healthy",
            "database": "connected",
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


# ============ SENSOR DATA ENDPOINTS ============

@app.post("/sensor-data", tags=["Sensor Data"], response_model=dict)
def create_sensor_data(data: SensorData):
    """
    Submit new sensor reading
    
    This endpoint receives sensor data from IoT devices or simulation
    """
    try:
        success = insert_sensor_data(data)
        if success:
            # Classify the health status
            reading_dict = data.dict()
            classification = classify_rope_health(reading_dict)
            
            # Create alert if Warning or Critical
            if classification['status'] in ['Warning', 'Critical']:
                alert_id = f"ALERT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                alert = Alert(
                    alert_id=alert_id,
                    elevator_id=data.elevator_id,
                    alert_type=classification['status'],
                    message=f"{classification['status']}: {classification['reason'][:100]}",
                    timestamp=datetime.utcnow().isoformat(),
                    resolved=False,
                    triggered_by=classification['triggered_metrics'][0] if classification['triggered_metrics'] else None
                )
                insert_alert(alert)
            
            return {
                "success": True,
                "message": "Sensor data recorded successfully",
                "classification": classification
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to insert sensor data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sensor-data/latest/{elevator_id}", tags=["Sensor Data"])
def get_latest_readings(elevator_id: str, limit: int = Query(10, ge=1, le=100)):
    """Get latest sensor readings for specific elevator"""
    try:
        readings = get_latest_sensor_data(elevator_id, limit)
        return {
            "elevator_id": elevator_id,
            "count": len(readings),
            "readings": readings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sensor-data/all", tags=["Sensor Data"])
def get_all_readings(limit: int = Query(100, ge=1, le=1000)):
    """Get all recent sensor readings across fleet"""
    try:
        readings = get_all_sensor_data(limit)
        return {
            "count": len(readings),
            "readings": readings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sensor-data/elevator/{elevator_id}", tags=["Sensor Data"])
def get_elevator_sensor_data(elevator_id: str):
    """Get all sensor data for a specific elevator"""
    try:
        readings = get_sensor_data_by_elevator(elevator_id)
        return {
            "elevator_id": elevator_id,
            "count": len(readings),
            "readings": readings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ HEALTH STATUS & CLASSIFICATION ============

@app.get("/status/{elevator_id}", tags=["Health Status"], response_model=dict)
def get_elevator_status(elevator_id: str):
    """
    Get current health status for an elevator
    
    Returns classification, risk score, predictions, and cost savings
    """
    try:
        # Get latest reading
        readings = get_latest_sensor_data(elevator_id, 1)
        if not readings:
            raise HTTPException(status_code=404, detail=f"No data found for elevator {elevator_id}")
        
        latest = readings[0]
        
        # Classify health
        result = classify_rope_health(latest)
        
        return {
            "elevator_id": elevator_id,
            "status": result['status'],
            "risk_score": result['risk_score'],
            "confidence": result['confidence'],
            "reason": result['reason'],
            "triggered_metrics": result['triggered_metrics'],
            "remaining_life": result['remaining_life'],
            "cost_savings": result['cost_savings'],
            "timestamp": result['timestamp'],
            "latest_reading": latest
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/fleet/summary", tags=["Health Status"])
def get_fleet_status():
    """Get health status summary for entire fleet"""
    try:
        elevators = get_all_elevators()
        
        fleet_data = []
        for elevator in elevators:
            readings = get_latest_sensor_data(elevator['elevator_id'], 1)
            if readings:
                fleet_data.append(readings[0])
        
        if not fleet_data:
            return {
                "total_elevators": len(elevators),
                "message": "No sensor data available yet"
            }
        
        analysis = analyze_fleet(fleet_data)
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ ALERTS ENDPOINTS ============

@app.post("/alerts", tags=["Alerts"])
def create_alert(alert: Alert):
    """Create a new alert"""
    try:
        success = insert_alert(alert)
        if success:
            return {"success": True, "message": "Alert created successfully", "alert_id": alert.alert_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to create alert")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alerts", tags=["Alerts"])
def get_all_alerts(
    elevator_id: Optional[str] = None,
    resolved: Optional[bool] = None
):
    """Get alerts with optional filters"""
    try:
        alerts = get_alerts(elevator_id, resolved)
        return {
            "count": len(alerts),
            "alerts": alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/alerts/{alert_id}/resolve", tags=["Alerts"])
def resolve_alert_endpoint(alert_id: str, technician_id: str):
    """Mark an alert as resolved"""
    try:
        success = resolve_alert(alert_id, technician_id)
        if success:
            # Award points to technician
            update_technician_points(technician_id, 50)  # 50 points for resolving alert
            
            return {
                "success": True,
                "message": f"Alert {alert_id} resolved by {technician_id}",
                "points_awarded": 50
            }
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ ELEVATOR MANAGEMENT ============

@app.post("/elevators", tags=["Elevators"])
def create_elevator(elevator: ElevatorInfo):
    """Register a new elevator"""
    try:
        success = insert_elevator_info(elevator)
        if success:
            return {"success": True, "message": "Elevator registered successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to register elevator")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/elevators", tags=["Elevators"])
def list_elevators():
    """Get all registered elevators"""
    try:
        elevators = get_all_elevators()
        return {
            "count": len(elevators),
            "elevators": elevators
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/elevators/{elevator_id}", tags=["Elevators"])
def get_elevator_details(elevator_id: str):
    """Get detailed information about an elevator"""
    try:
        elevators = get_all_elevators()
        elevator = next((e for e in elevators if e['elevator_id'] == elevator_id), None)
        
        if not elevator:
            raise HTTPException(status_code=404, detail="Elevator not found")
        
        # Get latest status
        status_data = None
        readings = get_latest_sensor_data(elevator_id, 1)
        if readings:
            result = classify_rope_health(readings[0])
            status_data = {
                "status": result['status'],
                "risk_score": result['risk_score'],
                "remaining_days": result['remaining_life']['estimated_days']
            }
        
        # Get maintenance history
        maintenance = get_maintenance_history(elevator_id)
        
        # Get active alerts
        alerts = get_alerts(elevator_id, resolved=False)
        
        return {
            "elevator_info": elevator,
            "current_status": status_data,
            "active_alerts": len(alerts),
            "maintenance_records": len(maintenance),
            "latest_maintenance": maintenance[0] if maintenance else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ MAINTENANCE ENDPOINTS ============

@app.post("/maintenance", tags=["Maintenance"])
def create_maintenance_record(record: MaintenanceRecord):
    """Record a maintenance activity"""
    try:
        success = insert_maintenance_record(record)
        if success:
            return {"success": True, "message": "Maintenance record created"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create record")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/maintenance/{elevator_id}", tags=["Maintenance"])
def get_elevator_maintenance_history(elevator_id: str):
    """Get maintenance history for an elevator"""
    try:
        history = get_maintenance_history(elevator_id)
        return {
            "elevator_id": elevator_id,
            "count": len(history),
            "records": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/maintenance/priorities/all", tags=["Maintenance"])
def get_all_maintenance_priorities():
    """Get prioritized maintenance list for entire fleet"""
    try:
        elevators = get_all_elevators()
        
        fleet_data = []
        for elevator in elevators:
            readings = get_latest_sensor_data(elevator['elevator_id'], 1)
            if readings:
                fleet_data.append(readings[0])
        
        if not fleet_data:
            return {"message": "No sensor data available"}
        
        priorities = get_maintenance_priorities(fleet_data)
        
        return {
            "count": len(priorities),
            "priorities": priorities
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ TECHNICIAN & GAMIFICATION ============

@app.post("/technicians", tags=["Technicians"])
def create_technician(technician: TechnicianProfile):
    """Register a new technician"""
    try:
        success = insert_technician(technician)
        if success:
            return {"success": True, "message": "Technician registered successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to register technician")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/technicians", tags=["Technicians"])
def list_technicians():
    """Get all technicians ranked by points (leaderboard)"""
    try:
        technicians = get_all_technicians()
        return {
            "count": len(technicians),
            "leaderboard": technicians
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/technicians/{technician_id}", tags=["Technicians"])
def get_technician_profile(technician_id: str):
    """Get technician profile and stats"""
    try:
        technician = get_technician(technician_id)
        if not technician:
            raise HTTPException(status_code=404, detail="Technician not found")
        
        return technician
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/technicians/{technician_id}/points", tags=["Technicians"])
def add_technician_points(technician_id: str, points: int):
    """Add points to a technician's score"""
    try:
        success = update_technician_points(technician_id, points)
        if success:
            technician = get_technician(technician_id)
            return {
                "success": True,
                "message": f"Added {points} points to {technician_id}",
                "new_total": technician['points'] if technician else None
            }
        else:
            raise HTTPException(status_code=404, detail="Technician not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ PROCUREMENT ENDPOINTS ============

@app.post("/procurement", tags=["Procurement"])
def create_procurement_request(request: ProcurementRequest):
    """Create automated procurement request"""
    try:
        success = insert_procurement_request(request)
        if success:
            return {
                "success": True,
                "message": "Procurement request created",
                "request_id": request.request_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create request")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/procurement", tags=["Procurement"])
def list_procurement_requests(
    elevator_id: Optional[str] = None,
    status: Optional[str] = None
):
    """Get procurement requests with optional filters"""
    try:
        requests = get_procurement_requests(elevator_id, status)
        return {
            "count": len(requests),
            "requests": requests
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/procurement/{request_id}/status", tags=["Procurement"])
def update_request_status(request_id: str, new_status: str):
    """Update procurement request status"""
    try:
        valid_statuses = ["Pending", "Approved", "Ordered", "Delivered"]
        if new_status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        success = update_procurement_status(request_id, new_status)
        if success:
            return {
                "success": True,
                "message": f"Request {request_id} updated to {new_status}"
            }
        else:
            raise HTTPException(status_code=404, detail="Request not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ COST SAVINGS & ROI ============

@app.get("/cost-savings/{elevator_id}", tags=["Analytics"])
def get_elevator_cost_savings(elevator_id: str):
    """Get cost savings analysis for specific elevator"""
    try:
        savings = get_cost_savings(elevator_id)
        return {
            "elevator_id": elevator_id,
            "count": len(savings),
            "savings_records": savings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cost-savings/total/all", tags=["Analytics"])
def get_total_cost_savings(period_days: int = Query(30, ge=1, le=365)):
    """Get total cost savings across fleet for a period"""
    try:
        total = get_total_savings(period_days)
        return {
            "period_days": period_days,
            "total_savings": round(total, 2),
            "currency": "INR"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/roi-report", tags=["Analytics"])
def get_roi_report():
    """Get comprehensive ROI report for entire fleet"""
    try:
        elevators = get_all_elevators()
        
        fleet_data = []
        for elevator in elevators:
            readings = get_latest_sensor_data(elevator['elevator_id'], 1)
            if readings:
                fleet_data.append(readings[0])
        
        if not fleet_data:
            return {"message": "No sensor data available for ROI calculation"}
        
        report = calculate_roi_report(fleet_data)
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ FLEET ANALYTICS ============

@app.get("/analytics/fleet", tags=["Analytics"])
def get_fleet_analytics():
    """Get comprehensive fleet analytics"""
    try:
        elevators = get_all_elevators()
        
        fleet_data = []
        for elevator in elevators:
            readings = get_latest_sensor_data(elevator['elevator_id'], 1)
            if readings:
                fleet_data.append(readings[0])
        
        if not fleet_data:
            return {
                "total_elevators": len(elevators),
                "message": "No sensor data available yet"
            }
        
        analysis = analyze_fleet(fleet_data)
        
        # Add additional metrics
        summary = get_fleet_summary()
        
        return {
            **analysis,
            "active_alerts": summary['active_alerts'],
            "resolved_today": summary['resolved_alerts_today'],
            "monthly_savings": summary['total_savings_this_month']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/buildings", tags=["Analytics"])
def get_building_comparison():
    """Compare elevator health across buildings"""
    try:
        elevators = get_all_elevators()
        
        # Group by building
        buildings_data = {}
        for elevator in elevators:
            building = elevator['building_name']
            readings = get_latest_sensor_data(elevator['elevator_id'], 1)
            
            if readings:
                if building not in buildings_data:
                    buildings_data[building] = []
                buildings_data[building].append(readings[0])
        
        if not buildings_data:
            return {"message": "No sensor data available"}
        
        comparison = compare_buildings(buildings_data)
        
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ DASHBOARD ENDPOINTS ============

@app.get("/dashboard/summary", tags=["Dashboard"])
def get_dashboard_summary():
    """Get summary data for main dashboard"""
    try:
        # Fleet summary
        fleet = get_fleet_summary()
        
        # Database stats
        stats = get_database_stats()
        
        # Get status breakdown
        elevators = get_all_elevators()
        status_counts = {"Healthy": 0, "Warning": 0, "Critical": 0}
        
        for elevator in elevators:
            readings = get_latest_sensor_data(elevator['elevator_id'], 1)
            if readings:
                result = classify_rope_health(readings[0])
                status_counts[result['status']] += 1
        
        # Top performing technician
        technicians = get_all_technicians()
        top_tech = technicians[0] if technicians else None
        
        return {
            "total_elevators": fleet['total_elevators'],
            "active_alerts": fleet['active_alerts'],
            "resolved_alerts_today": fleet['resolved_alerts_today'],
            "total_savings_this_month": fleet['total_savings_this_month'],
            "status_breakdown": status_counts,
            "fleet_health_percentage": round(
                (status_counts["Healthy"] / len(elevators) * 100) if elevators else 0, 2
            ),
            "top_technician": top_tech['name'] if top_tech else None,
            "total_sensor_readings": stats['total_sensor_readings'],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/realtime/{elevator_id}", tags=["Dashboard"])
def get_realtime_metrics(elevator_id: str):
    """Get real-time metrics for dashboard widget"""
    try:
        # Get latest reading
        readings = get_latest_sensor_data(elevator_id, 1)
        if not readings:
            raise HTTPException(status_code=404, detail="No data available")
        
        latest = readings[0]
        
        # Classify status
        result = classify_rope_health(latest)
        
        # Get elevator info
        elevators = get_all_elevators()
        elevator_info = next((e for e in elevators if e['elevator_id'] == elevator_id), None)
        
        return {
            "elevator_id": elevator_id,
            "building_name": elevator_info['building_name'] if elevator_info else "Unknown",
            "current_status": result['status'],
            "risk_score": result['risk_score'],
            "live_tension": latest['tension'],
            "live_vibration": latest['vibration'],
            "live_temperature": latest['temperature'],
            "live_wear": latest['wear'],
            "current_load": latest['load_weight'],
            "last_updated": latest['timestamp'],
            "next_inspection_due": elevator_info['last_maintenance'] if elevator_info else "N/A"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/trends/{elevator_id}", tags=["Dashboard"])
def get_trends(elevator_id: str, limit: int = Query(50, ge=10, le=500)):
    """Get historical trends for charts"""
    try:
        readings = get_latest_sensor_data(elevator_id, limit)
        
        if not readings:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Reverse to get chronological order
        readings.reverse()
        
        # Extract trends
        trends = {
            "timestamps": [r['timestamp'] for r in readings],
            "tension": [r['tension'] for r in readings],
            "vibration": [r['vibration'] for r in readings],
            "wear": [r['wear'] for r in readings],
            "temperature": [r['temperature'] for r in readings],
            "corrosion": [r['corrosion_level'] for r in readings]
        }
        
        return {
            "elevator_id": elevator_id,
            "data_points": len(readings),
            "trends": trends
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ REPORTS ENDPOINTS ============

@app.get("/reports/elevator/{elevator_id}", tags=["Reports"])
def generate_elevator_report(elevator_id: str):
    """Generate comprehensive report for an elevator"""
    try:
        # Get elevator info
        elevators = get_all_elevators()
        elevator_info = next((e for e in elevators if e['elevator_id'] == elevator_id), None)
        
        if not elevator_info:
            raise HTTPException(status_code=404, detail="Elevator not found")
        
        # Get latest status
        readings = get_latest_sensor_data(elevator_id, 1)
        if not readings:
            raise HTTPException(status_code=404, detail="No sensor data available")
        
        classification = classify_rope_health(readings[0])
        
        # Get maintenance history
        maintenance = get_maintenance_history(elevator_id)
        
        # Get alerts
        all_alerts = get_alerts(elevator_id)
        active_alerts = [a for a in all_alerts if not a['resolved']]
        
        # Get cost savings
        savings = get_cost_savings(elevator_id)
        total_savings = sum(s['total_savings'] for s in savings)
        
        return {
            "elevator_info": elevator_info,
            "current_status": {
                "status": classification['status'],
                "risk_score": classification['risk_score'],
                "confidence": classification['confidence'],
                "reason": classification['reason'],
                "remaining_life": classification['remaining_life']
            },
            "latest_reading": readings[0],
            "maintenance_summary": {
                "total_records": len(maintenance),
                "latest": maintenance[0] if maintenance else None
            },
            "alerts_summary": {
                "total_alerts": len(all_alerts),
                "active_alerts": len(active_alerts),
                "resolved_alerts": len(all_alerts) - len(active_alerts)
            },
            "cost_savings": {
                "total_savings": round(total_savings, 2),
                "roi_percentage": classification['cost_savings']['roi_percentage']
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports/fleet", tags=["Reports"])
def generate_fleet_report():
    """Generate comprehensive fleet report"""
    try:
        # Get all elevators
        elevators = get_all_elevators()
        
        # Collect fleet data
        fleet_data = []
        for elevator in elevators:
            readings = get_latest_sensor_data(elevator['elevator_id'], 1)
            if readings:
                fleet_data.append(readings[0])
        
        if not fleet_data:
            return {"message": "No sensor data available"}
        
        # Analytics
        fleet_analysis = analyze_fleet(fleet_data)
        roi_report = calculate_roi_report(fleet_data)
        priorities = get_maintenance_priorities(fleet_data)
        
        # Alerts summary
        all_alerts = get_alerts()
        active = [a for a in all_alerts if not a['resolved']]
        
        return {
            "fleet_overview": {
                "total_elevators": len(elevators),
                "data_available": len(fleet_data),
                "average_risk_score": fleet_analysis['average_risk_score'],
                "fleet_health_percentage": fleet_analysis['fleet_health_percentage']
            },
            "status_breakdown": fleet_analysis['status_breakdown'],
            "highest_risk_elevators": fleet_analysis['highest_risk_elevators'][:10],
            "maintenance_priorities": priorities[:10],
            "financial_summary": {
                "total_savings": roi_report['total_savings'],
                "total_investment": roi_report['total_investment'],
                "net_benefit": roi_report['net_benefit'],
                "overall_roi": roi_report['overall_roi_percentage']
            },
            "alerts_summary": {
                "total": len(all_alerts),
                "active": len(active),
                "resolved": len(all_alerts) - len(active)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ UTILITIES ============

@app.get("/database/stats", tags=["System"])
def database_statistics():
    """Get database statistics"""
    try:
        stats = get_database_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ RUN SERVER ============

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 Starting Elevatech SmartLift Monitor API Server")
    print("="*70)
    print("\n📚 API Documentation available at:")
    print("   • Swagger UI: http://localhost:8000/docs")
    print("   • ReDoc: http://localhost:8000/redoc")
    print("\n🔌 Endpoints:")
    print("   • Health Check: http://localhost:8000/health")
    print("   • Dashboard: http://localhost:8000/dashboard/summary")
    print("   • Fleet Status: http://localhost:8000/status/fleet/summary")
    print("\n✨ Features:")
    print("   ✅ Sensor Data Collection")
    print("   ✅ Real-time Health Classification")
    print("   ✅ Predictive Maintenance")
    print("   ✅ Cost Savings Analysis")
    print("   ✅ Fleet Analytics")
    print("   ✅ Gamification (Technician Leaderboard)")
    print("   ✅ Automated Procurement")
    print("   ✅ Alerts & Notifications")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

