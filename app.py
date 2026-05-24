import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__, template_folder='templates')
# Fixed secret key — use env var if set, otherwise a stable fallback so sessions survive restarts
app.secret_key = os.getenv('SECRET_KEY', 'crimedatabase-secret-key-stable-2024')

MAX_DESC_LEN = 2000  # max characters for description field


def get_db_connection():
    """Open a DB connection. Returns (conn, None) on success, (None, error_str) on failure."""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port="5432"
        )
        return conn, None
    except Exception as e:
        return None, str(e)


def db_error_page(message):
    """Render a simple error page when DB is unavailable."""
    return render_template('db_error.html', message=message), 503


# ─────────────────────────────────────────────
# OVERVIEW / COMMAND DASHBOARD
# ─────────────────────────────────────────────
@app.route('/')
def overview():
    conn, err = get_db_connection()
    if err:
        return db_error_page(err)

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Recent FIRs for the dispatch table
    cur.execute("""
        SELECT fir_id, date_filed, description, status
        FROM fir
        ORDER BY date_filed DESC, fir_id DESC
        LIMIT 10
    """)
    fir_data = cur.fetchall()

    # KPI: total open cases (non-resolved FIRs)
    cur.execute("SELECT COUNT(*) FROM fir WHERE status != 'Resolved'")
    open_cases = cur.fetchone()[0]

    # KPI: pending FIRs
    cur.execute("SELECT COUNT(*) FROM fir WHERE status = 'Pending'")
    pending_firs = cur.fetchone()[0]

    # KPI: total FIRs today
    cur.execute("SELECT COUNT(*) FROM fir WHERE date_filed = CURRENT_DATE")
    today_firs = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template(
        'command_overview.html',
        firs=fir_data,
        open_cases=open_cases,
        pending_firs=pending_firs,
        today_firs=today_firs,
    )


# ─────────────────────────────────────────────
# ACTIVITY FEED
# ─────────────────────────────────────────────
@app.route('/activity')
def activity():
    conn, err = get_db_connection()
    if err:
        return db_error_page(err)

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT fir_id, date_filed, description, status
        FROM fir
        ORDER BY date_filed DESC, fir_id DESC
        LIMIT 50
    """)
    fir_logs = cur.fetchall()

    # Sidebar stats
    cur.execute("SELECT COUNT(*) FROM fir")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fir WHERE status = 'Critical'")
    critical_count = cur.fetchone()[0]

    cur.execute("""
        SELECT status, COUNT(*) as cnt
        FROM fir GROUP BY status
    """)
    status_counts = {row['status']: row['cnt'] for row in cur.fetchall()}

    cur.close()
    conn.close()
    return render_template(
        'activity_feed.html',
        fir_logs=fir_logs,
        total=total,
        critical_count=critical_count,
        status_counts=status_counts,
    )


# ─────────────────────────────────────────────
# OPERATIONAL TOOLS
# ─────────────────────────────────────────────
@app.route('/tools')
def tools():
    conn, err = get_db_connection()
    if err:
        return db_error_page(err)

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT fir_id, description, status FROM fir ORDER BY fir_id DESC LIMIT 10")
    recent_firs = cur.fetchall()

    cur.close()
    conn.close()
    return render_template(
        'operational_tools.html',
        recent_firs=recent_firs,
        success=request.args.get('success'),
        error=request.args.get('error')
    )


# ─────────────────────────────────────────────
# INTEL INSIGHTS
# ─────────────────────────────────────────────
@app.route('/intel')
def intel():
    conn, err = get_db_connection()
    if err:
        return db_error_page(err)

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT status, COUNT(*) as cnt
        FROM fir
        GROUP BY status
    """)
    status_counts = {row['status']: row['cnt'] for row in cur.fetchall()}

    cur.execute("SELECT COUNT(*) FROM fir")
    total_firs = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fir WHERE status = 'Critical'")
    critical_firs = cur.fetchone()[0]

    cur.execute("""
        SELECT fir_id, date_filed, description, status
        FROM fir
        ORDER BY fir_id DESC
        LIMIT 5
    """)
    recent_intel = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'intelligence_insights.html',
        status_counts=status_counts,
        total_firs=total_firs,
        critical_firs=critical_firs,
        recent_intel=recent_intel,
    )


