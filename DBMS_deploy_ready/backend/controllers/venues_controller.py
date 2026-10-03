from flask import Blueprint, request, jsonify
from backend.database.db import db

venues_bp = Blueprint('venues', __name__)

@venues_bp.route('/api/venues', methods=['GET'])
def get_venues():
    try:
        search = request.args.get('search', '').strip()
        where_sql = ""
        params = []

        if search:
            where_sql = "WHERE v.Venue_Name LIKE ? OR v.Location LIKE ?"
            wildcard = f"%{search}%"
            params.extend([wildcard, wildcard])

        query = f"""
            SELECT 
                v.Venue_ID,
                v.Venue_Name,
                v.Location,
                v.Capacity,
                COUNT(e.Event_ID) AS Total_Events
            FROM Venue v
            LEFT JOIN Event e ON v.Venue_ID = e.Venue_ID
            {where_sql}
            GROUP BY v.Venue_ID, v.Venue_Name, v.Location, v.Capacity
            ORDER BY v.Venue_ID ASC
        """
        rows = db.fetch_all(query, params)
        return jsonify({"status": "success", "data": rows}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@venues_bp.route('/api/venues/<int:venue_id>', methods=['GET'])
def get_venue_details(venue_id):
    try:
        venue = db.fetch_one("SELECT * FROM Venue WHERE Venue_ID = ?", (venue_id,))
        if not venue:
            return jsonify({"status": "error", "message": "Venue not found."}), 404

        events = db.fetch_all("""
            SELECT 
                e.Event_ID, e.Event_Name, e.Date, e.Time,
                o.Name AS Organizer_Name, c.Category_Name
            FROM Event e
            JOIN Organizer o ON e.Organizer_ID = o.Organizer_ID
            JOIN Category c ON e.Category_ID = c.Category_ID
            WHERE e.Venue_ID = ?
            ORDER BY e.Date ASC
        """, (venue_id,))

        venue['events'] = events
        return jsonify({"status": "success", "data": venue}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@venues_bp.route('/api/venues', methods=['POST'])
def create_venue():
    try:
        data = request.get_json() or {}
        name = data.get('Venue_Name', '').strip()
        location = data.get('Location', '').strip()
        capacity = data.get('Capacity')

        if not name:
            return jsonify({"status": "error", "message": "Venue Name is required."}), 400
        if not location:
            return jsonify({"status": "error", "message": "Location is required."}), 400
        try:
            capacity = int(capacity)
            if capacity <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({"status": "error", "message": "Capacity must be a positive integer greater than zero."}), 400

        res = db.execute(
            "INSERT INTO Venue (Venue_Name, Location, Capacity) VALUES (?, ?, ?)",
            (name, location, capacity)
        )
        return jsonify({
            "status": "success",
            "message": "Venue created successfully.",
            "venue_id": res['lastrowid']
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@venues_bp.route('/api/venues/<int:venue_id>', methods=['PUT'])
def update_venue(venue_id):
    try:
        data = request.get_json() or {}
        name = data.get('Venue_Name', '').strip()
        location = data.get('Location', '').strip()
        capacity = data.get('Capacity')

        if not db.fetch_one("SELECT 1 FROM Venue WHERE Venue_ID = ?", (venue_id,)):
            return jsonify({"status": "error", "message": "Venue not found."}), 404

        if not name or not location:
            return jsonify({"status": "error", "message": "Venue Name and Location are required."}), 400
        
        try:
            capacity = int(capacity)
            if capacity <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({"status": "error", "message": "Capacity must be a positive integer greater than zero."}), 400

        db.execute(
            "UPDATE Venue SET Venue_Name = ?, Location = ?, Capacity = ? WHERE Venue_ID = ?",
            (name, location, capacity, venue_id)
        )
        return jsonify({"status": "success", "message": "Venue updated successfully."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@venues_bp.route('/api/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = db.fetch_one("SELECT Venue_Name FROM Venue WHERE Venue_ID = ?", (venue_id,))
        if not venue:
            return jsonify({"status": "error", "message": "Venue not found."}), 404

        event_cnt = db.fetch_one("SELECT COUNT(*) AS c FROM Event WHERE Venue_ID = ?", (venue_id,))['c']
        if event_cnt > 0:
            return jsonify({
                "status": "error",
                "message": f"Cannot delete venue '{venue['Venue_Name']}' because {event_cnt} event(s) are scheduled at this venue."
            }), 400

        db.execute("DELETE FROM Venue WHERE Venue_ID = ?", (venue_id,))
        return jsonify({"status": "success", "message": f"Venue '{venue['Venue_Name']}' deleted successfully."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
