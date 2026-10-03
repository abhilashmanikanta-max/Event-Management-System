import time
import re
from flask import Blueprint, request, jsonify
from backend.database.db import db

query_bp = Blueprint('query', __name__)

PRESET_QUERIES = [
    {
        "id": "q1",
        "title": "1. Multi-Table Join: Full Event Catalog",
        "description": "Inner joins 4 tables (Event, Organizer, Venue, Category) to produce a master event schedule.",
        "sql": """SELECT 
    e.Event_ID,
    e.Event_Name,
    e.Date,
    e.Time,
    o.Name AS Organizer_Name,
    v.Venue_Name,
    v.Capacity,
    c.Category_Name
FROM Event e
INNER JOIN Organizer o ON e.Organizer_ID = o.Organizer_ID
INNER JOIN Venue v ON e.Venue_ID = v.Venue_ID
INNER JOIN Category c ON e.Category_ID = c.Category_ID
ORDER BY e.Date ASC;"""
    },
    {
        "id": "q2",
        "title": "2. Aggregate with Left Join & Group By: Event Revenue",
        "description": "Calculates attendance count and gross revenue per event using SUM and COUNT aggregations.",
        "sql": """SELECT 
    e.Event_ID,
    e.Event_Name,
    v.Capacity,
    COUNT(r.Registration_ID) AS Total_Registered,
    ROUND((COUNT(r.Registration_ID) * 100.0 / v.Capacity), 1) AS Occupancy_Pct,
    COALESCE(SUM(p.Amount), 0) AS Total_Revenue
FROM Event e
JOIN Venue v ON e.Venue_ID = v.Venue_ID
LEFT JOIN Registration r ON e.Event_ID = r.Event_ID AND r.Status != 'Cancelled'
LEFT JOIN Payment p ON r.Registration_ID = p.Registration_ID AND p.Payment_Status = 'Completed'
GROUP BY e.Event_ID, e.Event_Name, v.Capacity
ORDER BY Total_Revenue DESC;"""
    },
    {
        "id": "q3",
        "title": "3. 5-Table Join: Complete Participant Audit",
        "description": "Joins Participant, Registration, Event, Venue, and Payment to trace every registration to its payment.",
        "sql": """SELECT 
    p.Name AS Participant,
    e.Event_Name,
    v.Venue_Name,
    r.Registration_Date,
    r.Status AS Reg_Status,
    COALESCE(pay.Amount, 0) AS Amount_Paid,
    COALESCE(pay.Payment_Status, 'Unpaid') AS Payment_Status
FROM Participant p
JOIN Registration r ON p.Participant_ID = r.Participant_ID
JOIN Event e ON r.Event_ID = e.Event_ID
JOIN Venue v ON e.Venue_ID = v.Venue_ID
LEFT JOIN Payment pay ON r.Registration_ID = pay.Registration_ID
ORDER BY r.Registration_Date DESC;"""
    },
    {
        "id": "q4",
        "title": "4. Group By with HAVING Filter: Category Analysis",
        "description": "Groups events by Category and filters only categories with at least 1 registered event.",
        "sql": """SELECT 
    c.Category_Name,
    COUNT(DISTINCT e.Event_ID) AS Event_Count,
    COUNT(r.Registration_ID) AS Registrations,
    COALESCE(SUM(p.Amount), 0) AS Revenue
FROM Category c
LEFT JOIN Event e ON c.Category_ID = e.Category_ID
LEFT JOIN Registration r ON e.Event_ID = r.Event_ID
LEFT JOIN Payment p ON r.Registration_ID = p.Registration_ID AND p.Payment_Status = 'Completed'
GROUP BY c.Category_ID, c.Category_Name
HAVING COUNT(DISTINCT e.Event_ID) > 0
ORDER BY Revenue DESC;"""
    },
    {
        "id": "q5",
        "title": "5. Subquery (IN): High-Capacity Event Registrants",
        "description": "Finds participants registered in events hosted in large venues (>400 capacity) using a subquery.",
        "sql": """SELECT 
    Participant_ID, 
    Name, 
    Email, 
    Phone 
FROM Participant
WHERE Participant_ID IN (
    SELECT DISTINCT r.Participant_ID
    FROM Registration r
    JOIN Event e ON r.Event_ID = e.Event_ID
    JOIN Venue v ON e.Venue_ID = v.Venue_ID
    WHERE v.Capacity > 400
);"""
    },
    {
        "id": "q6",
        "title": "6. Correlated Subquery: Above-Average Popularity Events",
        "description": "Demonstrates nested subqueries comparing event registration counts to the overall average.",
        "sql": """SELECT 
    e.Event_ID,
    e.Event_Name,
    (SELECT COUNT(*) FROM Registration r WHERE r.Event_ID = e.Event_ID) AS Registrations
FROM Event e
WHERE (SELECT COUNT(*) FROM Registration r WHERE r.Event_ID = e.Event_ID) >= (
    SELECT AVG(reg_count)
    FROM (
        SELECT COUNT(*) AS reg_count 
        FROM Registration 
        GROUP BY Event_ID
    )
);"""
    },
    {
        "id": "q7",
        "title": "7. Payment Status Reconciliation",
        "description": "Breakdown of total transaction counts and monetary sums per payment status.",
        "sql": """SELECT 
    Payment_Status,
    COUNT(*) AS Total_Transactions,
    ROUND(SUM(Amount), 2) AS Sum_Amount,
    ROUND(AVG(Amount), 2) AS Average_Amount
FROM Payment
GROUP BY Payment_Status
ORDER BY Sum_Amount DESC;"""
    },
    {
        "id": "q8",
        "title": "8. Venue Utilization & Capacity Analysis",
        "description": "Analyzes capacity utilization percentage across all venues.",
        "sql": """SELECT 
    v.Venue_ID,
    v.Venue_Name,
    v.Capacity,
    COUNT(DISTINCT e.Event_ID) AS Events_Conducted,
    COUNT(r.Registration_ID) AS Total_Attendees,
    ROUND((COUNT(r.Registration_ID) * 100.0 / v.Capacity), 1) AS Utilization_Pct
FROM Venue v
LEFT JOIN Event e ON v.Venue_ID = e.Venue_ID
LEFT JOIN Registration r ON e.Event_ID = r.Event_ID AND r.Status = 'Confirmed'
GROUP BY v.Venue_ID, v.Venue_Name, v.Capacity
ORDER BY Utilization_Pct DESC;"""
    }
]

