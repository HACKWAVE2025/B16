# simulate.py: Realistic sensor data generator for Elevatech SmartLift Monitor
# Creates varied scenarios: healthy elevators, degrading ones, and critical cases

import random
import time
from datetime import datetime, timedelta
from typing import Dict, List
import sys

# Import our models and database
from models import SensorData, ElevatorInfo, Alert, TechnicianProfile
from db import (
    insert_sensor_data, insert_elevator_info, insert_alert, 
    insert_technician, get_all_elevators
)
from ml_model import classify_rope_health

class ElevatorSimulator:
    """Simulates realistic sensor data for elevator ropes"""
    
    def __init__(self):
        self.elevator_profiles = {}
        self.alert_counter = 0
        
    def create_elevator_profile(self, elevator_id: str, health_status: str = "healthy") -> Dict:
        """
        Create an elevator profile with base characteristics
        
        health_status: "healthy", "degrading", "critical"
        """
        if health_status == "healthy":
            profile = {
                "base_tension": random.uniform(93, 98),
                "base_vibration": random.uniform(8, 13),
                "base_wear": random.uniform(20, 40),
                "base_temperature": random.uniform(28, 35),
                "base_rope_diameter": random.uniform(12.7, 13.1),
                "base_corrosion": random.uniform(5, 15),
                "base_elongation": random.uniform(1.0, 2.5),
                "base_load_weight": random.uniform(350, 550),
                "load_cycles": random.randint(1000, 10000),
                "degradation_rate": 0.001  # Very slow degradation
            }
        elif health_status == "degrading":
            profile = {
                "base_tension": random.uniform(88, 92),
                "base_vibration": random.uniform(14, 18),
                "base_wear": random.uniform(50, 65),
                "base_temperature": random.uniform(38, 45),
                "base_rope_diameter": random.uniform(12.3, 12.6),
                "base_corrosion": random.uniform(20, 30),
                "base_elongation": random.uniform(3.0, 4.0),
                "base_load_weight": random.uniform(550, 650),
                "load_cycles": random.randint(25000, 40000),
                "degradation_rate": 0.005  # Moderate degradation
            }
        else:  # critical
            profile = {
                "base_tension": random.uniform(80, 86),
                "base_vibration": random.uniform(19, 24),
                "base_wear": random.uniform(75, 90),
                "base_temperature": random.uniform(48, 55),
                "base_rope_diameter": random.uniform(11.5, 12.1),
                "base_corrosion": random.uniform(40, 60),
                "base_elongation": random.uniform(5.0, 7.0),
                "base_load_weight": random.uniform(700, 850),
                "load_cycles": random.randint(45000, 55000),
                "degradation_rate": 0.01  # Fast degradation
            }
        
        self.elevator_profiles[elevator_id] = profile
        return profile
    
    def generate_reading(self, elevator_id: str) -> Dict:
        """Generate a single sensor reading with realistic variations"""
        
        if elevator_id not in self.elevator_profiles:
            # Default to healthy if no profile exists
            self.create_elevator_profile(elevator_id, "healthy")
        
        profile = self.elevator_profiles[elevator_id]
        
        # Add random variations (noise)
        reading = {
            "timestamp": datetime.utcnow().isoformat(),
            "elevator_id": elevator_id,
            "tension": max(70, profile["base_tension"] + random.uniform(-2, 2)),
            "vibration": max(5, profile["base_vibration"] + random.uniform(-1.5, 1.5)),
            "wear": min(100, max(0, profile["base_wear"] + random.uniform(-2, 2))),
            "load_cycles": profile["load_cycles"],
            "temperature": max(20, profile["base_temperature"] + random.uniform(-3, 3)),
            "rope_diameter": max(10, profile["base_rope_diameter"] + random.uniform(-0.2, 0.1)),
            "corrosion_level": min(100, max(0, profile["base_corrosion"] + random.uniform(-2, 2))),
            "elongation": max(0, profile["base_elongation"] + random.uniform(-0.3, 0.3)),
            "load_weight": max(0, profile["base_load_weight"] + random.uniform(-100, 100))
        }
        
        # Increment load cycles
        profile["load_cycles"] += random.randint(1, 5)
        
        # Apply gradual degradation
        profile["base_tension"] -= profile["degradation_rate"] * random.uniform(0.5, 1.5)
        profile["base_vibration"] += profile["degradation_rate"] * random.uniform(0.5, 1.5)
        profile["base_wear"] += profile["degradation_rate"] * random.uniform(2, 5)
        profile["base_temperature"] += profile["degradation_rate"] * random.uniform(0.3, 0.8)
        profile["base_rope_diameter"] -= profile["degradation_rate"] * random.uniform(0.01, 0.03)
        profile["base_corrosion"] += profile["degradation_rate"] * random.uniform(1, 3)
        profile["base_elongation"] += profile["degradation_rate"] * random.uniform(0.02, 0.05)
        
        return reading
    
    def check_and_create_alerts(self, elevator_id: str, sensor_data: Dict) -> None:
        """Check sensor data and create alerts if needed"""
        
        # Classify the health
        result = classify_rope_health(sensor_data)
        
        if result['status'] in ['Warning', 'Critical']:
            self.alert_counter += 1
            alert_id = f"ALERT-{self.alert_counter:04d}"
            
            alert = Alert(
                alert_id=alert_id,
                elevator_id=elevator_id,
                alert_type=result['status'],
                message=f"{result['status']} alert: {result['reason'][:100]}",
                timestamp=datetime.utcnow().isoformat(),
                resolved=False,
                triggered_by=result['triggered_metrics'][0] if result['triggered_metrics'] else "multiple"
            )
            
            insert_alert(alert)
            print(f"   🚨 {result['status']} Alert Created: {alert_id} for {elevator_id}")


