from flask import Blueprint, request, jsonify
from datetime import datetime
from backend.database.db import db

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/api/payments', methods=['GET'])
def get_payments():
    try:
        search = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '').strip()

        where_clauses = []
        params = []

        if search:
            where_clauses.append("(p.Name LIKE ? OR e.Event_Name LIKE ? OR CAST(pay.Payment_ID AS TEXT) LIKE ?)")
            wildcard = f"%{search}%"
            params.extend([wildcard, wildcard, wildcard])

        if status_filter:
            where_clauses.append("pay.Payment_Status = ?")
            params.append(status_filter)

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        query = f"""
            SELECT 
                pay.Payment_ID,
                pay.Registration_ID,
                pay.Amount,
                pay.Payment_Date,
                pay.Payment_Status,
                p.Participant_ID,
                p.Name AS Participant_Name,
                p.Email AS Participant_Email,
                e.Event_ID,
                e.Event_Name
            FROM Payment pay
            JOIN Registration r ON pay.Registration_ID = r.Registration_ID
            JOIN Participant p ON r.Participant_ID = p.Participant_ID
            JOIN Event e ON r.Event_ID = e.Event_ID
            {where_sql}
            ORDER BY pay.Payment_ID DESC
        """
        rows = db.fetch_all(query, params)
        return jsonify({"status": "success", "data": rows}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@payments_bp.route('/api/payments/summary', methods=['GET'])
def get_payment_summary():
    try:
        # Total amount and status counts calculated in SQL
        stats = db.fetch_one("""
            SELECT 
                COUNT(*) AS total_transactions,
                COALESCE(SUM(Amount), 0) AS total_amount,
                COALESCE(SUM(CASE WHEN Payment_Status = 'Completed' THEN Amount ELSE 0 END), 0) AS completed_amount,
                COUNT(CASE WHEN Payment_Status = 'Completed' THEN 1 END) AS completed_count,
                COUNT(CASE WHEN Payment_Status = 'Pending' THEN 1 END) AS pending_count,
                COUNT(CASE WHEN Payment_Status = 'Failed' THEN 1 END) AS failed_count
            FROM Payment
        """)
        return jsonify({"status": "success", "data": stats}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@payments_bp.route('/api/payments/<int:pay_id>', methods=['GET'])
def get_payment_details(pay_id):
    try:
        query = """
            SELECT 
                pay.Payment_ID,
                pay.Registration_ID,
                pay.Amount,
                pay.Payment_Date,
                pay.Payment_Status,
                r.Registration_Date,
                r.Status AS Registration_Status,
                p.Participant_ID,
                p.Name AS Participant_Name,
                p.Email AS Participant_Email,
                p.Phone AS Participant_Phone,
                e.Event_ID,
                e.Event_Name
            FROM Payment pay
            JOIN Registration r ON pay.Registration_ID = r.Registration_ID
            JOIN Participant p ON r.Participant_ID = p.Participant_ID
            JOIN Event e ON r.Event_ID = e.Event_ID
            WHERE pay.Payment_ID = ?
        """
        row = db.fetch_one(query, (pay_id,))
        if not row:
            return jsonify({"status": "error", "message": "Payment record not found."}), 404

        return jsonify({"status": "success", "data": row}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@payments_bp.route('/api/payments', methods=['POST'])
def create_payment():
    try:
        data = request.get_json() or {}
        reg_id = data.get('Registration_ID')
        amount = data.get('Amount')
        pay_date = data.get('Payment_Date', '').strip() or datetime.now().strftime('%Y-%m-%d')
        status_val = data.get('Payment_Status', 'Completed').strip()

        if not reg_id:
            return jsonify({"status": "error", "message": "Registration ID must be selected."}), 400

        try:
            amount = float(amount)
            if amount < 0:
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({"status": "error", "message": "Amount must be a non-negative number."}), 400

        if status_val not in ('Completed', 'Pending', 'Failed', 'Refunded'):
            return jsonify({"status": "error", "message": "Invalid payment status."}), 400

        # Check registration existence
        if not db.fetch_one("SELECT 1 FROM Registration WHERE Registration_ID = ?", (reg_id,)):
            return jsonify({"status": "error", "message": f"Registration #{reg_id} does not exist."}), 400

        # Check 1:1 relationship (Payment must be unique per registration)
        existing_pay = db.fetch_one("SELECT Payment_ID FROM Payment WHERE Registration_ID = ?", (reg_id,))
        if existing_pay:
            return jsonify({
                "status": "error",
                "message": f"A payment record (#{existing_pay['Payment_ID']}) already exists for Registration #{reg_id} (1:1 constraint)."
            }), 400

        res = db.execute(
            "INSERT INTO Payment (Registration_ID, Amount, Payment_Date, Payment_Status) VALUES (?, ?, ?, ?)",
            (reg_id, amount, pay_date, status_val)
        )
        return jsonify({
            "status": "success",
            "message": "Payment recorded successfully in SQL database.",
            "payment_id": res['lastrowid']
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@payments_bp.route('/api/payments/<int:pay_id>', methods=['PUT'])
def update_payment(pay_id):
    try:
        data = request.get_json() or {}
        amount = data.get('Amount')
        pay_date = data.get('Payment_Date', '').strip()
        status_val = data.get('Payment_Status', '').strip()

        if not db.fetch_one("SELECT 1 FROM Payment WHERE Payment_ID = ?", (pay_id,)):
            return jsonify({"status": "error", "message": "Payment not found."}), 404

        try:
            amount = float(amount)
            if amount < 0:
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({"status": "error", "message": "Amount must be a non-negative number."}), 400

        if status_val not in ('Completed', 'Pending', 'Failed', 'Refunded'):
            return jsonify({"status": "error", "message": "Invalid payment status."}), 400

        db.execute(
            "UPDATE Payment SET Amount = ?, Payment_Date = ?, Payment_Status = ? WHERE Payment_ID = ?",
            (amount, pay_date, status_val, pay_id)
        )
        return jsonify({"status": "success", "message": "Payment updated successfully."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@payments_bp.route('/api/payments/<int:pay_id>', methods=['DELETE'])
def delete_payment(pay_id):
    try:
        if not db.fetch_one("SELECT 1 FROM Payment WHERE Payment_ID = ?", (pay_id,)):
            return jsonify({"status": "error", "message": "Payment not found."}), 404

        db.execute("DELETE FROM Payment WHERE Payment_ID = ?", (pay_id,))
        return jsonify({"status": "success", "message": "Payment record deleted successfully."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
