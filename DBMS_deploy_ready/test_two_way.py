import sqlite3
import urllib.request
import json

def test_two_way():
    print("=== TESTING TWO-WAY SQL INTERACTION ===")

    # 1. Direct SQL Database INSERT
    conn = sqlite3.connect('database/event_management.db')
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO Organizer (Organizer_ID, Name, Email, Phone) VALUES (999, 'Direct SQL Injected Organizer', 'direct_sql@college.edu', '+1-555-9999')")
    conn.commit()
    conn.close()
    print("[STEP 1 SUCCESS] Inserted record directly into SQLite file with raw SQL: 'Direct SQL Injected Organizer'")

    # 2. Verify Website API retrieves it immediately
    req = urllib.request.Request("http://127.0.0.1:5000/api/database/tables/Organizer?search=Injected")
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        found_name = data['data'][0]['Name']
        print(f"[STEP 2 SUCCESS] Website API fetched directly from SQL: '{found_name}'")
        assert found_name == 'Direct SQL Injected Organizer'

    # 3. Create record through Website API
    payload = json.dumps({
        "Event_Name": "Website API Created Hackathon",
        "Date": "2026-12-28",
        "Time": "02:00 PM",
        "Organizer_ID": 1,
        "Venue_ID": 1,
        "Category_ID": 1
    }).encode('utf-8')
    post_req = urllib.request.Request(
        "http://127.0.0.1:5000/api/events",
        data=payload,
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(post_req) as response:
        post_data = json.loads(response.read().decode())
        event_id = post_data['event_id']
        print(f"[STEP 3 SUCCESS] Event created through Website HTTP API with ID #{event_id}")

    # 4. Verify record directly in raw SQL database file
    conn = sqlite3.connect('database/event_management.db')
    cur = conn.cursor()
    row = cur.execute("SELECT Event_ID, Event_Name, Date FROM Event WHERE Event_ID = ?", (event_id,)).fetchone()
    conn.close()
    print(f"[STEP 4 SUCCESS] Verified directly in SQLite database file: Event_ID={row[0]}, Name='{row[1]}', Date='{row[2]}'")
    assert row[1] == "Website API Created Hackathon"

    # Clean up test rows
    conn = sqlite3.connect('database/event_management.db')
    conn.execute("DELETE FROM Event WHERE Event_ID = ?", (event_id,))
    conn.execute("DELETE FROM Organizer WHERE Organizer_ID = 999")
    conn.commit()
    conn.close()
    print("[CLEANUP SUCCESS] Test rows cleaned up. Database is pristine.")

    print("\n>>> TWO-WAY SQL INTERACTION (SQL <-> WEBSITE) FULLY VERIFIED! <<<\n")

if __name__ == '__main__':
    test_two_way()
