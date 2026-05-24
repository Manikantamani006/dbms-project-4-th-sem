<div align="center">

```
 ██████╗██████╗ ██╗███╗   ███╗███████╗
██╔════╝██╔══██╗██║████╗ ████║██╔════╝
██║     ██████╔╝██║██╔████╔██║█████╗  
██║     ██╔══██╗██║██║╚██╔╝██║██╔══╝  
╚██████╗██║  ██║██║██║ ╚═╝ ██║███████╗
 ╚═════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚══════╝
██████╗  █████╗ ████████╗ █████╗ ██████╗  █████╗ ███████╗███████╗
██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝
██║  ██║███████║   ██║   ███████║██████╔╝███████║███████╗█████╗  
██║  ██║██╔══██║   ██║   ██╔══██║██╔══██╗██╔══██║╚════██║██╔══╝  
██████╔╝██║  ██║   ██║   ██║  ██║██████╔╝██║  ██║███████║███████╗
╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝
```

**A tactical, dark-themed web application for managing First Information Reports (FIRs)**  
*Built with Flask · PostgreSQL · Tailwind CSS*

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-CDN-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)

</div>

---

## 📁 Project Structure

```
dbms-project-4-th-sem/
│
├── 📄 app.py                        ← Flask backend (routes, DB logic, API)
├── 📄 requirements.txt              ← Python dependencies (pip install -r)
├── 📄 README.md                     ← You are here
├── 📄 .gitignore                    ← Excludes venv/, .env secrets
│
├── 🗄️ database/
│   └── 📄 schema.sql               ← Full DB schema: tables, procedure,
│                                       trigger, seed data & queries
│
└── 🎨 templates/
    ├── 📄 command_overview.html     ← Dashboard: KPIs, dispatch table, live stats
    ├── 📄 operational_tools.html    ← Tools: Register FIR, Update Status, Search
    ├── 📄 activity_feed.html        ← Live feed: all FIR logs with status filter
    ├── 📄 intelligence_insights.html← Intel: status charts, breakdown, recent logs
    └── 📄 db_error.html             ← Graceful error page if DB is unreachable
```

> **Note:** The following are local-only and never pushed to GitHub:
> ```
> .env                 ← DB credentials (SECRET — do not share)
> venv/ or dbms pro/  ← Python virtual environment
> ```

---

## ⚙️ How It All Connects

```
Browser
   │
   ▼
┌──────────────────────────────────────────────────────────┐
│                        app.py                            │
│                                                          │
│  GET  /          →  command_overview.html                │
│  GET  /activity  →  activity_feed.html                   │
│  GET  /tools     →  operational_tools.html               │
│  GET  /intel     →  intelligence_insights.html           │
│                                                          │
│  POST /submit_fir    →  Insert FIR → redirect /tools     │
│  POST /assign_case   →  Update status → redirect /tools  │
│  POST /delete_fir    →  Delete FIR → redirect /tools     │
│  GET  /api/search    →  JSON search results              │
└───────────────────────────┬──────────────────────────────┘
                            │  psycopg2
                            ▼
               ┌────────────────────────┐
               │       PostgreSQL        │
               │                        │
               │  TABLE: fir            │
               │  TABLE: officer        │
               │  TABLE: cases          │
               │  TABLE: suspect        │
               │  TABLE: evidence       │
               │                        │
               │  PROCEDURE: AssignCase │
               │  TRIGGER: UpdateCaseTS │
               └────────────────────────┘
```

---

## 🚀 Setup & Installation

### 1. Prerequisites
- **Python 3.x** — [Download](https://python.org)
- **PostgreSQL** running on port `5432` — [Download](https://postgresql.org)
- **Git** — [Download](https://git-scm.com)

### 2. Clone the Repository
```bash
git clone https://github.com/Manikantamani006/dbms-project-4-th-sem.git
cd dbms-project-4-th-sem
```

### 3. Set Up the Database
Open **pgAdmin** or **psql** and run the schema file:
```sql
-- In psql:
\i database/schema.sql

-- Or in pgAdmin: open schema.sql and click ▶ Execute
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```env
DB_HOST=localhost
DB_NAME=your_database_name
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
SECRET_KEY=any-random-secret-string
```

### 5. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 6. Run the Application
```bash
python -m flask run --port=5001
```

Then open your browser at: **[http://127.0.0.1:5001](http://127.0.0.1:5001)**

---

## 🖥️ Pages & Features

| Page | URL | What it does |
|---|---|---|
| **Overview** | `/` | Dashboard with KPI cards (open cases, pending FIRs, today's count) + dispatch table |
| **Activity** | `/activity` | Live chronological feed of all FIRs — color-coded by status |
| **Tools** | `/tools` | Register new FIR · Update case status · Live DB search · Raise critical alert |
| **Intel** | `/intel` | Status breakdown stats · Recent intel logs from DB |

---

## 🗄️ Database Schema

```
officer ──────────────────────────────────────────┐
  officer_id (PK)                                 │
  name                                            │
  badge_number (UNIQUE)                           │
                                                  ▼
fir ──────────────────────── cases ───────────────┘
  fir_id (PK)                 case_id (PK)
  date_filed                  fir_id (FK → fir)
  description                 officer_id (FK → officer)
  status                      status
      │                       last_updated ←─── TRIGGER
      │                             │             (auto on evidence insert)
      ▼                             ▼
  suspect                       evidence
  suspect_id (PK)               evidence_id (PK)
  fir_id (FK → fir)             case_id (FK → cases)
  name                          description
  details                       date_logged
```

**Stored Procedure:**
```sql
CALL AssignCase(fir_id, officer_id);
-- Creates case entry + marks FIR as 'Assigned' atomically
```

**Trigger:**
```
evidence INSERT → UpdateCaseTimestamp → cases.last_updated = NOW()
```

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: flask` | Run `pip install -r requirements.txt` inside venv |
| Browser shows old/different app | Another Flask app is holding port 5000. Use `--port=5001` |
| `Database connection failed` | Check `.env` values and ensure PostgreSQL service is running |
| `FIR ID not found` on assign | Verify the FIR exists first via the DB Query tool on `/tools` |
| `Address already in use` | Kill the old process: `taskkill /F /IM python.exe` (Windows) |

---

<div align="center">

Made with 🔵 for DBMS 4th Semester Project

</div>
