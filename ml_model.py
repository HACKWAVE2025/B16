# ml_model.py: Machine Learning and rule-based classification for rope health
# Enhanced with cost savings, fleet analytics, and advanced features

from typing import Dict, Tuple, List
from datetime import datetime
import random

class RopeHealthClassifier:
    """Classifier for elevator rope health status"""
    
    def __init__(self):
        # Define thresholds for each metric
        self.thresholds = {
            'tension': {'critical': 85, 'warning': 90},  # Below these values
            'vibration': {'warning': 15, 'critical': 20},  # Above these values
            'wear': {'warning': 50, 'critical': 75},  # Above these values
            'temperature': {'warning': 40, 'critical': 50},  # Above these values
            'rope_diameter': {'critical': 12.0, 'warning': 12.5},  # Below these (normal ~13mm)
            'corrosion_level': {'warning': 20, 'critical': 40},  # Above these values
            'elongation': {'warning': 3.0, 'critical': 5.0},  # Above these values
            'load_weight': {'warning': 600, 'critical': 750}  # Above these values
        }
        
        # Cost constants (in INR)
        self.costs = {
            'rope_replacement': 50000,  # Cost of emergency rope replacement
            'planned_replacement': 30000,  # Cost of planned replacement
            'emergency_downtime_per_hour': 5000,  # Lost revenue per hour
            'emergency_response': 15000,  # Emergency callout fee
            'preventive_inspection': 2000,  # Cost of routine inspection
            'average_emergency_downtime_hours': 8  # Typical emergency repair time
        }
    
    def classify(self, sensor_data: Dict) -> Tuple[str, float, str, List[str]]:
        """
        Classify rope health based on sensor readings
        
        Returns:
            - status: "Healthy", "Warning", or "Critical"
            - confidence: 0-1 confidence score
            - reason: Human-readable explanation
            - critical_metrics: List of metrics that triggered the status
        """
        critical_issues = []
        warning_issues = []
        
        # Check tension (lower is worse)
        if sensor_data['tension'] < self.thresholds['tension']['critical']:
            critical_issues.append(f"Tension critically low ({sensor_data['tension']:.1f}N)")
        elif sensor_data['tension'] < self.thresholds['tension']['warning']:
            warning_issues.append(f"Tension below optimal ({sensor_data['tension']:.1f}N)")
        
        # Check vibration (higher is worse)
        if sensor_data['vibration'] > self.thresholds['vibration']['critical']:
            critical_issues.append(f"Vibration critically high ({sensor_data['vibration']:.1f}mm/s)")
        elif sensor_data['vibration'] > self.thresholds['vibration']['warning']:
            warning_issues.append(f"Vibration elevated ({sensor_data['vibration']:.1f}mm/s)")
        
        # Check wear (higher is worse)
        if sensor_data['wear'] > self.thresholds['wear']['critical']:
            critical_issues.append(f"Wear level critical ({sensor_data['wear']:.1f}%)")
        elif sensor_data['wear'] > self.thresholds['wear']['warning']:
            warning_issues.append(f"Wear level elevated ({sensor_data['wear']:.1f}%)")
        
        # Check temperature (higher is worse)
        if sensor_data['temperature'] > self.thresholds['temperature']['critical']:
            critical_issues.append(f"Temperature critically high ({sensor_data['temperature']:.1f}°C)")
        elif sensor_data['temperature'] > self.thresholds['temperature']['warning']:
            warning_issues.append(f"Temperature elevated ({sensor_data['temperature']:.1f}°C)")
        
        # Check rope diameter (lower is worse - indicates wear)
        if sensor_data['rope_diameter'] < self.thresholds['rope_diameter']['critical']:
            critical_issues.append(f"Rope diameter critically reduced ({sensor_data['rope_diameter']:.1f}mm)")
        elif sensor_data['rope_diameter'] < self.thresholds['rope_diameter']['warning']:
            warning_issues.append(f"Rope diameter reduced ({sensor_data['rope_diameter']:.1f}mm)")
        
        # Check corrosion (higher is worse)
        if sensor_data['corrosion_level'] > self.thresholds['corrosion_level']['critical']:
            critical_issues.append(f"Corrosion critically high ({sensor_data['corrosion_level']:.1f}%)")
        elif sensor_data['corrosion_level'] > self.thresholds['corrosion_level']['warning']:
            warning_issues.append(f"Corrosion detected ({sensor_data['corrosion_level']:.1f}%)")
        
        # Check elongation (higher is worse)
        if sensor_data['elongation'] > self.thresholds['elongation']['critical']:
            critical_issues.append(f"Elongation critically high ({sensor_data['elongation']:.1f}mm)")
        elif sensor_data['elongation'] > self.thresholds['elongation']['warning']:
            warning_issues.append(f"Elongation elevated ({sensor_data['elongation']:.1f}mm)")
        
        # Check load weight (higher is worse)
        if sensor_data['load_weight'] > self.thresholds['load_weight']['critical']:
            critical_issues.append(f"Load weight critically high ({sensor_data['load_weight']:.1f}kg)")
        elif sensor_data['load_weight'] > self.thresholds['load_weight']['warning']:
            warning_issues.append(f"Load weight elevated ({sensor_data['load_weight']:.1f}kg)")
        
        # Determine final status
        if critical_issues:
            status = "Critical"
            reason = " | ".join(critical_issues)
            confidence = 0.95
            triggered_metrics = [issue.split()[0] for issue in critical_issues]
        elif warning_issues:
            status = "Warning"
            reason = " | ".join(warning_issues)
            confidence = 0.85
            triggered_metrics = [issue.split()[0] for issue in warning_issues]
        else:
            status = "Healthy"
            reason = "All metrics within safe operating range"
            confidence = 0.90
            triggered_metrics = []
        
        return status, confidence, reason, triggered_metrics
    
    def get_risk_score(self, sensor_data: Dict) -> float:
        """
        Calculate overall risk score (0-100)
        100 = maximum risk, 0 = no risk
        """
        risk_score = 0
        
        # Tension risk (inverted - lower is riskier)
        tension_risk = max(0, (100 - sensor_data['tension']) / 100 * 20)
        risk_score += tension_risk
        
        # Vibration risk
        vibration_risk = min(sensor_data['vibration'] / 25 * 15, 15)
        risk_score += vibration_risk
        
        # Wear risk
        wear_risk = sensor_data['wear'] / 100 * 25
        risk_score += wear_risk
        
        # Temperature risk
        temp_risk = min(sensor_data['temperature'] / 60 * 10, 10)
        risk_score += temp_risk
        
        # Corrosion risk
        corrosion_risk = sensor_data['corrosion_level'] / 100 * 15
        risk_score += corrosion_risk
        
        # Elongation risk
        elongation_risk = min(sensor_data['elongation'] / 10 * 10, 10)
        risk_score += elongation_risk
        
        # Diameter risk (inverted)
        diameter_risk = max(0, (13.5 - sensor_data['rope_diameter']) * 5)
        risk_score += diameter_risk
        
        return min(risk_score, 100)
    
    def predict_remaining_life(self, sensor_data: Dict, load_cycles: int) -> Dict:
        """
        Predict remaining useful life of the rope
        
        Returns:
            - estimated_days: Estimated days until replacement needed
            - confidence: Confidence in prediction
        """
        # Simple heuristic model (can be replaced with ML later)
        base_life = 50000  # Base load cycles for a rope
        
        # Adjust based on current wear
        wear_factor = (100 - sensor_data['wear']) / 100
        
        # Adjust based on corrosion
        corrosion_factor = (100 - sensor_data['corrosion_level']) / 100
        
        # Adjust based on temperature abuse
        temp_factor = max(0.5, (60 - sensor_data['temperature']) / 60)
        
        # Calculate remaining cycles
        adjusted_life = base_life * wear_factor * corrosion_factor * temp_factor
        remaining_cycles = max(0, adjusted_life - load_cycles)
        
        # Assume average 100 cycles per day
        cycles_per_day = 100
        estimated_days = int(remaining_cycles / cycles_per_day)
        
        # Calculate confidence based on data quality
        confidence = 0.75 if estimated_days > 30 else 0.60
        
        return {
            "estimated_days": estimated_days,
            "estimated_cycles": int(remaining_cycles),
            "confidence": confidence,
            "recommendation": self._get_maintenance_recommendation(estimated_days)
        }
    
    def calculate_cost_savings(self, sensor_data: Dict, status: str) -> Dict:
        """
        Calculate cost savings from predictive maintenance
        
        Returns detailed breakdown of costs avoided
        """
        savings = {
            "total_savings": 0,
            "breakdown": {},
            "comparison": {},
            "roi_percentage": 0
        }
        
        if status == "Critical":
            # By catching critical issues early, we avoid emergency breakdown
            emergency_cost = (
                self.costs['rope_replacement'] +
                self.costs['emergency_response'] +
                (self.costs['emergency_downtime_per_hour'] * self.costs['average_emergency_downtime_hours'])
            )
            
            planned_cost = self.costs['planned_replacement'] + self.costs['preventive_inspection']
            
            savings['total_savings'] = emergency_cost - planned_cost
            savings['breakdown'] = {
                "avoided_emergency_replacement": self.costs['rope_replacement'],
                "avoided_emergency_callout": self.costs['emergency_response'],
                "avoided_downtime_cost": self.costs['emergency_downtime_per_hour'] * self.costs['average_emergency_downtime_hours'],
                "planned_replacement_cost": -self.costs['planned_replacement'],
                "inspection_cost": -self.costs['preventive_inspection']
            }
            savings['comparison'] = {
                "reactive_maintenance_cost": emergency_cost,
                "predictive_maintenance_cost": planned_cost
            }
            savings['roi_percentage'] = round((savings['total_savings'] / planned_cost) * 100, 2)
            
        elif status == "Warning":
            # By catching warning signs, we prevent escalation to critical
            potential_emergency_cost = (
                self.costs['rope_replacement'] +
                self.costs['emergency_response'] +
                (self.costs['emergency_downtime_per_hour'] * self.costs['average_emergency_downtime_hours'])
            )
            
            preventive_cost = self.costs['preventive_inspection']
            
            # Assume 60% chance warning would escalate to emergency without intervention
            savings['total_savings'] = int((potential_emergency_cost - preventive_cost) * 0.6)
            savings['breakdown'] = {
                "potential_avoided_costs": potential_emergency_cost,
                "preventive_action_cost": -preventive_cost,
                "probability_factor": 0.6
            }
            savings['comparison'] = {
                "potential_reactive_cost": potential_emergency_cost,
                "predictive_maintenance_cost": preventive_cost
            }
            savings['roi_percentage'] = round((savings['total_savings'] / preventive_cost) * 100, 2)
            
        else:  # Healthy
            # Continuous monitoring prevents unexpected failures
            annual_monitoring_cost = self.costs['preventive_inspection'] * 4  # Quarterly
            annual_avoided_emergency = self.costs['rope_replacement'] * 0.2  # 20% chance of unexpected failure
            
            savings['total_savings'] = int(annual_avoided_emergency - annual_monitoring_cost)
            savings['breakdown'] = {
                "annual_monitoring_cost": -annual_monitoring_cost,
                "estimated_avoided_emergency_cost": annual_avoided_emergency
            }
            savings['roi_percentage'] = round((savings['total_savings'] / annual_monitoring_cost) * 100, 2) if annual_monitoring_cost > 0 else 0
        
        return savings
    
    def _get_maintenance_recommendation(self, days_remaining: int) -> str:
        """Get maintenance recommendation based on remaining life"""
        if days_remaining < 7:
            return "URGENT: Schedule immediate rope replacement"
        elif days_remaining < 30:
            return "Schedule rope replacement within this month"
        elif days_remaining < 90:
            return "Plan rope replacement in next quarter"
        else:
            return "Continue routine monitoring"


