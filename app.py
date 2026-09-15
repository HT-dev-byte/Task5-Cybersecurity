from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
import json
import csv
import io
from datetime import datetime
import database

app = Flask(__name__)

@app.route('/')
def dashboard():
    conn = database.get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    emails = conn.execute('SELECT * FROM emails').fetchall()

    link_interactions = conn.execute("SELECT COUNT(*) FROM user_decisions WHERE action IN ('OPEN_LINK', 'FORM_SUBMIT')").fetchone()[0]
    phishing_reports = conn.execute("SELECT COUNT(*) FROM user_decisions WHERE action = 'REPORT_PHISHING'").fetchone()[0]

    avg_score_res = conn.execute("SELECT AVG(awareness_score) FROM users").fetchone()[0]
    avg_score = round(avg_score_res, 1) if avg_score_res else 100.0

    incident = conn.execute("SELECT * FROM incident_state ORDER BY id DESC LIMIT 1").fetchone()
    recent_events = conn.execute("SELECT * FROM security_events ORDER BY id DESC LIMIT 5").fetchall()

    conn.close()

    return render_template('dashboard.html',
                           active_page='dashboard',
                           total_users=len(users),
                           total_emails=len(emails),
                           link_interactions=link_interactions,
                           phishing_reports=phishing_reports,
                           avg_score=avg_score,
                           incident=incident,
                           recent_events=recent_events)

@app.route('/inbox')
def inbox():
    conn = database.get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    user_id = request.args.get('user_id', 1, type=int)
    current_user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not current_user and users:
        current_user = users[0]

    emails = conn.execute('SELECT * FROM emails').fetchall()
    conn.close()

    return render_template('inbox.html',
                           active_page='inbox',
                           users=users,
                           current_user=current_user,
                           emails=emails)

@app.route('/email/<int:email_id>')
def view_email(email_id):
    conn = database.get_db_connection()
    user_id = request.args.get('user_id', 1, type=int)
    current_user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    email = conn.execute('SELECT * FROM emails WHERE id = ?', (email_id,)).fetchone()
    conn.close()

    if not email:
        return "Email not found", 404

    return render_template('email_view.html',
                           active_page='inbox',
                           current_user=current_user,
                           email=email)

@app.route('/decision', methods=['POST'])
def user_decision():
    user_id = request.form.get('user_id', type=int)
    email_id = request.form.get('email_id', type=int)
    action = request.form.get('action')

    conn = database.get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    email = conn.execute('SELECT * FROM emails WHERE id = ?', (email_id,)).fetchone()

    if not user or not email:
        conn.close()
        return redirect(url_for('inbox'))

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if action == 'OPEN_LINK':
        risk_level = 'HIGH_RISK'
        severity = 'HIGH'
        details = f"User interacted with link in email ID {email_id} ({email['subject']})"
        event_type = 'LINK_INTERACTION'
        new_score = max(0, user['awareness_score'] - 15)
        conn.execute('UPDATE users SET awareness_score = ? WHERE id = ?', (new_score, user_id))

        conn.execute('INSERT INTO user_decisions (timestamp, username, email_id, action, risk_level) VALUES (?, ?, ?, ?, ?)',
                     (timestamp, user['email'], email_id, action, risk_level))
        conn.execute('INSERT INTO security_events (timestamp, username, event_type, severity, details) VALUES (?, ?, ?, ?, ?)',
                     (timestamp, user['email'], event_type, severity, details))
        conn.execute('INSERT INTO security_events (timestamp, username, event_type, severity, details) VALUES (?, ?, ?, ?, ?)',
                     (timestamp, 'SOC_ANALYST', 'INCIDENT_DETECTED', 'WARNING', f"Automated trigger: Phishing link interaction by {user['email']}"))
        conn.commit()
        conn.close()
        return redirect(url_for('landing_page', user_id=user_id, email_id=email_id))

    elif action == 'REPORT_PHISHING':
        risk_level = 'SAFE'
        severity = 'LOW'
        event_type = 'EMAIL_REPORTED'
        details = f"User reported email ID {email_id} ({email['subject']}) as suspicious"
        new_score = min(100, user['awareness_score'] + 5)
        conn.execute('UPDATE users SET awareness_score = ? WHERE id = ?', (new_score, user_id))

        conn.execute('INSERT INTO user_decisions (timestamp, username, email_id, action, risk_level) VALUES (?, ?, ?, ?, ?)',
                     (timestamp, user['email'], email_id, action, risk_level))
        conn.execute('INSERT INTO security_events (timestamp, username, event_type, severity, details) VALUES (?, ?, ?, ?, ?)',
                     (timestamp, user['email'], event_type, severity, details))
        conn.commit()
        conn.close()
        return redirect(url_for('awareness_analysis', user_id=user_id, email_id=email_id, action=action))

    else: # IGNORE
        risk_level = 'NEUTRAL'
        severity = 'INFO'
        event_type = 'EMAIL_IGNORED'
        details = f"User ignored email ID {email_id}"

        conn.execute('INSERT INTO user_decisions (timestamp, username, email_id, action, risk_level) VALUES (?, ?, ?, ?, ?)',
                     (timestamp, user['email'], email_id, action, risk_level))
        conn.execute('INSERT INTO security_events (timestamp, username, event_type, severity, details) VALUES (?, ?, ?, ?, ?)',
                     (timestamp, user['email'], event_type, severity, details))
        conn.commit()
        conn.close()
        return redirect(url_for('awareness_analysis', user_id=user_id, email_id=email_id, action=action))

