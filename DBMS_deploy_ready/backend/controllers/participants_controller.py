from flask import Blueprint, request, jsonify
from backend.database.db import db

participants_bp = Blueprint('participants', __name__)

@participants_bp.route('/api/participants', methods=['GET'])
def get_participants():
    try:
        search = request.args.get('search', '').strip()
        where_sql = ""
        params = []

        if search:
            where_sql = "WHERE p.Name LIKE ? OR p.Email LIKE ? OR p.Phone LIKE ?"
            wildcard = f"%{search}%"
            params.extend([wildcard, wildcard, wildcard])

        query = f"""
            SELECT 
                p.Participant_ID,
                p.Name,
                p.Email,
                p.Phone,
                COUNT(r.Registration_ID) AS Total_Registrations
            FROM Participant p
            LEFT JOIN Registration r ON p.Participant_ID = r.Participant_ID
            {where_sql}
            GROUP BY p.Participant_ID, p.Name, p.Email, p.Phone
            ORDER BY p.Participant_ID ASC
        """
        rows = db.fetch_all(query, params)
        return jsonify({"status": "success", "data": rows}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@participants_bp.route('/api/participants/<int:part_id>', methods=['GET'])
def get_participant_details(part_id):
    try:
        part = db.fetch_one("SELECT * FROM Participant WHERE Participant_ID = ?", (part_id,))
        if not part:
            return jsonify({"status": "error", "message": "Participant not found."}), 404

        registrations = db.fetch_all("""
            SELECT 
                r.Registration_ID,
                r.Registration_Date,
                r.Status AS Registration_Status,
                e.Event_ID,
                e.Event_Name,
                e.Date AS Event_Date,
                e.Time AS Event_Time,
                v.Venue_Name,
                pay.Payment_ID,
                pay.Amount,
                pay.Payment_Status
            FROM Registration r
            JOIN Event e ON r.Event_ID = e.Event_ID
            JOIN Venue v ON e.Venue_ID = v.Venue_ID
            LEFT JOIN Payment pay ON r.Registration_ID = pay.Registration_ID
            WHERE r.Participant_ID = ?
            ORDER BY r.Registration_Date DESC
        """, (part_id,))

        part['registrations'] = registrations
        return jsonify({"status": "success", "data": part}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@participants_bp.route('/api/participants', methods=['POST'])
def create_participant():
    try:
        data = request.get_json() or {}
        name = data.get('Name', '').strip()
        email = data.get('Email', '').strip()
        phone = data.get('Phone', '').strip()

        if not name:
            return jsonify({"status": "error", "message": "Participant Name is required."}), 400
        if not email or '@' not in email:
            return jsonify({"status": "error", "message": "A valid Email address is required."}), 400
        if not phone:
            return jsonify({"status": "error", "message": "Phone number is required."}), 400

        res = db.execute(
            "INSERT INTO Participant (Name, Email, Phone) VALUES (?, ?, ?)",
            (name, email, phone)
        )
        return jsonify({
            "status": "success",
            "message": "Participant registered successfully.",
            "participant_id": res['lastrowid']
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@participants_bp.route('/api/participants/<int:part_id>', methods=['PUT'])
def update_participant(part_id):
    try:
        data = request.get_json() or {}
        name = data.get('Name', '').strip()
        email = data.get('Email', '').strip()
        phone = data.get('Phone', '').strip()

        if not db.fetch_one("SELECT 1 FROM Participant WHERE Participant_ID = ?", (part_id,)):
            return jsonify({"status": "error", "message": "Participant not found."}), 404

        if not name or not email or '@' not in email or not phone:
            return jsonify({"status": "error", "message": "Name, valid Email, and Phone are required."}), 400

        db.execute(
            "UPDATE Participant SET Name = ?, Email = ?, Phone = ? WHERE Participant_ID = ?",
            (name, email, phone, part_id)
        )
        return jsonify({"status": "success", "message": "Participant updated successfully."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@participants_bp.route('/api/participants/<int:part_id>', methods=['DELETE'])
def delete_participant(part_id):
    try:
        part = db.fetch_one("SELECT Name FROM Participant WHERE Participant_ID = ?", (part_id,))
        if not part:
            return jsonify({"status": "error", "message": "Participant not found."}), 404

        reg_cnt = db.fetch_one("SELECT COUNT(*) AS c FROM Registration WHERE Participant_ID = ?", (part_id,))['c']
        if reg_cnt > 0:
            return jsonify({
                "status": "error",
                "message": f"Cannot delete participant '{part['Name']}' because they have {reg_cnt} active event registration(s)."
            }), 400

        db.execute("DELETE FROM Participant WHERE Participant_ID = ?", (part_id,))
        return jsonify({"status": "success", "message": f"Participant '{part['Name']}' deleted successfully."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
