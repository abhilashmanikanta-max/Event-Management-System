import csv
import io
from flask import Blueprint, request, jsonify, Response
from backend.database.db import db

reports_bp = Blueprint('reports', __name__)

REPORTS_CONFIG = {
    'event-report': {
        'title': 'Comprehensive Event & Attendance Report',
        'query': """
            SELECT 
                e.Event_ID,
                e.Event_Name,
                e.Date AS Event_Date,
                e.Time AS Event_Time,
                o.Name AS Organizer_Name,
                v.Venue_Name,
                v.Capacity,
                c.Category_Name,
                COUNT(r.Registration_ID) AS Total_Registrations,
                COUNT(CASE WHEN r.Status = 'Confirmed' THEN 1 END) AS Confirmed_Attendees,
                COALESCE(SUM(p.Amount), 0) AS Total_Revenue
            FROM Event e
            JOIN Organizer o ON e.Organizer_ID = o.Organizer_ID
            JOIN Venue v ON e.Venue_ID = v.Venue_ID
            JOIN Category c ON e.Category_ID = c.Category_ID
            LEFT JOIN Registration r ON e.Event_ID = r.Event_ID
            LEFT JOIN Payment p ON r.Registration_ID = p.Registration_ID AND p.Payment_Status = 'Completed'
            GROUP BY e.Event_ID, e.Event_Name, e.Date, e.Time, o.Name, v.Venue_Name, v.Capacity, c.Category_Name
            ORDER BY e.Date ASC
        """
    },
    'participant-report': {
        'title': 'Participant Registration & History Report',
        'query': """
            SELECT 
                p.Participant_ID,
                p.Name AS Participant_Name,
                p.Email AS Participant_Email,
                p.Phone AS Participant_Phone,
                COUNT(r.Registration_ID) AS Events_Registered,
                COUNT(CASE WHEN r.Status = 'Confirmed' THEN 1 END) AS Confirmed_Events,
                COALESCE(SUM(pay.Amount), 0) AS Total_Fees_Paid
            FROM Participant p
            LEFT JOIN Registration r ON p.Participant_ID = r.Participant_ID
            LEFT JOIN Payment pay ON r.Registration_ID = pay.Registration_ID AND pay.Payment_Status = 'Completed'
            GROUP BY p.Participant_ID, p.Name, p.Email, p.Phone
            ORDER BY Events_Registered DESC
        """
    },
    'payment-report': {
        'title': 'Financial & Payment Reconciliation Report',
        'query': """
            SELECT 
                pay.Payment_ID,
                pay.Payment_Date,
                pay.Amount,
                pay.Payment_Status,
                r.Registration_ID,
                r.Status AS Registration_Status,
                p.Name AS Participant_Name,
                p.Email AS Participant_Email,
                e.Event_Name
            FROM Payment pay
            JOIN Registration r ON pay.Registration_ID = r.Registration_ID
            JOIN Participant p ON r.Participant_ID = p.Participant_ID
            JOIN Event e ON r.Event_ID = e.Event_ID
            ORDER BY pay.Payment_Date DESC
        """
    },
    'organizer-report': {
        'title': 'Organizer Performance & Activity Report',
        'query': """
            SELECT 
                o.Organizer_ID,
                o.Name AS Organizer_Name,
                o.Email,
                o.Phone,
                COUNT(DISTINCT e.Event_ID) AS Total_Events_Hosted,
                COUNT(r.Registration_ID) AS Total_Registrations,
                COALESCE(SUM(p.Amount), 0) AS Gross_Revenue_Generated
            FROM Organizer o
            LEFT JOIN Event e ON o.Organizer_ID = e.Organizer_ID
            LEFT JOIN Registration r ON e.Event_ID = r.Event_ID
            LEFT JOIN Payment p ON r.Registration_ID = p.Registration_ID AND p.Payment_Status = 'Completed'
            GROUP BY o.Organizer_ID, o.Name, o.Email, o.Phone
            ORDER BY Total_Events_Hosted DESC
        """
    },
    'venue-report': {
        'title': 'Venue Usage & Utilization Report',
        'query': """
            SELECT 
                v.Venue_ID,
                v.Venue_Name,
                v.Location,
                v.Capacity,
                COUNT(DISTINCT e.Event_ID) AS Events_Conducted,
                COUNT(r.Registration_ID) AS Total_Attendees,
                ROUND((COUNT(r.Registration_ID) * 100.0 / v.Capacity), 1) AS Utilization_Rate_Pct
            FROM Venue v
            LEFT JOIN Event e ON v.Venue_ID = e.Venue_ID
            LEFT JOIN Registration r ON e.Event_ID = r.Event_ID AND r.Status = 'Confirmed'
            GROUP BY v.Venue_ID, v.Venue_Name, v.Location, v.Capacity
            ORDER BY Events_Conducted DESC
        """
    },
    'category-report': {
        'title': 'Category-wise Event & Revenue Breakdown',
        'query': """
            SELECT 
                c.Category_ID,
                c.Category_Name,
                c.Description,
                COUNT(DISTINCT e.Event_ID) AS Total_Events,
                COUNT(r.Registration_ID) AS Total_Registrations,
                COALESCE(SUM(p.Amount), 0) AS Total_Revenue
            FROM Category c
            LEFT JOIN Event e ON c.Category_ID = e.Category_ID
            LEFT JOIN Registration r ON e.Event_ID = r.Event_ID
            LEFT JOIN Payment p ON r.Registration_ID = p.Registration_ID AND p.Payment_Status = 'Completed'
            GROUP BY c.Category_ID, c.Category_Name, c.Description
            ORDER BY Total_Events DESC
        """
    },
    'upcoming-events-report': {
        'title': 'Upcoming Scheduled Events Report',
        'query': """
            SELECT 
                e.Event_ID,
                e.Event_Name,
                e.Date AS Scheduled_Date,
                e.Time AS Scheduled_Time,
                o.Name AS Organizer_Name,
                v.Venue_Name,
                v.Location,
                c.Category_Name,
                COUNT(r.Registration_ID) AS Confirmed_Seats
            FROM Event e
            JOIN Organizer o ON e.Organizer_ID = o.Organizer_ID
            JOIN Venue v ON e.Venue_ID = v.Venue_ID
            JOIN Category c ON e.Category_ID = c.Category_ID
            LEFT JOIN Registration r ON e.Event_ID = r.Event_ID AND r.Status = 'Confirmed'
            GROUP BY e.Event_ID, e.Event_Name, e.Date, e.Time, o.Name, v.Venue_Name, v.Location, c.Category_Name
            ORDER BY e.Date ASC
        """
    }
}

@reports_bp.route('/api/reports/<report_type>', methods=['GET'])
def get_report(report_type):
    try:
        if report_type not in REPORTS_CONFIG:
            return jsonify({"status": "error", "message": f"Invalid report type '{report_type}'."}), 404

        cfg = REPORTS_CONFIG[report_type]
        rows = db.fetch_all(cfg['query'])

        # Check if CSV export requested
        export_format = request.args.get('format', '').lower()
        if export_format == 'csv':
            if not rows:
                return Response("", mimetype="text/csv", headers={"Content-Disposition": f"attachment;filename={report_type}.csv"})

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment;filename={report_type}.csv"}
            )

        return jsonify({
            "status": "success",
            "report_key": report_type,
            "title": cfg['title'],
            "columns": list(rows[0].keys()) if rows else [],
            "total_rows": len(rows),
            "data": rows
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
