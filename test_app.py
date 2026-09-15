import unittest
import json
import os
import sqlite3
from app import app
import database
import seed

class TestPhishAware(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        seed.seed_data()

    def test_dashboard_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Security Awareness', response.data)

    def test_inbox_route(self):
        response = self.client.get('/inbox')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'alex.morgan@northstar.example', response.data)

    def test_email_view_route(self):
        response = self.client.get('/email/1?user_id=1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Urgent: Account Security Verification Required', response.data)

    def test_user_decision_report_phishing(self):
        response = self.client.post('/decision', data={
            'user_id': 1,
            'email_id': 1,
            'action': 'REPORT_PHISHING'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Defensive Action', response.data)

    def test_user_decision_open_link_and_submit_landing_form(self):
        # 1. Open Link
        response = self.client.post('/decision', data={
            'user_id': 1,
            'email_id': 1,
            'action': 'OPEN_LINK'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Northstar Account Security', response.data)

        # 2. Submit dummy form
        form_response = self.client.post('/landing-page/submit', data={
            'user_id': 1,
            'email_id': 1,
            'dummy_pass': 'dummy_password_test'
        }, follow_redirects=True)
        self.assertEqual(form_response.status_code, 200)
        self.assertIn(b'HIGH RISK INTERACTION DETECTED', form_response.data)

    def test_events_log_and_exports(self):
        res_events = self.client.get('/events')
        self.assertEqual(res_events.status_code, 200)

        res_json = self.client.get('/events/export/json')
        self.assertEqual(res_json.status_code, 200)
        data = json.loads(res_json.data)
        self.assertTrue(len(data) > 0)

        res_csv = self.client.get('/events/export/csv')
        self.assertEqual(res_csv.status_code, 200)
        self.assertIn(b'Timestamp', res_csv.data)

    def test_incident_response_lifecycle(self):
        # Containment
        res_contain = self.client.post('/incident-response/update', data={'action': 'CONTAIN'}, follow_redirects=True)
        self.assertEqual(res_contain.status_code, 200)
        self.assertIn(b'Contained', res_contain.data)

        # Eradication
        res_eradicate = self.client.post('/incident-response/update', data={'action': 'ERADICATE'}, follow_redirects=True)
        self.assertEqual(res_eradicate.status_code, 200)
        self.assertIn(b'Eradicated', res_eradicate.data)

        # Recovery
        res_recover = self.client.post('/incident-response/update', data={'action': 'RECOVER'}, follow_redirects=True)
        self.assertEqual(res_recover.status_code, 200)
        self.assertIn(b'RECOVERED', res_recover.data)

    def test_metrics_and_architecture_routes(self):
        res_m = self.client.get('/metrics')
        self.assertEqual(res_m.status_code, 200)

        res_a = self.client.get('/architecture')
        self.assertEqual(res_a.status_code, 200)

if __name__ == '__main__':
    unittest.main()
