Movie & Cinema Management System 🎬
Final Project for the Database Management Systems course - A comprehensive cinema operation system integrated with advanced data analytics.

📌 Project Overview
This system is designed to manage the operational workflows of a modern cinema, ranging from ticket booking and screening management to financial reporting. The project emphasizes data integrity (3NF), Security through Role-Based Access Control (RBAC), and high-performance data processing using Python and Pandas.

📂 Project Structure
Plaintext
movie-cinema-system/
├── sql/
│   ├── schema.sql             # Table structures and constraints (3NF)
│   ├── sample_data.sql        # Mock data for testing (>500 records)
│   ├── advanced_objects.sql   # Triggers, Procedures, Functions, and Views
│   └── security_setup.sql     # User creation & Role-Based Access Control (RBAC)
├── python/
│   ├── app.py                 # Main CLI/Streamlit application entry point
│   ├── database_conn.py       # MySQL connection wrapper
│   ├── requirements.txt       # Project dependencies
│   └── modules/               # Core business logic modules
├── scripts/
│   └── auto_backup.py         # Automated database dump script (DevOps)
├── backups/                   # Directory for time-stamped .sql backups
├── report/                    # LaTeX documentation and visual assets
├── .gitignore                 # Excludes artifacts (venv, __pycache__)
└── README.md                  # Project documentation
🛠 Setup Instructions
1. Database Initialization (MySQL)
Open MySQL Workbench or your preferred terminal and execute the SQL scripts in the following order:

sql/schema.sql

sql/advanced_objects.sql

sql/sample_data.sql

sql/security_setup.sql

2. Python Environment Setup
Bash
# Navigate to the python directory
cd python

# Install required dependencies
pip install -r requirements.txt
3. Configuration
Update the host, user, and password credentials in python/database_conn.py to match your local MySQL environment.

🚀 Key Features
🔐 Role-Based Access Control (RBAC)
Access is segmented into three primary tiers to ensure system security:

Admin: Full administrative privileges for total system control.

Ticket Clerk: Restricted to booking tickets, checking seat availability, and customer management.

Reporter: Read-only access specifically for generating financial and occupancy analytics.

⚡ Data Science Optimization
Memory Efficiency: Implements Pandas downcasting techniques to minimize RAM usage during large-scale data ingestion.

High-Speed Storage: Supports data exportation to Parquet format, offering superior compression and faster I/O compared to standard CSV.

🛡 System Administration (DevOps)
Automated Backups: The scripts/auto_backup.py utility automates point-in-time database dumps and enables GitHub synchronization, ensuring 99.9% data survivability.

📈 Backup Workflow
To trigger a manual database backup, execute:

Bash
python scripts/auto_backup.py
The script automatically generates a time-stamped .sql file within the backups/ directory.

✍️ Author
Full Name: Nguyen Thi Hai Yen

Institution: National Economics University (NEU)

Faculty: Faculty of Data Science and Artificial Intelligence (DS&AI)# MOVIE AND CINEMA ROOM MANAGEMENT SYSTEM