@app.route('/landing-page')
def landing_page():
    user_id = request.args.get('user_id', 1, type=int)
    email_id = request.args.get('email_id', 1, type=int)
    conn = database.get_db_connection()
    current_user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    return render_template('landing_page.html',
                           active_page='inbox',
                           current_user=current_user,
                           email_id=email_id)

@app.route('/landing-page/submit', methods=['POST'])
def submit_landing_form():
    user_id = request.form.get('user_id', type=int)
    email_id = request.form.get('email_id', type=int)

    conn = database.get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if user:
        conn.execute('INSERT INTO security_events (timestamp, username, event_type, severity, details) VALUES (?, ?, ?, ?, ?)',
                     (timestamp, user['email'], 'FORM_INTERACTION', 'HIGH', 'Interacted with dummy credential verification form on landing page'))
        conn.execute('INSERT INTO user_decisions (timestamp, username, email_id, action, risk_level) VALUES (?, ?, ?, ?, ?)',
                     (timestamp, user['email'], email_id, 'FORM_SUBMIT', 'HIGH_RISK'))
        conn.commit()
    conn.close()

    return redirect(url_for('awareness_analysis', user_id=user_id, email_id=email_id, action='FORM_SUBMIT'))

@app.route('/awareness-analysis')
def awareness_analysis():
    user_id = request.args.get('user_id', 1, type=int)
    email_id = request.args.get('email_id', 1, type=int)
    action = request.args.get('action', 'IGNORE')

    conn = database.get_db_connection()
    current_user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    email = conn.execute('SELECT * FROM emails WHERE id = ?', (email_id,)).fetchone()
    conn.close()

    indicators = json.loads(email['indicators']) if email and email['indicators'] else []

    return render_template('awareness_analysis.html',
                           active_page='inbox',
                           current_user=current_user,
                           email=email,
                           indicators=indicators,
                           action=action)

@app.route('/events')
def events():
    user_filter = request.args.get('user', '')
    event_type_filter = request.args.get('event_type', '')
    severity_filter = request.args.get('severity', '')

    query = "SELECT * FROM security_events WHERE 1=1"
    params = []

    if user_filter:
        query += " AND username = ?"
        params.append(user_filter)
    if event_type_filter:
        query += " AND event_type = ?"
        params.append(event_type_filter)
    if severity_filter:
        query += " AND severity = ?"
        params.append(severity_filter)

    query += " ORDER BY id DESC"

    conn = database.get_db_connection()
    event_rows = conn.execute(query, params).fetchall()
    users = conn.execute('SELECT * FROM users').fetchall()

    all_event_types_rows = conn.execute('SELECT DISTINCT event_type FROM security_events').fetchall()
    event_types = [r['event_type'] for r in all_event_types_rows]

    conn.close()

    return render_template('events.html',
                           active_page='events',
                           events=event_rows,
                           users=users,
                           event_types=event_types,
                           selected_user=user_filter,
                           selected_event_type=event_type_filter,
                           selected_severity=severity_filter)

@app.route('/events/export/json')
def export_events_json():
    user_filter = request.args.get('user', '')
    event_type_filter = request.args.get('event_type', '')
    severity_filter = request.args.get('severity', '')

    query = "SELECT * FROM security_events WHERE 1=1"
    params = []
    if user_filter:
        query += " AND username = ?"
        params.append(user_filter)
    if event_type_filter:
        query += " AND event_type = ?"
        params.append(event_type_filter)
    if severity_filter:
        query += " AND severity = ?"
        params.append(severity_filter)
    query += " ORDER BY id ASC"

    conn = database.get_db_connection()
    events_rows = conn.execute(query, params).fetchall()
    conn.close()

    events_list = [dict(r) for r in events_rows]
    return jsonify(events_list)

@app.route('/events/export/csv')
def export_events_csv():
    user_filter = request.args.get('user', '')
    event_type_filter = request.args.get('event_type', '')
    severity_filter = request.args.get('severity', '')

    query = "SELECT * FROM security_events WHERE 1=1"
    params = []
    if user_filter:
        query += " AND username = ?"
        params.append(user_filter)
    if event_type_filter:
        query += " AND event_type = ?"
        params.append(event_type_filter)
    if severity_filter:
        query += " AND severity = ?"
        params.append(severity_filter)
    query += " ORDER BY id ASC"

    conn = database.get_db_connection()
    events_rows = conn.execute(query, params).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Timestamp', 'Username', 'EventType', 'Severity', 'Details'])
    for r in events_rows:
        writer.writerow([r['id'], r['timestamp'], r['username'], r['event_type'], r['severity'], r['details']])

    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-disposition": "attachment; filename=simulated_security_events.csv"})

