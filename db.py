# db.py: Database connection and helpers for Elevatech backend (SQLite)
# Enhanced with fleet analytics, gamification, procurement, and cost savings

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from models import (
    SensorData, Alert, ElevatorInfo, MaintenanceRecord,
    TechnicianProfile, ProcurementRequest, CostSavings
)

# Database file
DB_FILE = "elevatech.db"


def init_db():
    """Initialize database and create tables if they don't exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Sensor data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            elevator_id TEXT NOT NULL,
            tension REAL NOT NULL,
            vibration REAL NOT NULL,
            wear REAL NOT NULL,
            load_cycles INTEGER NOT NULL,
            temperature REAL NOT NULL,
            rope_diameter REAL NOT NULL,
            corrosion_level REAL NOT NULL,
            elongation REAL NOT NULL,
            load_weight REAL NOT NULL
        )
    """)
    
    # Alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id TEXT UNIQUE NOT NULL,
            elevator_id TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            resolved INTEGER DEFAULT 0,
            triggered_by TEXT,
            assigned_to TEXT
        )
    """)
    
    # Elevator info table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS elevator_info (
            elevator_id TEXT PRIMARY KEY,
            building_name TEXT NOT NULL,
            floor_range TEXT NOT NULL,
            installation_date TEXT NOT NULL,
            last_maintenance TEXT NOT NULL,
            rope_type TEXT NOT NULL,
            location TEXT
        )
    """)
    
    # Maintenance records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maintenance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id TEXT UNIQUE NOT NULL,
            elevator_id TEXT NOT NULL,
            maintenance_date TEXT NOT NULL,
            technician_name TEXT NOT NULL,
            action_taken TEXT NOT NULL,
            parts_replaced TEXT,
            cost REAL,
            notes TEXT,
            downtime_hours REAL
        )
    """)
    
    # Technician profiles table (Gamification)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS technician_profiles (
            technician_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            points INTEGER DEFAULT 0,
            level TEXT DEFAULT 'Bronze',
            badges TEXT,
            alerts_resolved INTEGER DEFAULT 0,
            response_time_avg REAL DEFAULT 0,
            preventive_actions INTEGER DEFAULT 0
        )
    """)
    
    # Procurement requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS procurement_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT UNIQUE NOT NULL,
            elevator_id TEXT NOT NULL,
            part_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            urgency TEXT NOT NULL,
            estimated_cost REAL NOT NULL,
            supplier TEXT,
            status TEXT DEFAULT 'Pending',
            requested_date TEXT NOT NULL,
            required_by_date TEXT NOT NULL,
            notes TEXT
        )
    """)
    
    # Cost savings records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cost_savings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            elevator_id TEXT NOT NULL,
            total_savings REAL NOT NULL,
            breakdown TEXT NOT NULL,
            comparison TEXT NOT NULL,
            roi_percentage REAL NOT NULL,
            period TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    
    # System metrics table (for dashboard)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")


def insert_sensor_data(data: SensorData) -> bool:
    """Insert a new sensor reading"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sensor_data 
            (timestamp, elevator_id, tension, vibration, wear, load_cycles, 
             temperature, rope_diameter, corrosion_level, elongation, load_weight)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.timestamp, data.elevator_id, data.tension, data.vibration,
            data.wear, data.load_cycles, data.temperature, data.rope_diameter,
            data.corrosion_level, data.elongation, data.load_weight
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error inserting sensor data: {e}")
        return False


