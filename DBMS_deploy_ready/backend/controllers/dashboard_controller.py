from flask import Blueprint, jsonify
from backend.database.db import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        # 1. Total Counts directly from SQL
        events_cnt = db.fetch_one("SELECT COUNT(*) AS c FROM Event")['c']
        organizers_cnt = db.fetch_one("SELECT COUNT(*) AS c FROM Organizer")['c']
        venues_cnt = db.fetch_one("SELECT COUNT(*) AS c FROM Venue")['c']
        categories_cnt = db.fetch_one("SELECT COUNT(*) AS c FROM Category")['c']
        participants_cnt = db.fetch_one("SELECT COUNT(*) AS c FROM Participant")['c']
        registrations_cnt = db.fetch_one("SELECT COUNT(*) AS c FROM Registration")['c']
        
        pay_stats = db.fetch_one("SELECT COUNT(*) AS c, COALESCE(SUM(Amount), 0) AS total FROM Payment")
        payments_cnt = pay_stats['c']
        total_revenue = float(pay_stats['total'])

        # 2. Events by Category (SQL GROUP BY)
        events_by_category = db.fetch_all("""
            SELECT 
                c.Category_Name AS category,
                COUNT(e.Event_ID) AS count
            FROM Category c
            LEFT JOIN Event e ON c.Category_ID = e.Category_ID
            GROUP BY c.Category_ID, c.Category_Name
            ORDER BY count DESC
        """)

        # 3. Registrations per Event (SQL GROUP BY)
        regs_per_event = db.fetch_all("""
            SELECT 
                e.Event_Name AS event_name,
                COUNT(r.Registration_ID) AS registrations
            FROM Event e
            LEFT JOIN Registration r ON e.Event_ID = r.Event_ID
            GROUP BY e.Event_ID, e.Event_Name
            ORDER BY registrations DESC
            LIMIT 7
        """)

        # 4. Payment Status Distribution (SQL GROUP BY)
        payment_status_dist = db.fetch_all("""
            SELECT 
                Payment_Status AS status,
                COUNT(*) AS count,
                COALESCE(SUM(Amount), 0) AS total_amount
            FROM Payment
            GROUP BY Payment_Status
        """)

        # 5. Upcoming Events with 4-Table JOIN
        upcoming_events = db.fetch_all("""
            SELECT 
                e.Event_ID,
                e.Event_Name,
                e.Date,
                e.Time,
                o.Name AS Organizer_Name,
                v.Venue_Name,
                c.Category_Name
            FROM Event e
            JOIN Organizer o ON e.Organizer_ID = o.Organizer_ID
            JOIN Venue v ON e.Venue_ID = v.Venue_ID
            JOIN Category c ON e.Category_ID = c.Category_ID
            ORDER BY e.Date ASC
            LIMIT 5
        """)

        # 6. Venue Utilization (SQL Aggregation + Capacity %)
        venue_utilization = db.fetch_all("""
            SELECT 
                v.Venue_Name AS venue_name,
                v.Capacity AS capacity,
                COUNT(DISTINCT e.Event_ID) AS events_hosted,
                COUNT(r.Registration_ID) AS total_attendees,
                ROUND((COUNT(r.Registration_ID) * 100.0 / v.Capacity), 1) AS utilization_rate
            FROM Venue v
            LEFT JOIN Event e ON v.Venue_ID = e.Venue_ID
            LEFT JOIN Registration r ON e.Event_ID = r.Event_ID AND r.Status = 'Confirmed'
            GROUP BY v.Venue_ID, v.Venue_Name, v.Capacity
            ORDER BY total_attendees DESC
        """)

        return jsonify({
            "status": "success",
            "counts": {
                "events": events_cnt,
                "organizers": organizers_cnt,
                "venues": venues_cnt,
                "categories": categories_cnt,
                "participants": participants_cnt,
                "registrations": registrations_cnt,
                "payments": payments_cnt,
                "total_revenue": total_revenue
            },
            "charts": {
                "events_by_category": events_by_category,
                "registrations_per_event": regs_per_event,
                "payment_status": payment_status_dist,
                "venue_utilization": venue_utilization
            },
            "upcoming_events": upcoming_events
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
