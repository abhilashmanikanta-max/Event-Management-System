from flask import Blueprint, request, jsonify
from datetime import datetime
from backend.database.db import db

registrations_bp = Blueprint('registrations', __name__)

@registrations_bp.route('/api/registrations', methods=['GET'])
def get_registrations():
    try:
        search = request.args.get('search', '').strip()
        event_id = request.args.get('event_id', '').strip()
        status_filter = request.args.get('status', '').strip()

        where_clauses = []
        params = []

        if search:
            where_clauses.append("(p.Name LIKE ? OR p.Email LIKE ? OR e.Event_Name LIKE ?)")
            wildcard = f"%{search}%"
            params.extend([wildcard, wildcard, wildcard])

        if event_id:
            where_clauses.append("r.Event_ID = ?")
            params.append(int(event_id))

        if status_filter:
            where_clauses.append("r.Status = ?")
            params.append(status_filter)

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        query = f"""
            SELECT 
                r.Registration_ID,
                r.Registration_Date,
                r.Status,
                p.Participant_ID,
                p.Name AS Participant_Name,
                p.Email AS Participant_Email,
                e.Event_ID,
                e.Event_Name,
                e.Date AS Event_Date,
                e.Time AS Event_Time,
                pay.Payment_ID,
                pay.Amount AS Payment_Amount,
                COALESCE(pay.Payment_Status, 'Unpaid') AS Payment_Status
            FROM Registration r
            JOIN Participant p ON r.Participant_ID = p.Participant_ID
            JOIN Event e ON r.Event_ID = e.Event_ID
            LEFT JOIN Payment pay ON r.Registration_ID = pay.Registration_ID
            {where_sql}
            ORDER BY r.Registration_ID DESC
        """
        rows = db.fetch_all(query, params)
        return jsonify({"status": "success", "data": rows}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@registrations_bp.route('/api/registrations/<int:reg_id>', methods=['GET'])
def get_registration_details(reg_id):
    try:
        query = """
            SELECT 
                r.Registration_ID,
                r.Registration_Date,
                r.Status,
                p.Participant_ID,
                p.Name AS Participant_Name,
                p.Email AS Participant_Email,
                p.Phone AS Participant_Phone,
                e.Event_ID,
                e.Event_Name,
                e.Date AS Event_Date,
                e.Time AS Event_Time,
                v.Venue_Name,
                v.Location AS Venue_Location,
                pay.Payment_ID,
                pay.Amount AS Payment_Amount,
                pay.Payment_Date,
                pay.Payment_Status
            FROM Registration r
            JOIN Participant p ON r.Participant_ID = p.Participant_ID
            JOIN Event e ON r.Event_ID = e.Event_ID
            JOIN Venue v ON e.Venue_ID = v.Venue_ID
            LEFT JOIN Payment pay ON r.Registration_ID = pay.Registration_ID
            WHERE r.Registration_ID = ?
        """
        record = db.fetch_one(query, (reg_id,))
        if not record:
            return jsonify({"status": "error", "message": "Registration not found."}), 404

        return jsonify({"status": "success", "data": record}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@registrations_bp.route('/api/registrations', methods=['POST'])
def create_registration():
    try:
        data = request.get_json() or {}
        participant_id = data.get('Participant_ID')
        event_id = data.get('Event_ID')
        status_val = data.get('Status', 'Confirmed').strip()
        reg_date = data.get('Registration_Date', '').strip() or datetime.now().strftime('%Y-%m-%d')

        if not participant_id or not event_id:
            return jsonify({"status": "error", "message": "Participant and Event must be selected."}), 400

        # Check participant existence
        part = db.fetch_one("SELECT Name FROM Participant WHERE Participant_ID = ?", (participant_id,))
        if not part:
            return jsonify({"status": "error", "message": "Selected Participant does not exist."}), 400

        # Check event existence
        evt = db.fetch_one("SELECT Event_Name, Venue_ID FROM Event WHERE Event_ID = ?", (event_id,))
        if not evt:
            return jsonify({"status": "error", "message": "Selected Event does not exist."}), 400

        # Check duplicate registration constraint
        existing = db.fetch_one(
            "SELECT Registration_ID FROM Registration WHERE Participant_ID = ? AND Event_ID = ?",
            (participant_id, event_id)
        )
        if existing:
            return jsonify({
                "status": "error",
                "message": f"Participant '{part['Name']}' is already registered for event '{evt['Event_Name']}'."
            }), 400

        # Check venue capacity
        cap_info = db.fetch_one("""
            SELECT v.Capacity, COUNT(r.Registration_ID) AS current_regs
            FROM Event e
            JOIN Venue v ON e.Venue_ID = v.Venue_ID
            LEFT JOIN Registration r ON e.Event_ID = r.Event_ID AND r.Status != 'Cancelled'
            WHERE e.Event_ID = ?
            GROUP BY v.Capacity
        """, (event_id,))
        if cap_info and cap_info['current_regs'] >= cap_info['Capacity']:
            return jsonify({
                "status": "error",
                "message": f"Venue capacity reached ({cap_info['Capacity']} attendees maximum). Cannot accept new registrations."
            }), 400

        # Insert Registration
        insert_query = """
            INSERT INTO Registration (Participant_ID, Event_ID, Registration_Date, Status)
            VALUES (?, ?, ?, ?)
        """
        res = db.execute(insert_query, (participant_id, event_id, reg_date, status_val))
        reg_id = res['lastrowid']

        # Optional initial payment creation if specified
        amount = data.get('Amount')
        if amount is not None and float(amount) > 0:
            payment_status = data.get('Payment_Status', 'Completed')
            pay_date = reg_date
            db.execute(
                "INSERT INTO Payment (Registration_ID, Amount, Payment_Date, Payment_Status) VALUES (?, ?, ?, ?)",
                (reg_id, float(amount), pay_date, payment_status)
            )

        return jsonify({
            "status": "success",
            "message": f"Participant '{part['Name']}' registered successfully for '{evt['Event_Name']}'!",
            "registration_id": reg_id
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@registrations_bp.route('/api/registrations/<int:reg_id>', methods=['PUT'])
def update_registration(reg_id):
    try:
        data = request.get_json() or {}
        new_status = data.get('Status', '').strip()

        if new_status not in ('Confirmed', 'Pending', 'Cancelled'):
            return jsonify({"status": "error", "message": "Status must be 'Confirmed', 'Pending', or 'Cancelled'."}), 400

        if not db.fetch_one("SELECT 1 FROM Registration WHERE Registration_ID = ?", (reg_id,)):
            return jsonify({"status": "error", "message": "Registration not found."}), 404

        db.execute("UPDATE Registration SET Status = ? WHERE Registration_ID = ?", (new_status, reg_id))
        return jsonify({"status": "success", "message": f"Registration status updated to '{new_status}'."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@registrations_bp.route('/api/registrations/<int:reg_id>/cancel', methods=['POST'])
def cancel_registration(reg_id):
    try:
        reg = db.fetch_one("SELECT Status FROM Registration WHERE Registration_ID = ?", (reg_id,))
        if not reg:
            return jsonify({"status": "error", "message": "Registration not found."}), 404

        db.execute("UPDATE Registration SET Status = 'Cancelled' WHERE Registration_ID = ?", (reg_id,))
        return jsonify({"status": "success", "message": "Registration marked as Cancelled."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@registrations_bp.route('/api/registrations/<int:reg_id>', methods=['DELETE'])
def delete_registration(reg_id):
    try:
        if not db.fetch_one("SELECT 1 FROM Registration WHERE Registration_ID = ?", (reg_id,)):
            return jsonify({"status": "error", "message": "Registration not found."}), 404

        # Check if payment exists
        pay_cnt = db.fetch_one("SELECT COUNT(*) AS c FROM Payment WHERE Registration_ID = ?", (reg_id,))['c']
        if pay_cnt > 0:
            return jsonify({
                "status": "error",
                "message": "Cannot delete registration because an associated payment record exists. Delete or refund the payment record first, or cancel the registration."
            }), 400

        db.execute("DELETE FROM Registration WHERE Registration_ID = ?", (reg_id,))
        return jsonify({"status": "success", "message": "Registration deleted successfully."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
