from flask import Blueprint, request, jsonify
from backend.database.db import db

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        search = request.args.get('search', '').strip()
        where_sql = ""
        params = []

        if search:
            where_sql = "WHERE c.Category_Name LIKE ? OR c.Description LIKE ?"
            wildcard = f"%{search}%"
            params.extend([wildcard, wildcard])

        query = f"""
            SELECT 
                c.Category_ID,
                c.Category_Name,
                c.Description,
                COUNT(e.Event_ID) AS Total_Events
            FROM Category c
            LEFT JOIN Event e ON c.Category_ID = e.Category_ID
            {where_sql}
            GROUP BY c.Category_ID, c.Category_Name, c.Description
            ORDER BY c.Category_ID ASC
        """
        rows = db.fetch_all(query, params)
        return jsonify({"status": "success", "data": rows}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@categories_bp.route('/api/categories/<int:cat_id>', methods=['GET'])
def get_category_details(cat_id):
    try:
        category = db.fetch_one("SELECT * FROM Category WHERE Category_ID = ?", (cat_id,))
        if not category:
            return jsonify({"status": "error", "message": "Category not found."}), 404

        events = db.fetch_all("""
            SELECT 
                e.Event_ID, e.Event_Name, e.Date, e.Time,
                o.Name AS Organizer_Name, v.Venue_Name
            FROM Event e
            JOIN Organizer o ON e.Organizer_ID = o.Organizer_ID
            JOIN Venue v ON e.Venue_ID = v.Venue_ID
            WHERE e.Category_ID = ?
            ORDER BY e.Date ASC
        """, (cat_id,))

        category['events'] = events
        return jsonify({"status": "success", "data": category}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@categories_bp.route('/api/categories', methods=['POST'])
def create_category():
    try:
        data = request.get_json() or {}
        name = data.get('Category_Name', '').strip()
        description = data.get('Description', '').strip()

        if not name:
            return jsonify({"status": "error", "message": "Category Name is required."}), 400

        res = db.execute(
            "INSERT INTO Category (Category_Name, Description) VALUES (?, ?)",
            (name, description)
        )
        return jsonify({
            "status": "success",
            "message": "Category created successfully.",
            "category_id": res['lastrowid']
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@categories_bp.route('/api/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    try:
        data = request.get_json() or {}
        name = data.get('Category_Name', '').strip()
        description = data.get('Description', '').strip()

        if not db.fetch_one("SELECT 1 FROM Category WHERE Category_ID = ?", (cat_id,)):
            return jsonify({"status": "error", "message": "Category not found."}), 404

        if not name:
            return jsonify({"status": "error", "message": "Category Name is required."}), 400

        db.execute(
            "UPDATE Category SET Category_Name = ?, Description = ? WHERE Category_ID = ?",
            (name, description, cat_id)
        )
        return jsonify({"status": "success", "message": "Category updated successfully."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@categories_bp.route('/api/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    try:
        cat = db.fetch_one("SELECT Category_Name FROM Category WHERE Category_ID = ?", (cat_id,))
        if not cat:
            return jsonify({"status": "error", "message": "Category not found."}), 404

        event_cnt = db.fetch_one("SELECT COUNT(*) AS c FROM Event WHERE Category_ID = ?", (cat_id,))['c']
        if event_cnt > 0:
            return jsonify({
                "status": "error",
                "message": f"Cannot delete category '{cat['Category_Name']}' because {event_cnt} event(s) belong to this category."
            }), 400

        db.execute("DELETE FROM Category WHERE Category_ID = ?", (cat_id,))
        return jsonify({"status": "success", "message": f"Category '{cat['Category_Name']}' deleted successfully."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
