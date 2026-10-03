# EVENT MANAGEMENT SYSTEM - College DBMS Project

A complete, modern, interactive full-stack web application designed for a College Database Management System (DBMS) practical project and viva demonstration.

---

## 🎯 Project Overview & Purpose

The **Event Management System** is engineered to manage events, organizers, venues, categories, participants, registrations, and payments in a centralized relational database.

It demonstrates practical DBMS principles:
- **Relational Tables & Schema Normalization (3NF)**
- **Primary Keys (`PK`) & Foreign Keys (`FK`)**
- **Referential Integrity & Cascading Constraints**
- **1:N and 1:1 Entity Cardinalities**
- **Two-Way Interaction**: SQL Database &harr; REST Backend API &harr; Interactive Frontend Web UI
- **Complex Multi-Table SQL Queries (INNER JOIN, LEFT JOIN, GROUP BY, HAVING, Subqueries)**
- **SQL Injection Prevention via Parameterized Queries**
- **Support for Both SQLite (Zero-Config Default) and Oracle Database (12c/19c/21c/23ai)**

---

## 🗄️ Relational Database Schema

The system implements the exact 7 normalized database tables required:

### 1. `Organizer`
- `Organizer_ID` (Primary Key, Auto-Increment)
- `Name` (VARCHAR(100), NOT NULL)
- `Email` (VARCHAR(100), UNIQUE, NOT NULL)
- `Phone` (VARCHAR(20), NOT NULL)

### 2. `Venue`
- `Venue_ID` (Primary Key, Auto-Increment)
- `Venue_Name` (VARCHAR(100), NOT NULL)
- `Location` (VARCHAR(200), NOT NULL)
- `Capacity` (INTEGER, CHECK `Capacity > 0`)

### 3. `Category`
- `Category_ID` (Primary Key, Auto-Increment)
- `Category_Name` (VARCHAR(100), UNIQUE, NOT NULL)
- `Description` (TEXT)

### 4. `Participant`
- `Participant_ID` (Primary Key, Auto-Increment)
- `Name` (VARCHAR(100), NOT NULL)
- `Email` (VARCHAR(100), UNIQUE, NOT NULL)
- `Phone` (VARCHAR(20), NOT NULL)

### 5. `Event` (Central Entity)
- `Event_ID` (Primary Key, Auto-Increment)
- `Event_Name` (VARCHAR(150), NOT NULL)
- `Date` (DATE, NOT NULL)
- `Time` (VARCHAR(10), NOT NULL)
- `Organizer_ID` (Foreign Key &rarr; `Organizer.Organizer_ID`)
- `Venue_ID` (Foreign Key &rarr; `Venue.Venue_ID`)
- `Category_ID` (Foreign Key &rarr; `Category.Category_ID`)

### 6. `Registration`
- `Registration_ID` (Primary Key, Auto-Increment)
- `Participant_ID` (Foreign Key &rarr; `Participant.Participant_ID`)
- `Event_ID` (Foreign Key &rarr; `Event.Event_ID`)
- `Registration_Date` (DATE, NOT NULL)
- `Status` (VARCHAR(20), CHECK `Status IN ('Confirmed', 'Pending', 'Cancelled')`)
- `UNIQUE (Participant_ID, Event_ID)` to disallow duplicate bookings.

### 7. `Payment`
- `Payment_ID` (Primary Key, Auto-Increment)
- `Registration_ID` (Foreign Key &rarr; `Registration.Registration_ID`, **UNIQUE** to enforce strict **1:1** cardinality)
- `Amount` (DECIMAL(10,2), CHECK `Amount >= 0`)
- `Payment_Date` (DATE, NOT NULL)
- `Payment_Status` (VARCHAR(20), CHECK `Payment_Status IN ('Completed', 'Pending', 'Failed', 'Refunded')`)

### Cardinality Summary:
- **Organizer 1 : N Event** (One organizer hosts many events)
- **Category 1 : N Event** (One category contains many events)
- **Venue 1 : N Event** (One venue hosts many events)
- **Event 1 : N Registration** (One event has many registered attendees)
- **Participant 1 : N Registration** (One participant can register for many events)
- **Registration 1 : 1 Payment** (Each registration is linked to exactly one payment record)

---

## 🚀 Quick Start Guide (Run Locally in VS Code)

### Prerequisites
- Python 3.10+ (Python 3.14+ supported)
- Windows / macOS / Linux

