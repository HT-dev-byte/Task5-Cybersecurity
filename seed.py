import sqlite3
import json
import os
from database import get_db_connection, init_db

def seed_data():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing data and reset sqlite_sequence for fresh seed
    cursor.execute('DELETE FROM users')
    cursor.execute('DELETE FROM emails')
    cursor.execute('DELETE FROM security_events')
    cursor.execute('DELETE FROM user_decisions')
    cursor.execute('DELETE FROM incident_state')
    try:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('users', 'emails', 'security_events', 'user_decisions', 'incident_state')")
    except sqlite3.OperationalError:
        pass # sqlite_sequence might not exist yet if no autoincrement occurred

    # 1. Seed Fictional Users
    users = [
        ('Alex Morgan', 'alex.morgan@northstar.example', 'Finance', 85),
        ('Jordan Lee', 'jordan.lee@northstar.example', 'Human Resources', 90),
        ('Taylor Smith', 'taylor.smith@northstar.example', 'Sales & Operations', 75),
        ('Casey Vance', 'casey.vance@northstar.example', 'Marketing', 95),
        ('Riley Davis', 'riley.davis@northstar.example', 'Engineering', 80)
    ]
    for u in users:
        cursor.execute('''
            INSERT INTO users (username, email, department, awareness_score)
            VALUES (?, ?, ?, ?)
        ''', u)

    # 2. Seed Fictional Emails (Phishing and Legitimate)
    emails = [
        (
            'Northstar IT Security <security@northstar.example>',
            'Urgent: Account Security Verification Required',
            'Dear User,\n\nYour account has been flagged for unusual activity originating from an unrecognized IP address. Immediate security verification is required to avoid suspension of your portal access.\n\nPlease review your account status and confirm your security settings immediately.\n\nClick the link below to verify:\nhttp://northstar.example/landing-page\n\nRegards,\nNorthstar Security Team',
            1,
            json.dumps([
                "Urgent and alarming language threatening account suspension",
                "Unexpected request to verify credentials",
                "Generic salutation ('Dear User')",
                "Suspicious call to action leading to external verification form",
                "Sender address impersonating internal IT Security"
            ]),
            '/landing-page'
        ),
        (
            'Northstar HR Portal <hr-noreply@northstar.example>',
            'Reminder: Annual Benefits Enrollment Window Open',
            'Hello Northstar Team,\n\nThis is a standard reminder that the annual benefits enrollment portal is open through the end of the month. You can access the portal directly through your standard internal employee dashboard.\n\nNo immediate action is required if you are not making changes.\n\nBest regards,\nHuman Resources Team',
            0,
            json.dumps([]),
            None
        ),
        (
            'Payroll Department <payroll-alert@northstar.example>',
            'ACTION REQUIRED: Immediate Direct Deposit Information Update',
            'Urgent Notice:\n\nWe encountered an error processing your recent payroll direct deposit. To ensure your next paycheck is processed on time, you must verify your banking credentials and account information immediately.\n\nPlease update your details now.\n\nThank you,\nPayroll Services',
            1,
            json.dumps([
                "High urgency regarding financial payout",
                "Unscheduled request for payroll banking details",
                "Pressure tactic to force quick action without verification"
            ]),
            '/landing-page'
        ),
        (
            'Northstar IT Support <helpdesk@northstar.example>',
            'Scheduled Maintenance: Internal Network - Saturday 2 AM',
            'Team,\n\nPlease be advised that our internal database services will undergo scheduled maintenance this Saturday from 2:00 AM to 4:00 AM EST. Services may be intermittently unavailable during this window.\n\nNo user action is required.\n\nIT Infrastructure Team',
            0,
            json.dumps([]),
            None
        )
    ]

    for e in emails:
        cursor.execute('''
            INSERT INTO emails (sender, subject, body, is_phishing, indicators, landing_url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', e)

    # 3. Seed Initial Simulated Security Event Log
    events = [
        ('2025-05-10 08:30:00', 'alex.morgan@northstar.example', 'EMAIL_RECEIVED', 'INFO', 'Received email: Urgent: Account Security Verification Required'),
        ('2025-05-10 08:31:15', 'alex.morgan@northstar.example', 'EMAIL_OPENED', 'INFO', 'Opened email ID 1'),
        ('2025-05-10 08:31:45', 'alex.morgan@northstar.example', 'LINK_INTERACTION', 'HIGH', 'Clicked link in simulated phishing message (Email ID 1)'),
        ('2025-05-10 08:32:00', 'alex.morgan@northstar.example', 'FORM_INTERACTION', 'HIGH', 'Interacted with dummy login form on simulated landing page'),
        ('2025-05-10 08:32:15', 'SOC_ANALYST', 'INCIDENT_DETECTED', 'WARNING', 'Automated trigger: Phishing link interaction detected for user alex.morgan@northstar.example'),
        ('2025-05-10 08:33:00', 'jordan.lee@northstar.example', 'EMAIL_REPORTED', 'LOW', 'Reported email ID 1 as suspicious phishing attempt'),
        ('2025-05-10 08:35:00', 'SOC_ANALYST', 'CAMPAIGN_CONTAINED', 'INFO', 'Simulated campaign disabled and domain blocked in firewall rule simulation')
    ]

    for ev in events:
        cursor.execute('''
            INSERT INTO security_events (timestamp, username, event_type, severity, details)
            VALUES (?, ?, ?, ?, ?)
        ''', ev)

    # 4. Seed User Decisions
    decisions = [
        ('2025-05-10 08:31:45', 'alex.morgan@northstar.example', 1, 'OPEN_LINK', 'HIGH_RISK'),
        ('2025-05-10 08:33:00', 'jordan.lee@northstar.example', 1, 'REPORT_PHISHING', 'SAFE'),
        ('2025-05-10 08:40:00', 'taylor.smith@northstar.example', 2, 'IGNORE', 'SAFE')
    ]

    for d in decisions:
        cursor.execute('''
            INSERT INTO user_decisions (timestamp, username, email_id, action, risk_level)
            VALUES (?, ?, ?, ?, ?)
        ''', d)

    # 5. Initial Incident State
    cursor.execute('''
        INSERT INTO incident_state (
            incident_number, incident_type, severity, status,
            campaign_disabled, url_blocked, artifacts_removed, users_reviewed, training_assigned
        ) VALUES ('INCIDENT #001', 'Simulated Phishing', 'Medium', 'Detected', 0, 0, 0, 0, 0)
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    seed_data()
    print("Database seeded with fictional simulation data.")
