# models.py: Data schemas for Elevatech SmartLift Monitor backend
# Enhanced with cost savings, fleet analytics, and gamification models

from pydantic import BaseModel
from typing import Optional, List, Dict

class SensorData(BaseModel):
    """Schema for sensor readings from elevator rope"""
    timestamp: str                      # ISO format timestamp
    elevator_id: str                    # Unique elevator identifier
    tension: float                      # Rope tension (N or kgf)
    vibration: float                    # Vibration level (mm/s)
    wear: float                         # Wear percentage (0-100)
    load_cycles: int                    # Number of load cycles
    temperature: float                  # Rope temperature (°C)
    rope_diameter: float                # Current rope diameter (mm)
    corrosion_level: float              # Corrosion level (0-100 scale)
    elongation: float                   # Rope elongation/stretching (mm or %)
    load_weight: float                  # Current load weight (kg)
    
    class Config:
        schema_extra = {
            "example": {
                "timestamp": "2025-10-31T22:00:00",
                "elevator_id": "ELEV-001",
                "tension": 95.5,
                "vibration": 12.3,
                "wear": 45.2,
                "load_cycles": 1500,
                "temperature": 32.5,
                "rope_diameter": 12.8,
                "corrosion_level": 15.0,
                "elongation": 2.3,
                "load_weight": 450.0
            }
        }


class StatusResponse(BaseModel):
    """Schema for rope health status response"""
    elevator_id: str
    status: str                         # "Healthy", "Warning", or "Critical"
    confidence: Optional[float] = None
    reason: Optional[str] = None        # Explanation for status
    timestamp: str
    critical_metrics: Optional[List[str]] = None  # Which metrics triggered the status
    risk_score: Optional[float] = None  # 0-100 risk score

    class Config:
        schema_extra = {
            "example": {
                "elevator_id": "ELEV-001",
                "status": "Warning",
                "confidence": 0.85,
                "reason": "Wear level exceeds 50% and corrosion detected",
                "timestamp": "2025-10-31T22:00:00",
                "critical_metrics": ["wear", "corrosion_level"],
                "risk_score": 65.5
            }
        }


class Alert(BaseModel):
    """Schema for alert notifications"""
    alert_id: str
    elevator_id: str
    alert_type: str                     # "Warning" or "Critical"
    message: str
    timestamp: str
    resolved: bool = False
    triggered_by: Optional[str] = None  # Which metric triggered the alert
    assigned_to: Optional[str] = None   # Technician assigned

    class Config:
        schema_extra = {
            "example": {
                "alert_id": "ALERT-001",
                "elevator_id": "ELEV-001",
                "alert_type": "Critical",
                "message": "Rope tension below safe threshold",
                "timestamp": "2025-10-31T22:00:00",
                "resolved": False,
                "triggered_by": "tension",
                "assigned_to": "tech_john_doe"
            }
        }


class ElevatorInfo(BaseModel):
    """Schema for elevator metadata"""
    elevator_id: str
    building_name: str
    floor_range: str                    # e.g., "B2 to 15"
    installation_date: str
    last_maintenance: str
    rope_type: str                      # e.g., "Steel Wire Rope"
    location: Optional[str] = None      # Building location
    
    class Config:
        schema_extra = {
            "example": {
                "elevator_id": "ELEV-001",
                "building_name": "Tech Tower A",
                "floor_range": "B2 to 20",
                "installation_date": "2020-05-15",
                "last_maintenance": "2025-09-30",
                "rope_type": "8x19 Steel Wire Rope",
                "location": "Mumbai, Maharashtra"
            }
        }


class MaintenanceRecord(BaseModel):
    """Schema for maintenance history"""
    record_id: str
    elevator_id: str
    maintenance_date: str
    technician_name: str
    action_taken: str
    parts_replaced: Optional[str] = None
    cost: Optional[float] = None
    notes: Optional[str] = None
    downtime_hours: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "record_id": "MAINT-001",
                "elevator_id": "ELEV-001",
                "maintenance_date": "2025-09-30",
                "technician_name": "John Doe",
                "action_taken": "Rope inspection and lubrication",
                "parts_replaced": "None",
                "cost": 5000.0,
                "notes": "All metrics within safe range",
                "downtime_hours": 2.5
            }
        }


class CostSavings(BaseModel):
    """Schema for cost savings analysis"""
    elevator_id: str
    total_savings: float                # Total INR saved
    breakdown: Dict[str, float]         # Detailed cost breakdown
    comparison: Dict[str, float]        # Reactive vs Predictive costs
    roi_percentage: float               # Return on investment
    period: str                         # Time period (e.g., "Monthly", "Yearly")
    timestamp: str
    
    class Config:
        schema_extra = {
            "example": {
                "elevator_id": "ELEV-001",
                "total_savings": 58000.0,
                "breakdown": {
                    "avoided_emergency_replacement": 50000,
                    "avoided_emergency_callout": 15000,
                    "avoided_downtime_cost": 40000,
                    "planned_replacement_cost": -30000,
                    "inspection_cost": -2000
                },
                "comparison": {
                    "reactive_maintenance_cost": 105000,
                    "predictive_maintenance_cost": 32000
                },
                "roi_percentage": 181.25,
                "period": "Per Incident",
                "timestamp": "2025-10-31T22:00:00"
            }
        }


