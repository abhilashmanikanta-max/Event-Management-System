from flask import Blueprint, request, jsonify
from backend.database.db import db
import re

organizers_bp = Blueprint('organizers', __name__)

@organizers_bp.route('/api/organizers', methods=['GET'])
def get_organizers():
    try:
        search = request.args.get('search', '').strip()
        where_sql = ""
        params = []

        if search:
            where_sql = "WHERE o.Name LIKE ? OR o.Email LIKE ? OR o.Phone LIKE ?"
            wildcard = f"%{search}%"
            params.extend([wildcard, wildcard, wildcard])

        query = f"""
            SELECT 
                o.Organizer_ID,
                o.Name,
                o.Email,
                o.Phone,
                COUNT(e.Event_ID) AS Total_Events
            FROM Organizer o
            LEFT JOIN Event e ON o.Organizer_ID = e.Organizer_ID
            {where_sql}
            GROUP BY o.Organizer_ID, o.Name, o.Email, o.Phone
            ORDER BY o.Organizer_ID ASC
        """
        rows = db.fetch_all(query, params)
        return jsonify({"status": "success", "data": rows}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@organizers_bp.route('/api/organizers/<int:org_id>', methods=['GET'])
def get_organizer_details(org_id):
    try:
        org = db.fetch_one("SELECT * FROM Organizer WHERE Organizer_ID = ?", (org_id,))
        if not org:
            return jsonify({"status": "error", "message": "Organizer not found."}), 404

        events = db.fetch_all("""
            SELECT 
                e.Event_ID, e.Event_Name, e.Date, e.Time,
                v.Venue_Name, c.Category_Name
            FROM Event e
            JOIN Venue v ON e.Venue_ID = v.Venue_ID
            JOIN Category c ON e.Category_ID = c.Category_ID
            WHERE e.Organizer_ID = ?
            ORDER BY e.Date ASC
        """, (org_id,))

        org['events'] = events
        return jsonify({"status": "success", "data": org}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@organizers_bp.route('/api/organizers', methods=['POST'])
def create_organizer():
    try:
        data = request.get_json() or {}
        name = data.get('Name', '').strip()
        email = data.get('Email', '').strip()
        phone = data.get('Phone', '').strip()

        if not name:
            return jsonify({"status": "error", "message": "Organizer Name is required."}), 400
        if not email or '@' not in email:
            return jsonify({"status": "error", "message": "A valid Email address is required."}), 400
        if not phone:
            return jsonify({"status": "error", "message": "Phone number is required."}), 400

        res = db.execute(
            "INSERT INTO Organizer (Name, Email, Phone) VALUES (?, ?, ?)",
            (name, email, phone)
        )
        return jsonify({
            "status": "success",
            "message": "Organizer created successfully.",
            "organizer_id": res['lastrowid']
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@organizers_bp.route('/api/organizers/<int:org_id>', methods=['PUT'])
def update_organizer(org_id):
    try:
        data = request.get_json() or {}
        name = data.get('Name', '').strip()
        email = data.get('Email', '').strip()
        phone = data.get('Phone', '').strip()

        if not db.fetch_one("SELECT 1 FROM Organizer WHERE Organizer_ID = ?", (org_id,)):
            return jsonify({"status": "error", "message": "Organizer not found."}), 404

        if not name or not email or '@' not in email or not phone:
            return jsonify({"status": "error", "message": "Name, valid Email, and Phone are required."}), 400

        db.execute(
            "UPDATE Organizer SET Name = ?, Email = ?, Phone = ? WHERE Organizer_ID = ?",
            (name, email, phone, org_id)
        )
        return jsonify({"status": "success", "message": "Organizer updated successfully."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@organizers_bp.route('/api/organizers/<int:org_id>', methods=['DELETE'])
def delete_organizer(org_id):
    try:
        org = db.fetch_one("SELECT Name FROM Organizer WHERE Organizer_ID = ?", (org_id,))
        if not org:
            return jsonify({"status": "error", "message": "Organizer not found."}), 404

        # Enforce foreign key check
        event_cnt = db.fetch_one("SELECT COUNT(*) AS c FROM Event WHERE Organizer_ID = ?", (org_id,))['c']
        if event_cnt > 0:
            return jsonify({
                "status": "error",
                "message": f"Cannot delete organizer '{org['Name']}' because {event_cnt} event(s) are associated with it."
            }), 400

        db.execute("DELETE FROM Organizer WHERE Organizer_ID = ?", (org_id,))
        return jsonify({"status": "success", "message": f"Organizer '{org['Name']}' deleted successfully."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
