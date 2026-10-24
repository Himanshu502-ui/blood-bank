# Blood Bank and Donor Management System

A beginner-friendly DBMS assignment using **Python Flask + MySQL + HTML/CSS**.

## Features
- Dashboard summary: registered donors, recorded donations, pending requests and total stock
- Register and view donors
- Record a donation and automatically add its units to the matching blood group stock
- Submit blood requests and update request status
- View blood stock by blood group
- Relational schema with primary keys, foreign keys, unique constraints and check constraints

> This is an educational demo. It is not a clinical inventory or donor eligibility system. Donation quantities and donor eligibility must be verified by qualified blood-bank staff in real use.

## Requirements
- Python 3.10+
- MySQL Server
- MySQL Workbench (recommended)
- VS Code (recommended)

## Setup

### 1. Create the database
1. Open MySQL Workbench and connect to your local MySQL server.
2. Open `schema.sql`.
3. Run the whole script. It creates `blood_bank_db`, the four tables and the eight blood-group stock rows.

### 2. Install Python packages
Open a terminal inside this project folder:

```bash
python -m venv venv
```

Windows PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

Then run:
```bash
pip install -r requirements.txt
```

### 3. Set your MySQL password
Open `app.py` and replace `YOUR_MYSQL_PASSWORD` with your MySQL `root` password. If your MySQL username is not `root`, change that too.

### 4. Run the app
```bash
python app.py
```
Open the local address printed in the terminal, usually `http://127.0.0.1:5000`.

## Suggested demo order
1. Add a donor.
2. Open Donations and record a donation for that donor.
3. Open Stock and show that the matching blood group stock increased.
4. Submit a blood request.
5. Change its status from Pending to Approved/Fulfilled.
6. Return to Dashboard and show the updated counts.

## DBMS concepts to explain in viva
- **Primary key:** uniquely identifies each donor, donation and request.
- **Foreign key:** `donations.donor_id` references `donors.donor_id`.
- **UNIQUE:** prevents duplicate donor phone numbers.
- **CHECK:** limits demo donor ages to 18–65 and units to positive values.
- **JOIN:** donation history displays donor name and blood group by joining `donations` and `donors`.
- **Aggregate functions:** `COUNT()` and `SUM()` power the dashboard.
- **Normalization:** donor details are stored once in `donors`; donation events are stored separately in `donations`, reducing duplication.
- **Transaction:** recording a donation and updating stock are committed together.

## Main tables
- `donors`: donor personal/contact information
- `blood_stock`: current demo stock for each blood group
- `donations`: donation history linked to a donor
- `blood_requests`: requests and their status

## Important limitations
This classroom demo does not implement login, role-based access, medical screening, blood component/expiry tracking, compatibility rules, or automatic stock deduction on fulfilment. Do not use real personal or medical data.