# ─────────────────────────────────────────────
# POST: REGISTER FIR
# ─────────────────────────────────────────────
@app.route('/submit_fir', methods=['POST'])
def submit_fir():
    description = request.form.get('description', '').strip()
    status = request.form.get('status', 'Pending')

    # Validate status value
    valid_statuses = ['Pending', 'Investigating', 'Critical']
    if status not in valid_statuses:
        status = 'Pending'

    if not description:
        return redirect(url_for('tools', error='Description cannot be empty'))

    if len(description) > MAX_DESC_LEN:
        return redirect(url_for('tools', error=f'Description too long (max {MAX_DESC_LEN} chars)'))

    conn, err = get_db_connection()
    if err:
        return redirect(url_for('tools', error='Database connection failed'))

    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO fir (date_filed, description, status) VALUES (CURRENT_DATE, %s, %s)",
            (description, status)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('tools', success='FIR registered successfully'))
    except Exception as e:
        conn.rollback()
        conn.close()
        return redirect(url_for('tools', error=f'DB error: {str(e)[:100]}'))


# ─────────────────────────────────────────────
# POST: ASSIGN / UPDATE CASE STATUS
# ─────────────────────────────────────────────
@app.route('/assign_case', methods=['POST'])
def assign_case():
    fir_id = request.form.get('fir_id', '').strip()
    new_status = request.form.get('new_status', '').strip()

    if not fir_id or not new_status:
        return redirect(url_for('tools', error='FIR ID and status are required'))

    if not fir_id.isdigit():
        return redirect(url_for('tools', error='FIR ID must be a number'))

    valid_statuses = ['Pending', 'Investigating', 'Critical', 'Resolved', 'Assigned']
    if new_status not in valid_statuses:
        return redirect(url_for('tools', error='Invalid status value'))

    conn, err = get_db_connection()
    if err:
        return redirect(url_for('tools', error='Database connection failed'))

    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE fir SET status = %s WHERE fir_id = %s",
            (new_status, int(fir_id))
        )
        if cur.rowcount == 0:
            conn.rollback()
            cur.close()
            conn.close()
            return redirect(url_for('tools', error=f'FIR #{fir_id} not found'))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('tools', success=f'Case #{fir_id} updated to {new_status}'))
    except Exception as e:
        conn.rollback()
        conn.close()
        return redirect(url_for('tools', error=f'DB error: {str(e)[:100]}'))


# ─────────────────────────────────────────────
# API: LIVE SEARCH (JSON for async)
# ─────────────────────────────────────────────
@app.route('/api/search')
def api_search():
    query = request.args.get('q', '').strip()
    results = []

    if not query:
        return jsonify({'results': []})

    if len(query) > 200:
        return jsonify({'error': 'Query too long'}), 400

    conn, err = get_db_connection()
    if err:
        return jsonify({'error': 'Database connection failed'}), 503

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if query.isdigit():
            cur.execute(
                "SELECT fir_id, date_filed::text, description, status FROM fir WHERE fir_id = %s",
                (int(query),)
            )
        else:
            cur.execute(
                "SELECT fir_id, date_filed::text, description, status FROM fir WHERE description ILIKE %s ORDER BY date_filed DESC LIMIT 20",
                (f'%{query}%',)
            )
        results = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'results': results})


# ─────────────────────────────────────────────
# API: ALL FIRs (for delete/view operations)
# ─────────────────────────────────────────────
@app.route('/api/firs')
def api_firs():
    conn, err = get_db_connection()
    if err:
        return jsonify({'error': err}), 503
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT fir_id, date_filed::text, description, status FROM fir ORDER BY fir_id DESC LIMIT 100")
    results = [dict(row) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify({'results': results})


# ─────────────────────────────────────────────
# POST: DELETE FIR
# ─────────────────────────────────────────────
@app.route('/delete_fir', methods=['POST'])
def delete_fir():
    fir_id = request.form.get('fir_id', '').strip()
    if not fir_id or not fir_id.isdigit():
        return redirect(url_for('tools', error='Invalid FIR ID for deletion'))

    conn, err = get_db_connection()
    if err:
        return redirect(url_for('tools', error='Database connection failed'))

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM fir WHERE fir_id = %s", (int(fir_id),))
        if cur.rowcount == 0:
            conn.rollback()
            cur.close()
            conn.close()
            return redirect(url_for('tools', error=f'FIR #{fir_id} not found'))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('tools', success=f'FIR #{fir_id} deleted successfully'))
    except Exception as e:
        conn.rollback()
        conn.close()
        return redirect(url_for('tools', error=f'DB error: {str(e)[:100]}'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)