class FleetAnalytics(BaseModel):
    """Schema for fleet-wide analytics"""
    total_elevators: int
    status_breakdown: Dict[str, int]    # Count by status
    average_risk_score: float
    highest_risk_elevators: List[Dict]  # Top at-risk elevators
    fleet_health_percentage: float
    total_estimated_savings: Optional[float] = None
    timestamp: str
    
    class Config:
        schema_extra = {
            "example": {
                "total_elevators": 25,
                "status_breakdown": {
                    "critical": 2,
                    "warning": 8,
                    "healthy": 15
                },
                "average_risk_score": 42.5,
                "highest_risk_elevators": [
                    {
                        "elevator_id": "ELEV-003",
                        "risk_score": 85.2,
                        "status": "Critical"
                    }
                ],
                "fleet_health_percentage": 60.0,
                "total_estimated_savings": 450000.0,
                "timestamp": "2025-10-31T22:00:00"
            }
        }


class PredictiveAnalysis(BaseModel):
    """Schema for predictive maintenance analysis"""
    elevator_id: str
    estimated_days: int                 # Days until replacement needed
    estimated_cycles: int               # Cycles remaining
    confidence: float                   # Prediction confidence
    recommendation: str                 # Maintenance recommendation
    failure_probability: Optional[float] = None  # Probability of failure (0-1)
    timestamp: str
    
    class Config:
        schema_extra = {
            "example": {
                "elevator_id": "ELEV-001",
                "estimated_days": 120,
                "estimated_cycles": 12000,
                "confidence": 0.78,
                "recommendation": "Plan rope replacement in next quarter",
                "failure_probability": 0.15,
                "timestamp": "2025-10-31T22:00:00"
            }
        }


class TechnicianProfile(BaseModel):
    """Schema for technician gamification profile"""
    technician_id: str
    name: str
    email: str
    points: int                         # Gamification points
    level: str                          # e.g., "Bronze", "Silver", "Gold"
    badges: List[str]                   # Earned badges
    alerts_resolved: int                # Total alerts resolved
    response_time_avg: float            # Average response time (hours)
    preventive_actions: int             # Preventive maintenance performed
    
    class Config:
        schema_extra = {
            "example": {
                "technician_id": "TECH-001",
                "name": "John Doe",
                "email": "john.doe@elevatech.com",
                "points": 1250,
                "level": "Gold",
                "badges": ["Quick Responder", "Zero Downtime Hero", "Preventive Master"],
                "alerts_resolved": 45,
                "response_time_avg": 2.3,
                "preventive_actions": 12
            }
        }


class ProcurementRequest(BaseModel):
    """Schema for automated procurement requests"""
    request_id: str
    elevator_id: str
    part_name: str                      # e.g., "Steel Wire Rope 8x19"
    quantity: int
    urgency: str                        # "Low", "Medium", "High", "Critical"
    estimated_cost: float
    supplier: Optional[str] = None
    status: str                         # "Pending", "Approved", "Ordered", "Delivered"
    requested_date: str
    required_by_date: str
    notes: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "request_id": "PROC-001",
                "elevator_id": "ELEV-001",
                "part_name": "Steel Wire Rope 8x19, 13mm diameter",
                "quantity": 1,
                "urgency": "High",
                "estimated_cost": 30000.0,
                "supplier": "Industrial Ropes Ltd.",
                "status": "Pending",
                "requested_date": "2025-10-31",
                "required_by_date": "2025-11-07",
                "notes": "Critical alert triggered - rope wear at 78%"
            }
        }


class SystemHealth(BaseModel):
    """Schema for overall system health dashboard"""
    total_elevators: int
    active_alerts: int
    resolved_alerts_today: int
    average_fleet_health: float
    total_savings_this_month: float
    top_performing_technician: Optional[str] = None
    system_uptime_percentage: float
    data_points_collected_today: int
    timestamp: str
    
    class Config:
        schema_extra = {
            "example": {
                "total_elevators": 25,
                "active_alerts": 5,
                "resolved_alerts_today": 12,
                "average_fleet_health": 78.5,
                "total_savings_this_month": 340000.0,
                "top_performing_technician": "John Doe",
                "system_uptime_percentage": 99.8,
                "data_points_collected_today": 36000,
                "timestamp": "2025-10-31T22:00:00"
            }
        }


class RealTimeMetrics(BaseModel):
    """Schema for real-time dashboard metrics"""
    elevator_id: str
    current_status: str
    live_tension: float
    live_vibration: float
    live_temperature: float
    current_load: float
    last_updated: str
    next_inspection_due: str
    
    class Config:
        schema_extra = {
            "example": {
                "elevator_id": "ELEV-001",
                "current_status": "Healthy",
                "live_tension": 96.2,
                "live_vibration": 11.8,
                "live_temperature": 31.5,
                "current_load": 420.0,
                "last_updated": "2025-10-31T22:00:00",
                "next_inspection_due": "2025-12-15"
            }
        }
