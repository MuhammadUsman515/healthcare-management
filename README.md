# Healthcare Management System (Enterprise)

A comprehensive, enterprise-grade Healthcare Management System built on **Frappe Framework**, designed for multi-branch hospital operations with full clinical, laboratory, pharmacy, revenue, welfare, and portal modules.

## Architecture — 6 Apps

| App | Module | Description |
|-----|--------|-------------|
| **hms_core** | HMS Core | Shared masters, company, branches, departments, insurance providers, audit, notifications |
| **hms_clinical** | HMS Clinical | OPD, IPD, EMR, encounters, prescriptions, nursing, procedures, admission/discharge |
| **hms_lis** | HMS LIS | Lab ordering, sample collection, 3-stage result authorization, machine interfacing, portal release |
| **hms_pharmacy** | HMS Pharmacy | Drug inventory, formulary, dispensing, POS, batch/expiry, controlled stock, safety checks |
| **hms_revenue** | HMS Revenue | Billing, packages, insurance/TPA claims, welfare committee, donations, subsidy ledger |
| **hms_portal** | HMS Portal | Patient portal, lab report portal, appointment booking, donation page, corporate/insurance panels |

## Key Features

### Clinical
- Enterprise Patient with duplicate detection, CNIC, VIP/medico-legal flags, insurance mapping
- SOAP-format Encounter (Subjective/Objective/Assessment/Plan)
- Prescription with child table items, pharmacy workflow
- Vital Signs with auto BMI/BSA, critical range alerts
- IPD with bed management, transfer, discharge summary, billing clearance
- Nursing tasks, medication administration records, handover logs

### Laboratory (LIS)
- **3-Stage Result Authorization**: Entered → Verified → Authorized → Released
- Critical value alerts with real-time notifications
- TAT tracking and breach alerts
- Sample collection with barcode, rejection handling
- Patient portal result release control

### Pharmacy
- Drug item management with batch, expiry, controlled drug tracking
- Prescription → Dispense → POS Invoice (3 separate documents)
- Safety checks: drug interactions, allergy alerts, duplicate drug detection
- Stock management with reorder alerts

### Revenue & Billing
- Encounter/Admission charge sheets → Final Bill
- Insurance pre-authorization and claim lifecycle
- Deposit/advance management
- Package enrollment and consumption tracking

### Welfare & Donations
- Full welfare case workflow: Application → Documents → Social Assessment → Committee Review → Approval
- Donation receipt with fund restriction (Zakat/Sadaqah/General)
- Fund-wise balance tracking and utilization reporting
- Patient subsidy ledger

### Portal
- Patient portal: appointments, lab results, prescriptions, invoices, welfare status
- Public appointment booking and doctor search
- Lab report verification (mobile + DOB)
- Donation page
- Corporate and insurance partner panels

## Workflows

| Workflow | States |
|----------|--------|
| Appointment | Scheduled → Checked In → In Consultation → Completed / Cancelled / No Show |
| Encounter | Draft → Under Review → Signed → Closed |
| Prescription | Draft → Signed → Sent to Pharmacy → Partially/Fully Dispensed |
| Lab Test | Ordered → Sample Collected → In Process → Result Entered → Verified → Authorized → Released |
| Admission | Admitted → Transferred → Discharge Initiated → Billing Clearance → Discharged / LAMA |
| Welfare Case | Draft → Submitted → Documents Verified → Social Assessment → Committee Review → Approved → Applied |
| Insurance Claim | Draft → Preauth → Approved → Submitted → Under Review → Settled / Denied → Reconciled |

## Desk Pages (Custom UI)

- `/app/queue-board` — Live patient queue board
- `/app/bed-board` — Ward-wise bed occupancy board
- `/app/lab-workbench` — Lab tech workstation with live stats
- `/app/pharmacy-dispense-console` — Prescription queue and dispensing

## Workspaces (8 Role-Based Panels)

Reception | Doctor | Nurse Station | Laboratory | Pharmacy | Cashier | Welfare | Executive Dashboard

## Reports

- Daily Registration Summary, Appointment Load by Doctor, Bed Occupancy
- Lab TAT, Critical Values, Sample Rejection Rate
- Daily Revenue Collection, Outstanding Receivables, Donation Utilization
- Welfare Case Aging, Fund Balance

## Print Formats

- Patient Registration Slip
- Prescription Print
- Lab Report Print
- Final Bill Print
- Donation Receipt Print

## Roles (12 Enterprise Roles)

| Role | Access Level |
|------|-------------|
| Healthcare Administrator | Full system access |
| Hospital Admin | Branch-level admin |
| Branch Admin | Single branch management |
| Physician | Clinical records, encounters, prescriptions |
| Nurse | Vitals, nursing tasks, admissions |
| Lab Technician | Sample collection, result entry |
| Lab Supervisor | Result verification, authorization |
| Pharmacist | Dispensing, drug management, POS |
| Cashier | Billing, receipts, payments |
| Welfare Officer | Welfare cases, donations |
| Welfare Committee | Approval authority |
| Auditor | Read-only audit access |

## API Endpoints

```
GET /api/method/hms_clinical.hms_clinical.api.patient_history.get_patient_history
GET /api/method/hms_clinical.hms_clinical.api.patient_history.get_dashboard_stats
GET /api/method/hms_portal.hms_portal.api.portal.get_my_appointments
GET /api/method/hms_portal.hms_portal.api.portal.get_my_lab_results
GET /api/method/hms_portal.hms_portal.api.portal.get_my_prescriptions
GET /api/method/hms_portal.hms_portal.api.portal.get_my_invoices
POST /api/method/hms_portal.hms_portal.api.portal.book_appointment
POST /api/method/hms_portal.hms_portal.api.portal.verify_lab_report (guest)
GET /api/method/hms_core.hms_core.api.utils.get_active_branches
GET /api/method/hms_core.hms_core.api.utils.get_departments
GET /api/method/hms_pharmacy.hms_pharmacy.api.safety.check_stock_availability
```

## Installation

### Prerequisites
- Python 3.10+
- Frappe Bench (v15+)
- MariaDB / PostgreSQL
- Redis
- Node.js 18+

### Setup

```bash
# Get all apps
bench get-app hms_core https://github.com/muhammadusman515/healthcare-management.git --branch claude/explore-frappe-erpnext-Q6x6u

# Install apps in order
bench --site your-site install-app hms_core
bench --site your-site install-app hms_clinical
bench --site your-site install-app hms_lis
bench --site your-site install-app hms_pharmacy
bench --site your-site install-app hms_revenue
bench --site your-site install-app hms_portal

# Migrate
bench --site your-site migrate
bench start
```

## Build Phases

1. **Phase 1**: Patient, Appointment, Encounter, Prescription, Portal skeleton
2. **Phase 2**: LIS (Lab ordering → authorization → portal release)
3. **Phase 3**: Pharmacy + POS
4. **Phase 4**: IPD + Nursing
5. **Phase 5**: Revenue + Insurance + Welfare
6. **Phase 6**: Executive Analytics + Audit hardening

## License

MIT