def initialize_demo_data():
    """Initialize database with demo elevators and technicians"""
    
    print("\n" + "="*70)
    print("🏗️  INITIALIZING DEMO DATA FOR ELEVATECH SMARTLIFT MONITOR")
    print("="*70 + "\n")
    
    # Create diverse elevator fleet
    buildings = [
        ("Tech Tower A", "Mumbai"),
        ("Business Park B", "Bangalore"),
        ("Corporate Hub C", "Delhi"),
        ("Innovation Center", "Hyderabad"),
        ("Commerce Plaza", "Pune")
    ]
    
    elevator_data = []
    
    for i, (building, location) in enumerate(buildings):
        # Each building has 3-5 elevators with mixed health
        num_elevators = random.randint(3, 5)
        
        for j in range(num_elevators):
            elevator_id = f"ELEV-{(i * 5 + j + 1):03d}"
            
            # Mix of health statuses: 60% healthy, 30% degrading, 10% critical
            rand = random.random()
            if rand < 0.6:
                health = "healthy"
            elif rand < 0.9:
                health = "degrading"
            else:
                health = "critical"
            
            elevator = ElevatorInfo(
                elevator_id=elevator_id,
                building_name=building,
                floor_range=f"B2 to {random.randint(15, 30)}",
                installation_date=f"{random.randint(2015, 2022)}-{random.randint(1, 12):02d}-15",
                last_maintenance=f"2025-{random.randint(8, 10):02d}-{random.randint(1, 28):02d}",
                rope_type=random.choice([
                    "8x19 Steel Wire Rope",
                    "8x25 Filler Wire Rope",
                    "6x36 Wire Rope"
                ]),
                location=location
            )
            
            insert_elevator_info(elevator)
            elevator_data.append((elevator_id, health))
            print(f"   ✅ Created {elevator_id} in {building} ({location}) - Status: {health}")
    
    print(f"\n📊 Total Elevators Created: {len(elevator_data)}")
    
    # Create technician profiles
    technicians = [
        ("TECH-001", "Rajesh Kumar", "rajesh.kumar@elevatech.com"),
        ("TECH-002", "Priya Sharma", "priya.sharma@elevatech.com"),
        ("TECH-003", "Arjun Patel", "arjun.patel@elevatech.com"),
        ("TECH-004", "Sneha Reddy", "sneha.reddy@elevatech.com"),
        ("TECH-005", "Vikram Singh", "vikram.singh@elevatech.com")
    ]
    
    print("\n👷 Creating Technician Profiles:")
    for tech_id, name, email in technicians:
        tech = TechnicianProfile(
            technician_id=tech_id,
            name=name,
            email=email,
            points=random.randint(100, 1000),
            level=random.choice(["Bronze", "Silver", "Gold"]),
            badges=random.sample([
                "Quick Responder",
                "Zero Downtime Hero",
                "Preventive Master",
                "Safety Champion",
                "Efficiency Expert"
            ], random.randint(1, 3)),
            alerts_resolved=random.randint(10, 50),
            response_time_avg=random.uniform(1.5, 4.0),
            preventive_actions=random.randint(5, 20)
        )
        insert_technician(tech)
        print(f"   ✅ Created {name} ({tech.level} level)")
    
    print("\n" + "="*70)
    print("✅ INITIALIZATION COMPLETE!")
    print("="*70 + "\n")
    
    return elevator_data