class FleetAnalytics:
    """Analytics for multiple elevators across buildings"""
    
    def __init__(self):
        self.classifier = RopeHealthClassifier()
    
    def analyze_fleet(self, elevator_data_list: List[Dict]) -> Dict:
        """
        Analyze health of entire elevator fleet
        
        Args:
            elevator_data_list: List of dicts with 'elevator_id' and sensor data
        
        Returns:
            Fleet-wide analytics and rankings
        """
        fleet_results = []
        total_savings = 0
        
        for elevator in elevator_data_list:
            status, confidence, reason, triggered = self.classifier.classify(elevator)
            risk_score = self.classifier.get_risk_score(elevator)
            savings_data = self.classifier.calculate_cost_savings(elevator, status)
            
            fleet_results.append({
                "elevator_id": elevator.get('elevator_id', 'Unknown'),
                "status": status,
                "risk_score": risk_score,
                "confidence": confidence,
                "reason": reason,
                "potential_savings": savings_data['total_savings']
            })
            
            total_savings += savings_data['total_savings']
        
        # Sort by risk score (highest first)
        fleet_results.sort(key=lambda x: x['risk_score'], reverse=True)
        
        # Calculate fleet statistics
        total = len(fleet_results)
        critical_count = sum(1 for e in fleet_results if e['status'] == 'Critical')
        warning_count = sum(1 for e in fleet_results if e['status'] == 'Warning')
        healthy_count = sum(1 for e in fleet_results if e['status'] == 'Healthy')
        
        avg_risk = sum(e['risk_score'] for e in fleet_results) / total if total > 0 else 0
        
        return {
            "total_elevators": total,
            "status_breakdown": {
                "critical": critical_count,
                "warning": warning_count,
                "healthy": healthy_count
            },
            "average_risk_score": round(avg_risk, 2),
            "highest_risk_elevators": fleet_results[:5],  # Top 5 at-risk
            "fleet_health_percentage": round((healthy_count / total * 100), 2) if total > 0 else 0,
            "total_estimated_savings": round(total_savings, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def compare_buildings(self, buildings_data: Dict[str, List[Dict]]) -> Dict:
        """
        Compare health across multiple buildings
        
        Args:
            buildings_data: Dict with building_name as key, list of elevator data as value
        
        Returns:
            Comparison metrics across buildings
        """
        building_summaries = []
        
        for building_name, elevators in buildings_data.items():
            fleet_analysis = self.analyze_fleet(elevators)
            
            building_summaries.append({
                "building_name": building_name,
                "total_elevators": fleet_analysis['total_elevators'],
                "average_risk": fleet_analysis['average_risk_score'],
                "health_percentage": fleet_analysis['fleet_health_percentage'],
                "critical_count": fleet_analysis['status_breakdown']['critical'],
                "estimated_savings": fleet_analysis['total_estimated_savings']
            })
        
        # Sort by health percentage (best first)
        building_summaries.sort(key=lambda x: x['health_percentage'], reverse=True)
        
        return {
            "buildings": building_summaries,
            "best_performing": building_summaries[0]['building_name'] if building_summaries else None,
            "needs_attention": [b['building_name'] for b in building_summaries if b['critical_count'] > 0],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def generate_maintenance_priority_list(self, elevator_data_list: List[Dict]) -> List[Dict]:
        """
        Generate prioritized maintenance list
        
        Returns list sorted by urgency
        """
        priority_list = []
        
        for elevator in elevator_data_list:
            status, confidence, reason, triggered = self.classifier.classify(elevator)
            risk_score = self.classifier.get_risk_score(elevator)
            remaining_life = self.classifier.predict_remaining_life(elevator, elevator['load_cycles'])
            
            # Calculate priority score (0-100, higher = more urgent)
            priority_score = risk_score
            
            # Boost priority if days remaining is low
            if remaining_life['estimated_days'] < 7:
                priority_score = min(priority_score + 30, 100)
            elif remaining_life['estimated_days'] < 30:
                priority_score = min(priority_score + 15, 100)
            
            priority_list.append({
                "elevator_id": elevator.get('elevator_id', 'Unknown'),
                "priority_score": round(priority_score, 2),
                "status": status,
                "risk_score": risk_score,
                "days_remaining": remaining_life['estimated_days'],
                "recommendation": remaining_life['recommendation'],
                "reason": reason
            })
        
        # Sort by priority score (highest first)
        priority_list.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return priority_list


# Singleton instances
classifier = RopeHealthClassifier()
fleet_analytics = FleetAnalytics()


def classify_rope_health(sensor_data: Dict) -> Dict:
    """
    Main function to classify rope health
    
    Args:
        sensor_data: Dictionary with sensor readings
    
    Returns:
        Dictionary with status, confidence, reason, risk_score, and prediction
    """
    status, confidence, reason, triggered_metrics = classifier.classify(sensor_data)
    risk_score = classifier.get_risk_score(sensor_data)
    remaining_life = classifier.predict_remaining_life(sensor_data, sensor_data['load_cycles'])
    cost_savings = classifier.calculate_cost_savings(sensor_data, status)
    
    return {
        "status": status,
        "confidence": confidence,
        "reason": reason,
        "triggered_metrics": triggered_metrics,
        "risk_score": round(risk_score, 2),
        "remaining_life": remaining_life,
        "cost_savings": cost_savings,
        "timestamp": datetime.utcnow().isoformat()
    }


def analyze_fleet(elevator_data_list: List[Dict]) -> Dict:
    """
    Analyze entire fleet of elevators
    
    Args:
        elevator_data_list: List of sensor data dicts with elevator_id
    
    Returns:
        Fleet-wide analytics
    """
    return fleet_analytics.analyze_fleet(elevator_data_list)


def get_maintenance_priorities(elevator_data_list: List[Dict]) -> List[Dict]:
    """
    Get prioritized maintenance list
    
    Args:
        elevator_data_list: List of sensor data dicts
    
    Returns:
        Sorted list by maintenance priority
    """
    return fleet_analytics.generate_maintenance_priority_list(elevator_data_list)


def compare_buildings(buildings_data: Dict[str, List[Dict]]) -> Dict:
    """
    Compare elevator health across buildings
    
    Args:
        buildings_data: Dict with building names as keys
    
    Returns:
        Building comparison metrics
    """
    return fleet_analytics.compare_buildings(buildings_data)


def calculate_roi_report(elevator_data_list: List[Dict]) -> Dict:
    """
    Generate comprehensive ROI report for fleet
    
    Args:
        elevator_data_list: List of sensor data dicts
    
    Returns:
        Comprehensive ROI and savings report
    """
    total_savings = 0
    total_investment = 0
    breakdown_by_status = {"Critical": 0, "Warning": 0, "Healthy": 0}
    
    for elevator in elevator_data_list:
        status, _, _, _ = classifier.classify(elevator)
        savings = classifier.calculate_cost_savings(elevator, status)
        
        total_savings += savings['total_savings']
        breakdown_by_status[status] += savings['total_savings']
        
        # Investment is the predictive maintenance cost
        if status == "Critical":
            total_investment += (classifier.costs['planned_replacement'] + 
                               classifier.costs['preventive_inspection'])
        elif status == "Warning":
            total_investment += classifier.costs['preventive_inspection']
        else:
            total_investment += classifier.costs['preventive_inspection'] * 4 / 12  # Monthly portion
    
    overall_roi = round((total_savings / total_investment * 100), 2) if total_investment > 0 else 0
    
    return {
        "total_savings": round(total_savings, 2),
        "total_investment": round(total_investment, 2),
        "net_benefit": round(total_savings - total_investment, 2),
        "overall_roi_percentage": overall_roi,
        "savings_by_status": {k: round(v, 2) for k, v in breakdown_by_status.items()},
        "elevators_analyzed": len(elevator_data_list),
        "average_savings_per_elevator": round(total_savings / len(elevator_data_list), 2) if elevator_data_list else 0,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============ QUICK TEST ============
if __name__ == "__main__":
    print("🧪 Testing ML Model with Enhanced Features\n")
    print("=" * 60)
    
    # Test 1: Single Elevator - Healthy
    print("\n1️⃣ Testing HEALTHY Elevator:")
    print("-" * 60)
    healthy_data = {
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
    
    result = classify_rope_health(healthy_data)
    print(f"   Status: {result['status']}")
    print(f"   Risk Score: {result['risk_score']}/100")
    print(f"   Reason: {result['reason']}")
    print(f"   Remaining Life: {result['remaining_life']['estimated_days']} days")
    print(f"   Recommendation: {result['remaining_life']['recommendation']}")
    print(f"   💰 Potential Savings: ₹{result['cost_savings']['total_savings']:,.2f}")
    print(f"   📊 ROI: {result['cost_savings']['roi_percentage']}%")
    
    # Test 2: Single Elevator - Critical
    print("\n2️⃣ Testing CRITICAL Elevator:")
    print("-" * 60)
    critical_data = {
        "elevator_id": "ELEV-002",
        "tension": 82.0,
        "vibration": 22.0,
        "wear": 80.0,
        "load_cycles": 45000,
        "temperature": 52.0,
        "rope_diameter": 11.5,
        "corrosion_level": 45.0,
        "elongation": 5.5,
        "load_weight": 780.0
    }
    
    result = classify_rope_health(critical_data)
    print(f"   Status: {result['status']}")
    print(f"   Risk Score: {result['risk_score']}/100")
    print(f"   Reason: {result['reason'][:100]}...")
    print(f"   Remaining Life: {result['remaining_life']['estimated_days']} days")
    print(f"   Recommendation: {result['remaining_life']['recommendation']}")
    print(f"   💰 Total Savings: ₹{result['cost_savings']['total_savings']:,.2f}")
    print(f"   📊 ROI: {result['cost_savings']['roi_percentage']}%")
    print(f"   Reactive Cost: ₹{result['cost_savings']['comparison']['reactive_maintenance_cost']:,.2f}")
    print(f"   Predictive Cost: ₹{result['cost_savings']['comparison']['predictive_maintenance_cost']:,.2f}")
    
    # Test 3: Fleet Analysis
    print("\n3️⃣ Testing FLEET ANALYTICS:")
    print("-" * 60)
    
    fleet_data = [
        {**healthy_data, "elevator_id": "ELEV-001"},
        {**critical_data, "elevator_id": "ELEV-002"},
        {
            "elevator_id": "ELEV-003",
            "tension": 88.0,
            "vibration": 16.5,
            "wear": 55.0,
            "load_cycles": 25000,
            "temperature": 42.0,
            "rope_diameter": 12.3,
            "corrosion_level": 25.0,
            "elongation": 3.5,
            "load_weight": 620.0
        },
        {
            "elevator_id": "ELEV-004",
            "tension": 97.0,
            "vibration": 10.2,
            "wear": 30.0,
            "load_cycles": 5000,
            "temperature": 28.0,
            "rope_diameter": 13.0,
            "corrosion_level": 8.0,
            "elongation": 1.5,
            "load_weight": 380.0
        }
    ]
    
    fleet_analysis = analyze_fleet(fleet_data)
    print(f"   Total Elevators: {fleet_analysis['total_elevators']}")
    print(f"   Status Breakdown:")
    print(f"      - Critical: {fleet_analysis['status_breakdown']['critical']}")
    print(f"      - Warning: {fleet_analysis['status_breakdown']['warning']}")
    print(f"      - Healthy: {fleet_analysis['status_breakdown']['healthy']}")
    print(f"   Average Risk Score: {fleet_analysis['average_risk_score']}/100")
    print(f"   Fleet Health: {fleet_analysis['fleet_health_percentage']}%")
    print(f"   💰 Total Estimated Savings: ₹{fleet_analysis['total_estimated_savings']:,.2f}")
    print(f"\n   🚨 Highest Risk Elevators:")
    for i, elev in enumerate(fleet_analysis['highest_risk_elevators'][:3], 1):
        print(f"      {i}. {elev['elevator_id']} - Risk: {elev['risk_score']}/100 ({elev['status']})")
    
    # Test 4: Maintenance Priority List
    print("\n4️⃣ Testing MAINTENANCE PRIORITY LIST:")
    print("-" * 60)
    priorities = get_maintenance_priorities(fleet_data)
    for i, item in enumerate(priorities, 1):
        print(f"   {i}. {item['elevator_id']} - Priority: {item['priority_score']}/100")
        print(f"      Status: {item['status']} | Days Remaining: {item['days_remaining']}")
        print(f"      Action: {item['recommendation']}")
    
    # Test 5: ROI Report
    print("\n5️⃣ Testing ROI REPORT:")
    print("-" * 60)
    roi_report = calculate_roi_report(fleet_data)
    print(f"   💰 Total Savings: ₹{roi_report['total_savings']:,.2f}")
    print(f"   💸 Total Investment: ₹{roi_report['total_investment']:,.2f}")
    print(f"   ✅ Net Benefit: ₹{roi_report['net_benefit']:,.2f}")
    print(f"   📊 Overall ROI: {roi_report['overall_roi_percentage']}%")
    print(f"   📈 Avg Savings/Elevator: ₹{roi_report['average_savings_per_elevator']:,.2f}")
    
    print("\n" + "=" * 60)
    print("✅ All ML model tests completed successfully!")
    print("=" * 60)