def get_latest_sensor_data(elevator_id: str, limit: int = 10) -> List[Dict]:
    """Get the latest sensor readings for an elevator"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM sensor_data 
        WHERE elevator_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (elevator_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_all_sensor_data(limit: int = 100) -> List[Dict]:
    """Get all recent sensor readings"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM sensor_data 
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_sensor_data_by_elevator(elevator_id: str) -> List[Dict]:
    """Get all sensor data for a specific elevator"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM sensor_data 
        WHERE elevator_id = ?
        ORDER BY timestamp DESC
    """, (elevator_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def insert_alert(alert: Alert) -> bool:
    """Insert a new alert"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO alerts 
            (alert_id, elevator_id, alert_type, message, timestamp, resolved, triggered_by, assigned_to)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.alert_id, alert.elevator_id, alert.alert_type, 
            alert.message, alert.timestamp, alert.resolved, alert.triggered_by, alert.assigned_to
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error inserting alert: {e}")
        return False


def get_alerts(elevator_id: Optional[str] = None, resolved: Optional[bool] = None) -> List[Dict]:
    """Get alerts, optionally filtered by elevator and resolution status"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM alerts WHERE 1=1"
    params = []
    
    if elevator_id:
        query += " AND elevator_id = ?"
        params.append(elevator_id)
    
    if resolved is not None:
        query += " AND resolved = ?"
        params.append(1 if resolved else 0)
    
    query += " ORDER BY timestamp DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def resolve_alert(alert_id: str, technician_id: str) -> bool:
    """Mark an alert as resolved"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE alerts 
            SET resolved = 1, assigned_to = ?
            WHERE alert_id = ?
        """, (technician_id, alert_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error resolving alert: {e}")
        return False


def insert_elevator_info(info: ElevatorInfo) -> bool:
    """Insert or update elevator information"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO elevator_info 
            (elevator_id, building_name, floor_range, installation_date, last_maintenance, rope_type, location)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            info.elevator_id, info.building_name, info.floor_range,
            info.installation_date, info.last_maintenance, info.rope_type, info.location
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error inserting elevator info: {e}")
        return False


def get_all_elevators() -> List[Dict]:
    """Get all registered elevators"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM elevator_info")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def insert_maintenance_record(record: MaintenanceRecord) -> bool:
    """Insert a maintenance record"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO maintenance_records 
            (record_id, elevator_id, maintenance_date, technician_name, action_taken, 
             parts_replaced, cost, notes, downtime_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.record_id, record.elevator_id, record.maintenance_date,
            record.technician_name, record.action_taken, record.parts_replaced,
            record.cost, record.notes, record.downtime_hours
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error inserting maintenance record: {e}")
        return False


def get_maintenance_history(elevator_id: str) -> List[Dict]:
    """Get maintenance history for an elevator"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM maintenance_records 
        WHERE elevator_id = ?
        ORDER BY maintenance_date DESC
    """, (elevator_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# ============ GAMIFICATION FUNCTIONS ============

def insert_technician(profile: TechnicianProfile) -> bool:
    """Insert or update technician profile"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        badges_json = json.dumps(profile.badges)
        
        cursor.execute("""
            INSERT OR REPLACE INTO technician_profiles 
            (technician_id, name, email, points, level, badges, alerts_resolved, response_time_avg, preventive_actions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.technician_id, profile.name, profile.email, profile.points,
            profile.level, badges_json, profile.alerts_resolved, 
            profile.response_time_avg, profile.preventive_actions
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error inserting technician: {e}")
        return False


def get_technician(technician_id: str) -> Optional[Dict]:
    """Get technician profile"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM technician_profiles WHERE technician_id = ?", (technician_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        result = dict(row)
        result['badges'] = json.loads(result['badges']) if result['badges'] else []
        return result
    return None


def get_all_technicians() -> List[Dict]:
    """Get all technicians ranked by points"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM technician_profiles ORDER BY points DESC")
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        result = dict(row)
        result['badges'] = json.loads(result['badges']) if result['badges'] else []
        results.append(result)
    
    return results


def update_technician_points(technician_id: str, points_to_add: int) -> bool:
    """Add points to a technician"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE technician_profiles 
            SET points = points + ?
            WHERE technician_id = ?
        """, (points_to_add, technician_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating points: {e}")
        return False


# ============ PROCUREMENT FUNCTIONS ============

def insert_procurement_request(request: ProcurementRequest) -> bool:
    """Insert a procurement request"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO procurement_requests 
            (request_id, elevator_id, part_name, quantity, urgency, estimated_cost, 
             supplier, status, requested_date, required_by_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.request_id, request.elevator_id, request.part_name, request.quantity,
            request.urgency, request.estimated_cost, request.supplier, request.status,
            request.requested_date, request.required_by_date,
            request.notes
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error inserting procurement request: {e}")
        return False


def get_procurement_requests(elevator_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
    """Get procurement requests with optional filters"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM procurement_requests WHERE 1=1"
    params = []
    
    if elevator_id:
        query += " AND elevator_id = ?"
        params.append(elevator_id)
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY requested_date DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def update_procurement_status(request_id: str, new_status: str) -> bool:
    """Update procurement request status"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE procurement_requests 
            SET status = ?
            WHERE request_id = ?
        """, (new_status, request_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating procurement status: {e}")
        return False


# ============ COST SAVINGS FUNCTIONS ============

def insert_cost_savings(savings: CostSavings) -> bool:
    """Insert cost savings record"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        breakdown_json = json.dumps(savings.breakdown)
        comparison_json = json.dumps(savings.comparison)
        
        cursor.execute("""
            INSERT INTO cost_savings 
            (elevator_id, total_savings, breakdown, comparison, roi_percentage, period, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            savings.elevator_id, savings.total_savings, breakdown_json,
            comparison_json, savings.roi_percentage, savings.period, savings.timestamp
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error inserting cost savings: {e}")
        return False


def get_cost_savings(elevator_id: Optional[str] = None) -> List[Dict]:
    """Get cost savings records"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if elevator_id:
        cursor.execute("""
            SELECT * FROM cost_savings 
            WHERE elevator_id = ?
            ORDER BY timestamp DESC
        """, (elevator_id,))
    else:
        cursor.execute("SELECT * FROM cost_savings ORDER BY timestamp DESC")
    
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        result = dict(row)
        result['breakdown'] = json.loads(result['breakdown'])
        result['comparison'] = json.loads(result['comparison'])
        results.append(result)
    
    return results


def get_total_savings(period_days: int = 30) -> float:
    """Get total savings over a period"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT SUM(total_savings) as total
        FROM cost_savings
        WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' days')
    """, (period_days,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result if result else 0.0


# ============ ANALYTICS & DASHBOARD FUNCTIONS ============

def get_fleet_summary() -> Dict:
    """Get summary statistics for entire fleet"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Total elevators
    cursor.execute("SELECT COUNT(*) as count FROM elevator_info")
    total_elevators = cursor.fetchone()['count']
    
    # Active alerts
    cursor.execute("SELECT COUNT(*) as count FROM alerts WHERE resolved = 0")
    active_alerts = cursor.fetchone()['count']
    
    # Resolved alerts today
    cursor.execute("""
        SELECT COUNT(*) as count FROM alerts 
        WHERE resolved = 1 AND date(timestamp) = date('now')
    """)
    resolved_today = cursor.fetchone()['count']
    
    # Total savings this month
    cursor.execute("""
        SELECT SUM(total_savings) as total
        FROM cost_savings
        WHERE datetime(timestamp) >= datetime('now', '-30 days')
    """)
    savings_result = cursor.fetchone()
    total_savings = savings_result['total'] if savings_result['total'] else 0.0
    
    conn.close()
    
    return {
        "total_elevators": total_elevators,
        "active_alerts": active_alerts,
        "resolved_alerts_today": resolved_today,
        "total_savings_this_month": round(total_savings, 2),
        "timestamp": datetime.utcnow().isoformat()
    }


def get_elevator_status_counts() -> Dict:
    """Get count of elevators by status (requires latest sensor data analysis)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get unique elevators
    cursor.execute("SELECT elevator_id FROM elevator_info")
    elevators = [row for row in cursor.fetchall()]
    
    conn.close()
    
    # This will be populated by the API layer after ML classification
    return {
        "total": len(elevators),
        "healthy": 0,
        "warning": 0,
        "critical": 0
    }


def insert_system_metric(metric_name: str, metric_value: float) -> bool:
    """Insert a system metric for tracking"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO system_metrics (metric_name, metric_value, timestamp)
            VALUES (?, ?, ?)
        """, (metric_name, metric_value, datetime.utcnow().isoformat()))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error inserting system metric: {e}")
        return False


def get_system_metrics(metric_name: str, limit: int = 100) -> List[Dict]:
    """Get historical system metrics"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM system_metrics 
        WHERE metric_name = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (metric_name, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# ============ UTILITY FUNCTIONS ============

def get_database_stats() -> Dict:
    """Get database statistics for monitoring"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM sensor_data")
    total_readings = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) FROM alerts")
    total_alerts = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) FROM elevator_info")
    total_elevators = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) FROM technician_profiles")
    total_technicians = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) FROM procurement_requests")
    total_procurements = cursor.fetchone()
    
    conn.close()
    
    return {
        "total_sensor_readings": total_readings,
        "total_alerts": total_alerts,
        "total_elevators": total_elevators,
        "total_technicians": total_technicians,
        "total_procurement_requests": total_procurements
    }


def clear_old_sensor_data(days_to_keep: int = 90) -> int:
    """Delete sensor data older than specified days"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM sensor_data 
            WHERE datetime(timestamp) < datetime('now', '-' || ? || ' days')
        """, (days_to_keep,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"🗑️ Deleted {deleted} old sensor records")
        return deleted
    except Exception as e:
        print(f"Error clearing old data: {e}")
        return 0


# Initialize database when this module is imported
init_db()


# ============ QUICK TEST ============
if __name__ == "__main__":
    from models import SensorData, ElevatorInfo, TechnicianProfile
    
    print("🧪 Testing Database Functions\n")
    
    # Test 1: Insert Elevator Info
    print("1. Testing Elevator Info...")
    elevator = ElevatorInfo(
        elevator_id="ELEV-001",
        building_name="Tech Tower A",
        floor_range="B2 to 20",
        installation_date="2020-05-15",
        last_maintenance="2025-09-30",
        rope_type="8x19 Steel Wire Rope",
        location="Mumbai, Maharashtra"
    )
    insert_elevator_info(elevator)
    elevators = get_all_elevators()
    print(f"   ✅ Elevators in DB: {len(elevators)}")
    
    # Test 2: Insert Sensor Data
    print("\n2. Testing Sensor Data...")
    sensor = SensorData(
        timestamp=datetime.utcnow().isoformat(),
        elevator_id="ELEV-001",
        tension=95.5,
        vibration=12.3,
        wear=45.2,
        load_cycles=1500,
        temperature=32.5,
        rope_diameter=12.8,
        corrosion_level=15.0,
        elongation=2.3,
        load_weight=450.0
    )
    insert_sensor_data(sensor)
    readings = get_latest_sensor_data("ELEV-001", 5)
    print(f"   ✅ Sensor readings: {len(readings)}")
    
    # Test 3: Insert Technician
    print("\n3. Testing Technician Profile...")
    tech = TechnicianProfile(
        technician_id="TECH-001",
        name="John Doe",
        email="john@elevatech.com",
        points=500,
        level="Silver",
        badges=["Quick Responder", "First Alert"],
        alerts_resolved=15,
        response_time_avg=2.5,
        preventive_actions=5
    )
    insert_technician(tech)
    techs = get_all_technicians()
    print(f"   ✅ Technicians in DB: {len(techs)}")
    
    # Test 4: Database Stats
    print("\n4. Database Statistics:")
    stats = get_database_stats()
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    # Test 5: Fleet Summary
    print("\n5. Fleet Summary:")
    summary = get_fleet_summary()
    for key, value in summary.items():
        print(f"   - {key}: {value}")
    
    print("\n✅ All database tests completed successfully!")