@app.route('/incident-response')
def incident_response():
    conn = database.get_db_connection()
    incident = conn.execute('SELECT * FROM incident_state ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()

    return render_template('incident_response.html',
                           active_page='incident',
                           incident=incident)

@app.route('/incident-response/update', methods=['POST'])
def update_incident():
    action = request.form.get('action')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = database.get_db_connection()
    incident = conn.execute('SELECT * FROM incident_state ORDER BY id DESC LIMIT 1').fetchone()

    if action == 'CONTAIN':
        conn.execute('''
            UPDATE incident_state
            SET status = 'Contained', campaign_disabled = 1, url_blocked = 1, updated_at = ?
            WHERE id = ?
        ''', (timestamp, incident['id']))
        conn.execute('INSERT INTO security_events (timestamp, username, event_type, severity, details) VALUES (?, ?, ?, ?, ?)',
                     (timestamp, 'SOC_ANALYST', 'CAMPAIGN_CONTAINED', 'INFO', 'Campaign disabled and simulated URL blocked in firewall rules'))

    elif action == 'ERADICATE':
        conn.execute('''
            UPDATE incident_state
            SET status = 'Eradicated', artifacts_removed = 1, updated_at = ?
            WHERE id = ?
        ''', (timestamp, incident['id']))
        conn.execute('INSERT INTO security_events (timestamp, username, event_type, severity, details) VALUES (?, ?, ?, ?, ?)',
                     (timestamp, 'SOC_ANALYST', 'ARTIFACTS_REMOVED', 'INFO', 'Simulated phishing artifacts purged from user mailboxes'))

    elif action == 'RECOVER':
        conn.execute('''
            UPDATE incident_state
            SET status = 'Recovered', users_reviewed = 1, training_assigned = 1, updated_at = ?
            WHERE id = ?
        ''', (timestamp, incident['id']))
        conn.execute('INSERT INTO security_events (timestamp, username, event_type, severity, details) VALUES (?, ?, ?, ?, ?)',
                     (timestamp, 'SOC_ANALYST', 'RECOVERY_COMPLETED', 'INFO', 'Affected test users reviewed and targeted awareness modules assigned'))

    conn.commit()
    conn.close()
    return redirect(url_for('incident_response'))

@app.route('/incident-timeline')
def incident_timeline():
    conn = database.get_db_connection()
    timeline_events = conn.execute('SELECT * FROM security_events ORDER BY id ASC').fetchall()
    conn.close()

    return render_template('incident_timeline.html',
                           active_page='timeline',
                           timeline_events=timeline_events)

@app.route('/findings')
def findings():
    return render_template('findings.html', active_page='findings')

@app.route('/metrics')
def metrics():
    conn = database.get_db_connection()
    total_emails = conn.execute("SELECT COUNT(*) FROM emails").fetchone()[0]
    total_actions = conn.execute("SELECT COUNT(*) FROM user_decisions").fetchone()[0]

    reports_count = conn.execute("SELECT COUNT(*) FROM user_decisions WHERE action = 'REPORT_PHISHING'").fetchone()[0]
    links_count = conn.execute("SELECT COUNT(*) FROM user_decisions WHERE action = 'OPEN_LINK'").fetchone()[0]
    forms_count = conn.execute("SELECT COUNT(*) FROM user_decisions WHERE action = 'FORM_SUBMIT'").fetchone()[0]
    ignore_count = conn.execute("SELECT COUNT(*) FROM user_decisions WHERE action = 'IGNORE'").fetchone()[0]

    reporting_rate = round((reports_count / total_actions * 100), 1) if total_actions > 0 else 0.0
    interaction_rate = round(((links_count + forms_count) / total_actions * 100), 1) if total_actions > 0 else 0.0

    users = conn.execute("SELECT username, awareness_score FROM users").fetchall()
    user_names = [u['username'] for u in users]
    user_scores = [u['awareness_score'] for u in users]

    conn.close()

    return render_template('metrics.html',
                           active_page='metrics',
                           total_emails=total_emails,
                           total_actions=total_actions,
                           reports_count=reports_count,
                           links_count=links_count,
                           forms_count=forms_count,
                           ignore_count=ignore_count,
                           reporting_rate=reporting_rate,
                           interaction_rate=interaction_rate,
                           user_names=user_names,
                           user_scores=user_scores)

@app.route('/architecture')
def architecture():
    return render_template('architecture.html', active_page='architecture')

if __name__ == '__main__':
    database.init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