### Option 1: Instant Launch (Zero Configuration)
Simply double-click:
```cmd
run.bat
```
or run in PowerShell:
```powershell
.\run.ps1
```
The server will automatically:
1. Create the virtual environment (`.venv`)
2. Install dependencies (`pip install -r requirements.txt`)
3. Initialize the SQLite relational database (`database/event_management.db`)
4. Create all 7 tables and populate initial seed data
5. Launch the application at **`http://127.0.0.1:5000`** and open your browser!

---

### Option 2: Connecting to Oracle Database

To connect this application to an **Oracle Database** instance:

1. Open `.env` in the project root:
```ini
DB_TYPE=oracle

# Oracle Database Credentials
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=XEPDB1
ORACLE_SID=
ORACLE_USER=c##event_admin
ORACLE_PASSWORD=YourPasswordHere
```

2. Run the Oracle DDL & Seed scripts provided in:
   - `database/schema/schema_oracle.sql`
   - `database/seed/seed_oracle.sql`

3. Start the application:
```cmd
python run.py
```
The backend uses **`python-oracledb`** in pure thin mode (no Oracle Instant Client installation required).

---

## 🎓 Demonstrating to Your Professor / Evaluator

### 1. Two-Way Interaction (SQL &harr; Website)
This proves your system is connected to a real SQL database and not using static mock data:

**Direct SQL &rarr; Website:**
1. Open the website and navigate to **"Database Tables" &rarr; "Organizer"**.
2. Note the total count.
3. Open a Python or SQLite terminal:
   ```python
   import sqlite3
   conn = sqlite3.connect('database/event_management.db')
   conn.execute("INSERT INTO Organizer (Name, Email, Phone) VALUES ('Prof. Demonstration Host', 'demo@college.edu', '+1-555-8888')")
   conn.commit()
   conn.close()
   ```
4. Click the **"🔄 Refresh Data from SQL"** button on the website.
5. The record `'Prof. Demonstration Host'` appears instantly in the table!

**Website &rarr; Direct SQL:**
1. Click **"+ Add New Event"** on the website.
2. Enter an event (e.g. `"Campus Robotics Expo 2026"`), select an Organizer, Venue, and Category from the SQL dropdowns, and save.
3. Query the database directly via command line:
   ```python
   import sqlite3
   conn = sqlite3.connect('database/event_management.db')
   row = conn.execute("SELECT Event_ID, Event_Name, Date FROM Event WHERE Event_Name LIKE '%Robotics%'").fetchone()
   print(row)
   ```
4. Show your evaluator the newly inserted row in the real SQL file.

---

### 2. Foreign Key Constraint Enforcement
1. Go to the **Organizers** page.
2. Attempt to delete an organizer that has events scheduled (e.g., *TechNova Innovations*).
3. The system captures the relational constraint and shows a friendly explanation:
   > *"Cannot delete organizer 'TechNova Innovations' because events are associated with it."*
4. Explain how this enforces **Referential Integrity** and prevents orphaned child records.

---

### 3. Interactive ER Diagram & Schema Inspector
- Navigate to the **"ER Diagram"** page.
- Show the visual entity cards displaying primary keys (`PK`), foreign keys (`FK`), and cardinalities (`1:N`, `1:1`).
- Click on any entity (e.g., `Event` or `Payment`) to view its data types, constraints, and relational definitions.

---

### 4. Interactive SQL Console & Presets
- Navigate to the **"SQL Console"** page.
- Choose any of the 8 curated preset queries demonstrating:
  - 4-Table and 5-Table `INNER JOIN` & `LEFT JOIN`
  - `GROUP BY` with `HAVING` filters
  - `SUM()`, `COUNT()`, `AVG()` aggregations
  - Correlated and Uncorrelated Subqueries (`WHERE ... IN (...)`)
- Click **"▶ Run SQL Query"** to view real-time execution duration (e.g. `1.2 ms`) and table output.

---

### 5. Multi-Table SQL Reports with CSV Export
- Navigate to the **"SQL Reports"** page.
- View any of the 7 business reports:
  1. *Comprehensive Event & Attendance Report*
  2. *Participant Registration History*
  3. *Financial & Payment Reconciliation*
  4. *Organizer Performance Report*
  5. *Venue Usage & Capacity Utilization %*
  6. *Category-wise Event Breakdown*
  7. *Upcoming Scheduled Events*
- Click **"📥 Export to CSV"** or **"🖨️ Print Report"** to export formatted data.

---

## 📁 Project Structure

