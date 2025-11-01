YANTROG: Intelligent Elevator Monitoring Dashboard
An advanced, real-time elevator shaft monitoring system designed for safety, analytics, and predictive maintenance. The solution uses a modern web-dashboard to visualize sensor data, fleet status, alerts, and technician actions.

Software Overview
YANTROG is a web application built using:

HTML & CSS: Responsive, visually aesthetic UI with clean gradients and Poppins font for readability.
JavaScript: Core logic for data visualization, interactivity, and API integration.
Chart.js: Dynamic charts for live sensor data and trend analytics.
Font Awesome: Iconography for clear, intuitive navigation.
html2pdf.js: Enables PDF generation for on-demand report creation.
Authentication Logic: Demo login with admin/admin123 credentials for private dashboard access.

Key Features
Dashboard: Central hub displaying live elevator fleet analytics, including condition indices, real-time alerts, and statuses.
Alerts Table: Grouped view of safety events (vibration, gas, temperature, overload, intrusion, etc.).
Technician Section: Track technician interventions, view leaderboard, and management assignments.
Analytics: ROI, cost savings, downtime avoidance, and other operational KPIs.
PDF Report: Generate snapshot reports for audits or presentations.
Expandable API Integration: Simple integration with any backend (FastAPI, Flask, Node.js) by setting the APIBASE variable.

Software Workflow
Sensor Data Collection: Microcontroller (ESP32) collects data from vibration, gas, temperature, load, ultrasonic, and camera modules.
Data Transmission: Sensor readings can be sent to backend in JSON format via REST API.
Dashboard Visualization: Frontend receives API data, updates charts, stats, and alert logs automatically.
Event Handling: Triggers and logs alerts for threshold breaches and technician activities.
Reporting: Users can export dashboards and logs as PDF reports for further review.

Getting Started
Clone the Repository
git clone https://github.com/HACKWAVE2025/B16.git

To connect live hardware, implement a backend API accepting sensor data at /api/sensordata or customize the endpoint.

Future Integrations
Cloud Storage & Analytics
Real-time Notifications/Alerts
Advanced Machine Learning for Fault Prediction
Mobile Dashboard Extension

Hardware (Summary)
ESP32 Dev Module or ESP32-CAM (Wi-Fi + Camera)
Sensors: SW420 vibration, MQ2 gas, LM35 temperature, HX711 load cell, HC-SR04 ultrasonic
Prototype setup: Breadboard, jumpers, Li-ion power supply

Note: Hardware integration demo code is provided separately; main focus is on software dashboard and analytics.

License
Open source under MIT License.

Contact
For queries, contributions, or collaboration, raise Issues or contact the repository owner.

