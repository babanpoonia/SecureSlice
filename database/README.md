# Database – SecureSlice

This folder holds all database-related files and schemas used in SecureSlice for logging attack data and detection results.

## Technologies Used:
- PostgreSQL
- SQLAlchemy (ORM used in Flask backend)

## Tables:
- `AttackLogs` – Records all simulated attacks (method, timestamp, threat level)
- `DetectionEvents` – Stores detected anomalies and AI output
- `SystemStatus` – Logs system uptime, downtime, and network state
