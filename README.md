# CrimeDatabase

Welcome to **CrimeDatabase**, a tactical web-based interface for managing First Information Reports (FIRs), analyzing intelligence insights, and handling active operations. 

This system uses a **Python Flask backend** with a **PostgreSQL database** and features a dark, CRT-styled, responsive tactical frontend built with Tailwind CSS.

---

## 🚀 Setup & Installation

### 1. Prerequisites
- **Python 3.x** installed on your system.
- **PostgreSQL** installed and running on port `5432`.
- Your Postgres server should have a database set up with the `fir` table.

### 2. Configure Database
Create a file named `.env` in the root of the project folder (`C:\db project 2.0\.env`) and add your database credentials:
```env
DB_HOST=localhost
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
```

### 3. Open Terminal & Navigate to Project
Open PowerShell or Command Prompt and change directory to the project folder:
```powershell
cd "C:\db project 2.0"
```

### 4. Activate the Virtual Environment
Activate the pre-existing Python environment where the dependencies (Flask, psycopg2) are installed:
```powershell
.\venv\Scripts\activate
```
*(You will see `(venv)` appear at the start of your command prompt.)*

### 5. Run the Application
Start the Flask server. We recommend running it on port 5001 to avoid conflicts with other apps:
```powershell
python -m flask run --port=5001
```

---

## 💻 How to Use the Dashboard

Once the server is running, open your web browser and go to: **[http://127.0.0.1:5001](http://127.0.0.1:5001)**

### 1. Overview (`/`)
- Shows a high-level summary of Open Cases, Pending FIRs, and Today's FIRs.
- Click the floating `+` button in the bottom right to quickly pop open the **Register FIR** modal.

### 2. Activity (`/activity`)
- This is a live, chronological feed of all FIRs recently logged into the database.
- It displays the FIR ID, time filed, description, and color-coded statuses (e.g., Critical, Resolving, Pending).

### 3. Tools (`/tools`)
- **Register FIR**: Use the form on the left to file a new report into the system. Choose a category, location, and hit submit. You will see a green success notification in the corner.
- **Update Case Status**: Enter an existing `FIR ID` (just the number) and use the dropdown to change its status (e.g., to "Investigating" or "Resolved").
- **Database Query**: Use the text box on the right side of the screen to search the database. You can search by entering a specific FIR ID or by typing keywords (like "theft" or "assault") to instantly filter records.

### 4. Intel Insights (`/intel`)
- Displays statistical breakdowns.
- Shows total FIR counts, the number of critical incidents, and a status distribution.
- Lists the most recent intelligence logs in a concise sidebar format.

---

## 🛠️ Troubleshooting

- **Address already in use / Old version showing:** If you run `python app.py` and your browser shows an old version of the site (or "RMS COMMAND"), it means you have a stuck background process holding onto port `5000`. Stop your server by pressing `Ctrl + C`, and start it on port `5001` instead (`python -m flask run --port=5001`).
- **Database Connection Error:** Ensure your PostgreSQL server is running and that the credentials in your `.env` file are exactly correct.