DISALLOWED_PATTERN = re.compile(
    r'\b(DROP|TRUNCATE|ALTER|DELETE|UPDATE|INSERT|REPLACE|ATTACH|DETACH|PRAGMA\s+writable_schema)\b',
    re.IGNORECASE
)

@query_bp.route('/api/admin/presets', methods=['GET'])
def get_presets():
    return jsonify({"status": "success", "presets": PRESET_QUERIES}), 200

@query_bp.route('/api/admin/execute', methods=['POST'])
def execute_query():
    try:
        data = request.get_json() or {}
        raw_sql = data.get('query', '').strip()

        if not raw_sql:
            return jsonify({"status": "error", "message": "SQL query cannot be empty."}), 400

        # Remove trailing semicolons
        clean_sql = raw_sql.rstrip(';')

        # Check for disallowed destructive queries for security
        first_word = clean_sql.split()[0].upper() if clean_sql.split() else ''
        if first_word not in ('SELECT', 'WITH', 'EXPLAIN'):
            return jsonify({
                "status": "error",
                "message": (
                    "Security Policy: The interactive SQL Query console only permits SELECT, WITH, "
                    "and EXPLAIN queries for safe demonstration. To modify or insert data, please use "
                    "the dedicated management interfaces (Events, Organizers, etc.) or REST API endpoints."
                )
            }), 403

        if DISALLOWED_PATTERN.search(clean_sql):
            return jsonify({
                "status": "error",
                "message": "Destructive or schema-altering SQL statements are restricted in this console."
            }), 403

        # Execute and measure time
        start_time = time.perf_counter()
        rows = db.fetch_all(clean_sql)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        columns = list(rows[0].keys()) if rows else []

        return jsonify({
            "status": "success",
            "query": clean_sql,
            "duration_ms": duration_ms,
            "row_count": len(rows),
            "columns": columns,
            "data": rows[:500]  # Cap preview at 500 rows for browser performance
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
