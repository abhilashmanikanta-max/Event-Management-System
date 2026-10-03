from flask import Blueprint, request, jsonify
from backend.database.db import db

events_bp = Blueprint('events', __name__)

@events_bp.route('/api/events', methods=['GET'])
def get_events():
    try:
        search = request.args.get('search', '').strip()
        category_id = request.args.get('category_id', '').strip()
        date_filter = request.args.get('date', '').strip()
        sort_by = request.args.get('sort_by', 'Date')
        order = request.args.get('order', 'ASC').upper()
        page = max(1, int(request.args.get('page', 1)))
        limit = max(1, min(100, int(request.args.get('limit', 10))))
        offset = (page - 1) * limit

        # Allowed sort columns to prevent SQL injection
        allowed_sort = {
            'Event_ID': 'e.Event_ID',
            'Event_Name': 'e.Event_Name',
            'Date': 'e.Date',
            'Time': 'e.Time',
            'Organizer': 'o.Name',
            'Venue': 'v.Venue_Name',
            'Category': 'c.Category_Name'
        }
        order_col = allowed_sort.get(sort_by, 'e.Date')
        order_dir = 'DESC' if order == 'DESC' else 'ASC'

        # Build WHERE clause
        where_clauses = []
        params = []

        if search:
            where_clauses.append("(e.Event_Name LIKE ? OR o.Name LIKE ? OR v.Venue_Name LIKE ?)")
            wildcard = f"%{search}%"
            params.extend([wildcard, wildcard, wildcard])

        if category_id:
            where_clauses.append("e.Category_ID = ?")
            params.append(int(category_id))

        if date_filter:
            where_clauses.append("e.Date = ?")
            params.append(date_filter)

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        # Count total matching
        count_query = f"""
            SELECT COUNT(*) AS total
            FROM Event e
            JOIN Organizer o ON e.Organizer_ID = o.Organizer_ID
            JOIN Venue v ON e.Venue_ID = v.Venue_ID
            JOIN Category c ON e.Category_ID = c.Category_ID
            {where_sql}
        """
        total_count = db.fetch_one(count_query, params)['total']

        # Fetch records
        query = f"""
            SELECT 
                e.Event_ID,
                e.Event_Name,
                e.Date,
                e.Time,
                e.Organizer_ID,
                o.Name AS Organizer_Name,
                e.Venue_ID,
                v.Venue_Name,
                v.Capacity,
                e.Category_ID,
                c.Category_Name,
                COUNT(r.Registration_ID) AS Total_Registrations
            FROM Event e
            JOIN Organizer o ON e.Organizer_ID = o.Organizer_ID
            JOIN Venue v ON e.Venue_ID = v.Venue_ID
            JOIN Category c ON e.Category_ID = c.Category_ID
            LEFT JOIN Registration r ON e.Event_ID = r.Event_ID
            {where_sql}
            GROUP BY e.Event_ID, e.Event_Name, e.Date, e.Time, e.Organizer_ID, o.Name, e.Venue_ID, v.Venue_Name, v.Capacity, e.Category_ID, c.Category_Name
            ORDER BY {order_col} {order_dir}
            LIMIT ? OFFSET ?
        """
        fetch_params = list(params) + [limit, offset]
        rows = db.fetch_all(query, fetch_params)

        return jsonify({
            "status": "success",
            "data": rows,
            "pagination": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "total_pages": (total_count + limit - 1) // limit if total_count > 0 else 1
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@events_bp.route('/api/events/<int:event_id>', methods=['GET'])
def get_event_details(event_id):
    try:
        # Event Details
        query = """
            SELECT 
                e.Event_ID,
                e.Event_Name,
                e.Date,
                e.Time,
                e.Organizer_ID,
                o.Name AS Organizer_Name,
                o.Email AS Organizer_Email,
                o.Phone AS Organizer_Phone,
                e.Venue_ID,
                v.Venue_Name,
                v.Location AS Venue_Location,
                v.Capacity AS Venue_Capacity,
                e.Category_ID,
                c.Category_Name,
                c.Description AS Category_Description
            FROM Event e
            JOIN Organizer o ON e.Organizer_ID = o.Organizer_ID
            JOIN Venue v ON e.Venue_ID = v.Venue_ID
            JOIN Category c ON e.Category_ID = c.Category_ID
            WHERE e.Event_ID = ?
        """
        event = db.fetch_one(query, (event_id,))
        if not event:
            return jsonify({"status": "error", "message": f"Event with ID {event_id} not found."}), 404

        # Registered Participants list
        reg_query = """
            SELECT 
                r.Registration_ID,
                r.Registration_Date,
                r.Status AS Registration_Status,
                p.Participant_ID,
                p.Name AS Participant_Name,
                p.Email AS Participant_Email,
                p.Phone AS Participant_Phone,
                pay.Payment_ID,
                pay.Amount AS Paid_Amount,
                pay.Payment_Status
            FROM Registration r
            JOIN Participant p ON r.Participant_ID = p.Participant_ID
            LEFT JOIN Payment pay ON r.Registration_ID = pay.Registration_ID
            WHERE r.Event_ID = ?
            ORDER BY r.Registration_Date DESC
        """
        registrations = db.fetch_all(reg_query, (event_id,))
        event['Registrations'] = registrations
        event['Total_Registrations'] = len(registrations)

        return jsonify({"status": "success", "data": event}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@events_bp.route('/api/events', methods=['POST'])
def create_event():
    try:
        data = request.get_json() or {}
        event_name = data.get('Event_Name', '').strip()
        date_val = data.get('Date', '').strip()
        time_val = data.get('Time', '').strip()
        organizer_id = data.get('Organizer_ID')
        venue_id = data.get('Venue_ID')
        category_id = data.get('Category_ID')

        # Validation
        if not event_name:
            return jsonify({"status": "error", "message": "Event Name is required."}), 400
        if not date_val:
            return jsonify({"status": "error", "message": "Event Date is required."}), 400
        if not time_val:
            return jsonify({"status": "error", "message": "Event Time is required."}), 400
        if not organizer_id:
            return jsonify({"status": "error", "message": "Organizer selection is required."}), 400
        if not venue_id:
            return jsonify({"status": "error", "message": "Venue selection is required."}), 400
        if not category_id:
            return jsonify({"status": "error", "message": "Category selection is required."}), 400

        # Foreign Key check: ensure parent records exist
        if not db.fetch_one("SELECT 1 FROM Organizer WHERE Organizer_ID = ?", (organizer_id,)):
            return jsonify({"status": "error", "message": "Selected Organizer does not exist in the database."}), 400
        if not db.fetch_one("SELECT 1 FROM Venue WHERE Venue_ID = ?", (venue_id,)):
            return jsonify({"status": "error", "message": "Selected Venue does not exist in the database."}), 400
        if not db.fetch_one("SELECT 1 FROM Category WHERE Category_ID = ?", (category_id,)):
            return jsonify({"status": "error", "message": "Selected Category does not exist in the database."}), 400

        insert_query = """
            INSERT INTO Event (Event_Name, Date, Time, Organizer_ID, Venue_ID, Category_ID)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        res = db.execute(insert_query, (event_name, date_val, time_val, organizer_id, venue_id, category_id))
        
        return jsonify({
            "status": "success",
            "message": "Event created successfully in SQL database.",
            "event_id": res['lastrowid']
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@events_bp.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    try:
        data = request.get_json() or {}
        event_name = data.get('Event_Name', '').strip()
        date_val = data.get('Date', '').strip()
        time_val = data.get('Time', '').strip()
        organizer_id = data.get('Organizer_ID')
        venue_id = data.get('Venue_ID')
        category_id = data.get('Category_ID')

        if not db.fetch_one("SELECT 1 FROM Event WHERE Event_ID = ?", (event_id,)):
            return jsonify({"status": "error", "message": f"Event with ID {event_id} not found."}), 404

        if not event_name or not date_val or not time_val:
            return jsonify({"status": "error", "message": "Name, Date, and Time are required fields."}), 400

        update_query = """
            UPDATE Event
            SET Event_Name = ?, Date = ?, Time = ?, Organizer_ID = ?, Venue_ID = ?, Category_ID = ?
            WHERE Event_ID = ?
        """
        db.execute(update_query, (event_name, date_val, time_val, organizer_id, venue_id, category_id, event_id))

        return jsonify({
            "status": "success",
            "message": "Event updated successfully."
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@events_bp.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        # Check existence
        event = db.fetch_one("SELECT Event_Name FROM Event WHERE Event_ID = ?", (event_id,))
        if not event:
            return jsonify({"status": "error", "message": f"Event with ID {event_id} not found."}), 404

        # Enforce foreign key protection explicitly before delete
        reg_count = db.fetch_one("SELECT COUNT(*) AS c FROM Registration WHERE Event_ID = ?", (event_id,))['c']
        if reg_count > 0:
            return jsonify({
                "status": "error",
                "message": f"Cannot delete event '{event['Event_Name']}' because {reg_count} participant registration(s) exist for it. Please cancel or delete the registrations first."
            }), 400

        db.execute("DELETE FROM Event WHERE Event_ID = ?", (event_id,))
        return jsonify({
            "status": "success",
            "message": f"Event '{event['Event_Name']}' deleted successfully."
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