def generate_historical_data(elevator_data: List[tuple], days: int = 7):
    """Generate historical sensor data for past days"""
    
    print(f"\n📈 Generating {days} days of historical data...")
    print("-" * 70)
    
    simulator = ElevatorSimulator()
    
    # Create profiles for all elevators
    for elevator_id, health in elevator_data:
        simulator.create_elevator_profile(elevator_id, health)
    
    total_readings = 0
    
    # Generate data for each day
    for day in range(days, 0, -1):
        day_date = datetime.utcnow() - timedelta(days=day)
        
        # Generate 10-20 readings per elevator per day
        for elevator_id, health in elevator_data:
            readings_count = random.randint(10, 20)
            
            for _ in range(readings_count):
                reading = simulator.generate_reading(elevator_id)
                # Adjust timestamp to past
                reading['timestamp'] = (day_date + timedelta(
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )).isoformat()
                
                sensor = SensorData(**reading)
                insert_sensor_data(sensor)
                total_readings += 1
        
        print(f"   ✅ Day {days - day + 1}/{days} complete")
    
    print(f"\n📊 Total Historical Readings Generated: {total_readings}")
    print("-" * 70)
    
    return simulator


def run_live_simulation(simulator: ElevatorSimulator, duration_seconds: int = 60, interval_seconds: int = 3):
    """Run live simulation that generates data in real-time"""
    
    print(f"\n🔴 STARTING LIVE SIMULATION (Duration: {duration_seconds}s, Interval: {interval_seconds}s)")
    print("="*70)
    
    elevators = get_all_elevators()
    
    if not elevators:
        print("❌ No elevators found in database. Run initialization first.")
        return
    
    start_time = time.time()
    iteration = 0
    
    try:
        while (time.time() - start_time) < duration_seconds:
            iteration += 1
            print(f"\n⏱️  Iteration {iteration} - {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 70)
            
            # Generate reading for each elevator
            for elevator in elevators:
                elevator_id = elevator['elevator_id']
                
                # Ensure profile exists
                if elevator_id not in simulator.elevator_profiles:
                    # Determine health from existing data or random
                    health = random.choice(["healthy", "healthy", "degrading", "critical"])
                    simulator.create_elevator_profile(elevator_id, health)
                
                # Generate and store reading
                reading = simulator.generate_reading(elevator_id)
                sensor = SensorData(**reading)
                insert_sensor_data(sensor)
                
                # Check for alerts
                simulator.check_and_create_alerts(elevator_id, reading)
                
                # Classify and display status
                result = classify_rope_health(reading)
                status_emoji = "🟢" if result['status'] == "Healthy" else "🟡" if result['status'] == "Warning" else "🔴"
                
                print(f"   {status_emoji} {elevator_id}: {result['status']} (Risk: {result['risk_score']}/100)")
            
            print(f"\n   💾 {len(elevators)} readings stored")
            
            # Wait for next iteration
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n\n⏸️  Simulation stopped by user")
    
    print("\n" + "="*70)
    print(f"✅ SIMULATION COMPLETE - Generated data for {iteration} iterations")
    print("="*70)


def main():
    """Main execution function"""
    
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║     ELEVATECH SMARTLIFT MONITOR - DATA SIMULATOR                  ║")
    print("║     Predictive Maintenance for Elevator Ropes                     ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print("\n")
    
    print("Choose simulation mode:")
    print("  1. Full Setup (Initialize + Historical + Live)")
    print("  2. Initialize Demo Data Only")
    print("  3. Generate Historical Data (7 days)")
    print("  4. Run Live Simulation Only")
    print("  5. Quick Demo (Initialize + 30sec live)")
    
    try:
        choice = input("\nEnter your choice (1-5): ").strip()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        return
    
    if choice == "1":
        # Full setup
        elevator_data = initialize_demo_data()
        simulator = generate_historical_data(elevator_data, days=7)
        print("\n⏳ Starting live simulation in 3 seconds...")
        time.sleep(3)
        run_live_simulation(simulator, duration_seconds=60, interval_seconds=5)
        
    elif choice == "2":
        # Initialize only
        initialize_demo_data()
        
    elif choice == "3":
        # Historical data only
        elevators = get_all_elevators()
        if not elevators:
            print("❌ No elevators found. Please run initialization first (option 2).")
            return
        
        elevator_data = [(e['elevator_id'], 'healthy') for e in elevators]
        generate_historical_data(elevator_data, days=7)
        
    elif choice == "4":
        # Live simulation only
        elevators = get_all_elevators()
        if not elevators:
            print("❌ No elevators found. Please run initialization first (option 2).")
            return
        
        simulator = ElevatorSimulator()
        
        # Ask for duration
        try:
            duration = int(input("Enter simulation duration in seconds (default 60): ") or "60")
            interval = int(input("Enter reading interval in seconds (default 3): ") or "3")
        except ValueError:
            duration = 60
            interval = 3
        
        run_live_simulation(simulator, duration_seconds=duration, interval_seconds=interval)
        
    elif choice == "5":
        # Quick demo
        elevator_data = initialize_demo_data()
        print("\n⏳ Starting quick demo in 3 seconds...")
        time.sleep(3)
        
        simulator = ElevatorSimulator()
        for elevator_id, health in elevator_data:
            simulator.create_elevator_profile(elevator_id, health)
        
        run_live_simulation(simulator, duration_seconds=30, interval_seconds=3)
        
    else:
        print("❌ Invalid choice. Please run again and select 1-5.")
        return
    
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                    SIMULATION SUMMARY                              ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    # Show summary stats
    from db import get_database_stats, get_fleet_summary
    
    stats = get_database_stats()
    fleet = get_fleet_summary()
    
    print("\n📊 Database Statistics:")
    print(f"   - Total Elevators: {stats['total_elevators']}")
    print(f"   - Total Sensor Readings: {stats['total_sensor_readings']}")
    print(f"   - Total Alerts: {stats['total_alerts']}")
    print(f"   - Total Technicians: {stats['total_technicians']}")
    
    print("\n🏢 Fleet Summary:")
    print(f"   - Active Alerts: {fleet['active_alerts']}")
    print(f"   - Resolved Today: {fleet['resolved_alerts_today']}")
    print(f"   - Total Savings (30 days): ₹{fleet['total_savings_this_month']:,.2f}")
    
    print("\n✅ Simulation complete! Your database is now populated.")
    print("💡 Next step: Run main.py to start the API server\n")


# ============ STANDALONE FUNCTIONS ============

def quick_test():
    """Quick test to generate a few readings without full simulation"""
    print("🧪 Quick Test Mode - Generating sample data...\n")
    
    simulator = ElevatorSimulator()
    
    # Create 3 test elevators
    test_elevators = [
        ("TEST-001", "healthy"),
        ("TEST-002", "degrading"),
        ("TEST-003", "critical")
    ]
    
    for elevator_id, health in test_elevators:
        simulator.create_elevator_profile(elevator_id, health)
        
        for i in range(5):
            reading = simulator.generate_reading(elevator_id)
            print(f"{elevator_id} ({health}):")
            print(f"  Tension: {reading['tension']:.1f}N | Wear: {reading['wear']:.1f}%")
            print(f"  Vibration: {reading['vibration']:.1f}mm/s | Temp: {reading['temperature']:.1f}°C")
            
            result = classify_rope_health(reading)
            print(f"  Status: {result['status']} | Risk: {result['risk_score']}/100\n")


def generate_single_reading(elevator_id: str = "DEMO-001", health: str = "healthy"):
    """Generate a single reading for testing"""
    simulator = ElevatorSimulator()
    simulator.create_elevator_profile(elevator_id, health)
    reading = simulator.generate_reading(elevator_id)
    
    print(f"\n📊 Generated Reading for {elevator_id}:")
    print("-" * 50)
    for key, value in reading.items():
        if key != "timestamp":
            print(f"  {key:20s}: {value}")
    
    result = classify_rope_health(reading)
    print(f"\n  Classification: {result['status']}")
    print(f"  Risk Score: {result['risk_score']}/100")
    print(f"  Reason: {result['reason']}")
    
    return reading


def simulate_degradation_timeline(elevator_id: str = "DEMO-001", iterations: int = 20):
    """Simulate and display how an elevator degrades over time"""
    print(f"\n📉 Simulating Degradation Timeline for {elevator_id}")
    print("="*70 + "\n")
    
    simulator = ElevatorSimulator()
    simulator.create_elevator_profile(elevator_id, "healthy")
    
    # Increase degradation rate for demo
    simulator.elevator_profiles[elevator_id]['degradation_rate'] = 0.05
    
    for i in range(iterations):
        reading = simulator.generate_reading(elevator_id)
        result = classify_rope_health(reading)
        
        status_emoji = "🟢" if result['status'] == "Healthy" else "🟡" if result['status'] == "Warning" else "🔴"
        
        print(f"Iteration {i+1:2d}: {status_emoji} {result['status']:8s} | "
              f"Risk: {result['risk_score']:5.1f}/100 | "
              f"Wear: {reading['wear']:5.1f}% | "
              f"Tension: {reading['tension']:5.1f}N")
        
        if result['status'] == "Critical":
            print(f"\n🚨 CRITICAL STATUS REACHED at iteration {i+1}")
            print(f"   Reason: {result['reason']}")
            break


# ============ BATCH DATA GENERATION ============

def generate_batch_readings(num_readings: int = 100):
    """Generate a batch of readings and store them"""
    print(f"\n⚡ Generating {num_readings} batch readings...")
    
    elevators = get_all_elevators()
    if not elevators:
        print("❌ No elevators in database. Run initialization first.")
        return
    
    simulator = ElevatorSimulator()
    
    for i in range(num_readings):
        # Pick random elevator
        elevator = random.choice(elevators)
        elevator_id = elevator['elevator_id']
        
        # Generate and store
        if elevator_id not in simulator.elevator_profiles:
            health = random.choice(["healthy", "healthy", "degrading"])
            simulator.create_elevator_profile(elevator_id, health)
        
        reading = simulator.generate_reading(elevator_id)
        sensor = SensorData(**reading)
        insert_sensor_data(sensor)
        
        if (i + 1) % 20 == 0:
            print(f"   Progress: {i+1}/{num_readings} readings generated")
    
    print(f"\n✅ {num_readings} readings generated and stored!")


# ============ ENTRY POINT ============

if __name__ == "__main__":
    import sys
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            quick_test()
        elif command == "single":
            generate_single_reading()
        elif command == "degrade":
            simulate_degradation_timeline()
        elif command == "batch":
            num = int(sys.argv[2]) if len(sys.argv) > 2 else 100
            generate_batch_readings(num)
        elif command == "init":
            initialize_demo_data()
        elif command == "live":
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            elevators = get_all_elevators()
            if elevators:
                simulator = ElevatorSimulator()
                run_live_simulation(simulator, duration_seconds=duration)
            else:
                print("❌ No elevators found. Run 'python simulate.py init' first")
        else:
            print("Unknown command. Available commands:")
            print("  python simulate.py test       - Quick test")
            print("  python simulate.py single     - Generate single reading")
            print("  python simulate.py degrade    - Show degradation timeline")
            print("  python simulate.py batch 100  - Generate 100 readings")
            print("  python simulate.py init       - Initialize demo data")
            print("  python simulate.py live 60    - Run live simulation for 60s")
    else:
        # Run interactive menu
        main()