```text
event-management-system/
├── backend/
│   ├── config/
│   │   └── config.py               # Environment configuration (.env loader)
│   ├── database/
│   │   └── db.py                   # Unified SQLite & Oracle DatabaseManager
│   ├── controllers/
│   │   ├── dashboard_controller.py # SQL aggregations for dashboard & charts
│   │   ├── events_controller.py    # CRUD & FK validation for events
│   │   ├── organizers_controller.py
│   │   ├── venues_controller.py
│   │   ├── categories_controller.py
│   │   ├── participants_controller.py
│   │   ├── registrations_controller.py
│   │   ├── payments_controller.py
│   │   ├── reports_controller.py   # 7 SQL reports & CSV export
│   │   ├── database_controller.py  # Live table schema & rows viewer
│   │   └── query_controller.py    # Safe SQL runner & presets
│   └── app.py                      # Flask Application factory
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css          # Responsive styling, tables, modals, ER cards
│   │   └── js/
│   │       ├── api.js              # REST API Client & toast system
│   │       ├── charts.js           # Chart.js visualization engine
│   │       └── app.js              # SPA navigation, modals & CRUD handlers
│   └── templates/
│       └── index.html              # Responsive single-page application UI
├── database/
│   ├── schema/
│   │   ├── schema_sqlite.sql       # SQLite DDL with FKs, checks & indexes
│   │   └── schema_oracle.sql       # Oracle SQL DDL (IDENTITY, VARCHAR2, etc.)
│   ├── seed/
│   │   ├── seed_sqlite.sql         # Realistic test seed data for SQLite
│   │   └── seed_oracle.sql         # Seed data for Oracle Database
│   └── queries/
│       └── sample_queries.sql      # 8 Demonstrative DBMS queries
├── test_backend.py                 # Automated test suite (16 tests, 100% pass)
├── test_two_way.py                 # Two-way SQL verification script
├── requirements.txt                # Python dependencies
├── run.bat                         # 1-Click Windows launch script
├── run.ps1                         # PowerShell launch script
├── run.py                          # Python application runner
├── .env.example                    # Environment variable template
└── README.md                       # Comprehensive project documentation
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | DB connection state, engine type, active tables |
| `GET` | `/api/dashboard/stats` | SQL counts, revenue, and chart data |
| `GET` | `/api/events` | List events (search, filter, sort, paginate) |
| `POST` | `/api/events` | Create event (validates FKs to Org, Venue, Cat) |
| `PUT` | `/api/events/:id` | Update event details |
| `DELETE` | `/api/events/:id` | Delete event (checks for registered attendees) |
| `GET` | `/api/organizers` | List organizers with hosted event counts |
| `POST` | `/api/organizers` | Create new organizer |
| `DELETE` | `/api/organizers/:id` | Delete organizer (FK protected) |
| `GET` | `/api/venues` | List venues with seating capacity |
| `POST` | `/api/venues` | Add venue (validates `Capacity > 0`) |
| `GET` | `/api/categories` | List categories with event count |
| `GET` | `/api/participants` | List registered participants |
| `GET` | `/api/registrations` | List attendee registrations with payment status |
| `POST` | `/api/registrations` | Book participant for event (checks capacity) |
| `GET` | `/api/payments` | List payment transactions |
| `POST` | `/api/payments` | Record payment (enforces 1:1 with registration) |
| `GET` | `/api/reports/:type` | Generate SQL report (`?format=csv` for download) |
| `GET` | `/api/database/tables/:name` | Live inspection of SQL table records and schema |
| `POST` | `/api/admin/execute` | Execute safe SELECT SQL query in console |
| `POST` | `/api/database/reset` | Drop and re-seed all tables to initial state |

---

## 🏆 Assessment & Viva Preparation Checklist

When presenting this project:
- [x] **Show ER Diagram:** Point out Primary Keys (`PK`), Foreign Keys (`FK`), and explain why `Payment` has a 1:1 relationship with `Registration`.
- [x] **Show Database Tables:** Open the *"Database Tables"* tab, select different tables, and explain how the rows displayed are queried directly from the real SQL database.
- [x] **Demonstrate CRUD Operations:** Add an event, edit an organizer, delete a test record, and view the notification toasts.
- [x] **Demonstrate Referential Integrity:** Try to delete an organizer who has events scheduled to show the database error handling.
- [x] **Demonstrate Complex Queries:** Go to the *"SQL Console"*, run the Multi-Table JOIN or Aggregate query presets, and point out the execution duration and returned columns.
- [x] **Export a Report:** Select the *Comprehensive Event Report* and download it as CSV.
