# Healthcare Management System

A comprehensive healthcare management application built on the **Frappe Framework / ERPNext** platform.

## Features

### DocTypes (Modules)

| DocType | Description |
|---------|-------------|
| **Patient** | Patient registration with demographics, contact info, and medical history |
| **Practitioner** | Doctor/physician profiles with specialization and license details |
| **Appointment** | Schedule and manage patient appointments with duplicate detection |
| **Vital Signs** | Record patient vitals - BP, heart rate, temperature, SpO2, BMI calculation |
| **Lab Test** | Order and track lab tests with results and critical alerts |
| **Prescription** | Manage medication prescriptions with dosage and frequency |
| **Clinical Procedure** | Track clinical procedures with outcomes and follow-ups |
| **Medical Department** | Define hospital departments |

### Key Capabilities

- **Auto-naming**: All records use healthcare-specific naming series (HLC-PAT, HLC-APT, etc.)
- **Smart Validations**: Duplicate appointment detection, vital signs range warnings, critical lab alerts
- **BMI Auto-calculation**: Automatically computed from height and weight
- **Patient History API**: Single endpoint to fetch complete patient medical history
- **Dashboard Stats API**: Get real-time statistics for the healthcare dashboard
- **Submittable Workflows**: Lab Tests, Prescriptions, Vital Signs, and Clinical Procedures support submit/cancel workflow

## Installation

### Prerequisites

- Python 3.10+
- Frappe Bench (v15+)
- MariaDB / PostgreSQL
- Redis
- Node.js 18+

### Setup

```bash
# Get the app
bench get-app healthcare https://github.com/muhammadusman515/healthcare-management.git

# Install on your site
bench --site your-site.local install-app healthcare

# Run migrations
bench --site your-site.local migrate

# Start the development server
bench start
```

## API Endpoints

### Get Patient History
```
GET /api/method/healthcare.healthcare.api.get_patient_history
Params: patient (Patient ID)
```

### Get Dashboard Stats
```
GET /api/method/healthcare.healthcare.api.get_dashboard_stats
```

## Project Structure

```
healthcare/
├── healthcare/
│   ├── api/                    # Whitelisted API methods
│   ├── dashboard/              # Dashboard configuration
│   └── doctype/
│       ├── patient/            # Patient management
│       ├── practitioner/       # Doctor/physician profiles
│       ├── appointment/        # Appointment scheduling
│       ├── vital_signs/        # Patient vital signs
│       ├── lab_test/           # Lab test management
│       ├── prescription/       # Medication prescriptions
│       ├── clinical_procedure/ # Clinical procedures
│       └── medical_department/ # Department definitions
├── hooks.py                    # Frappe hooks configuration
├── modules.txt                 # Module registration
├── patches.txt                 # Migration patches
└── __init__.py
```

## Roles

- **Healthcare Administrator**: Full access to all DocTypes
- **Physician**: Read/write access to clinical records

## License

MIT
