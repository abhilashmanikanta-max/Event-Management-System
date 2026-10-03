import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import create_app

def run_tests():
    app = create_app()
    app.testing = True
    client = app.test_client()

    print("=== RUNNING AUTOMATED DBMS BACKEND API TESTS ===")

    # 1. Health check
    res = client.get('/api/health')
    assert res.status_code == 200, f"Health check failed: {res.data}"
    print("[PASS] 1. Health Check & Table Discovery:", res.json['engine'])

    # 2. Dashboard Stats
    res = client.get('/api/dashboard/stats')
    assert res.status_code == 200, f"Dashboard stats failed: {res.data}"
    counts = res.json['counts']
    print(f"[PASS] 2. Dashboard Stats: {counts['events']} Events, {counts['participants']} Participants, {counts['registrations']} Registrations, ${counts['total_revenue']} Revenue")

    # 3. Events List & Filtering
    res = client.get('/api/events?limit=5')
    assert res.status_code == 200
    events = res.json['data']
    assert len(events) > 0
    print(f"[PASS] 3. Events List (retrieved {len(events)} events): First event is '{events[0]['Event_Name']}'")

    # 4. Create Event with FKs
    new_evt = {
        "Event_Name": "DBMS Project Showcase 2026",
        "Date": "2026-12-20",
        "Time": "11:00 AM",
        "Organizer_ID": 1,
        "Venue_ID": 1,
        "Category_ID": 1
    }
    res = client.post('/api/events', json=new_evt)
    assert res.status_code == 201, f"Create event failed: {res.data}"
    created_evt_id = res.json['event_id']
    print(f"[PASS] 4. Created Event #{created_evt_id} with Foreign Keys")

    # 5. Organizers List
    res = client.get('/api/organizers')
    assert res.status_code == 200
    assert len(res.json['data']) >= 5
    print(f"[PASS] 5. Organizers List ({len(res.json['data'])} organizers)")

    # 6. Venues List
    res = client.get('/api/venues')
    assert res.status_code == 200
    assert len(res.json['data']) >= 5
    print(f"[PASS] 6. Venues List ({len(res.json['data'])} venues)")

    # 7. Categories List
    res = client.get('/api/categories')
    assert res.status_code == 200
    assert len(res.json['data']) >= 5
    print(f"[PASS] 7. Categories List ({len(res.json['data'])} categories)")

    # 8. Participants List
    res = client.get('/api/participants')
    assert res.status_code == 200
    assert len(res.json['data']) >= 8
    print(f"[PASS] 8. Participants List ({len(res.json['data'])} participants)")

    # 9. Registrations & Foreign Key Integrity
    res = client.get('/api/registrations')
    assert res.status_code == 200
    assert len(res.json['data']) >= 12
    print(f"[PASS] 9. Registrations List ({len(res.json['data'])} registrations)")

    # 10. Register participant for the newly created event
    new_reg = {
        "Participant_ID": 5,
        "Event_ID": created_evt_id,
        "Status": "Confirmed",
        "Amount": 100.0,
        "Payment_Status": "Completed"
    }
    res = client.post('/api/registrations', json=new_reg)
    assert res.status_code == 201, f"Registration failed: {res.data}"
    created_reg_id = res.json['registration_id']
    print(f"[PASS] 10. Registration #{created_reg_id} and Payment created successfully")

    # 11. Payments Summary
    res = client.get('/api/payments/summary')
    assert res.status_code == 200
    print(f"[PASS] 11. Payments Summary: Total Transactions = {res.json['data']['total_transactions']}")

    # 12. Reports (Event Report)
    res = client.get('/api/reports/event-report')
    assert res.status_code == 200
    assert len(res.json['data']) > 0
    print(f"[PASS] 12. SQL Event Report Generated ({len(res.json['data'])} rows)")

    # 13. Database Tables live inspection
    res = client.get('/api/database/tables/Event')
    assert res.status_code == 200
    meta = res.json['metadata']
    print(f"[PASS] 13. Live SQL Table Inspection for 'Event': {len(meta['columns'])} columns, {res.json['pagination']['total']} rows")

    # 14. SQL Query Execution Console (Safe SELECT)
    query_payload = {"query": "SELECT e.Event_Name, v.Venue_Name, v.Capacity FROM Event e JOIN Venue v ON e.Venue_ID = v.Venue_ID"}
    res = client.post('/api/admin/execute', json=query_payload)
    assert res.status_code == 200
    print(f"[PASS] 14. Admin SQL Query executed in {res.json['duration_ms']}ms returning {res.json['row_count']} rows")

    # 15. Destructive query prevention in SQL Query console
    hack_payload = {"query": "DROP TABLE Event"}
    res = client.post('/api/admin/execute', json=hack_payload)
    assert res.status_code == 403
    print("[PASS] 15. Security Safeguard: Prevented destructive SQL statement execution")

    # 16. Foreign Key Constraint Enforcement test on DELETE
    res = client.delete('/api/organizers/1')
    assert res.status_code == 400
    print("[PASS] 16. DBMS Foreign Key Constraint enforced on DELETE Organizer")

    print("\n>>> ALL 16 DBMS INTEGRATION TESTS PASSED WITH 100% SUCCESS! <<<\n")

if __name__ == '__main__':
    run_tests()
