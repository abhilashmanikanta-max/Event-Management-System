from flask import Blueprint, request, jsonify
from backend.database.db import db
from backend.config.config import Config

database_bp = Blueprint('database', __name__)

ALLOWED_TABLES = ['Organizer', 'Venue', 'Category', 'Participant', 'Event', 'Registration', 'Payment']

@database_bp.route('/api/database/status', methods=['GET'])
def get_db_status():
    try:
        tables = db.get_existing_tables()
        table_summaries = []
        for tbl in ALLOWED_TABLES:
            if tbl in tables:
                cnt = db.fetch_one(f"SELECT COUNT(*) AS c FROM {tbl}")['c']
                table_summaries.append({
                    "name": tbl,
                    "record_count": cnt,
                    "exists": True
                })
            else:
                table_summaries.append({
                    "name": tbl,
                    "record_count": 0,
                    "exists": False
                })

        return jsonify({
            "status": "success",
            "db_type": db.db_type,
            "engine": "Oracle SQL Database" if db.db_type == 'oracle' else "SQLite 3 Relational Engine",
            "connection_info": (
                f"{Config.ORACLE_HOST}:{Config.ORACLE_PORT}/{Config.ORACLE_SERVICE_NAME}"
                if db.db_type == 'oracle'
                else str(Config.SQLITE_DB_PATH)
            ),
            "tables": table_summaries
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@database_bp.route('/api/database/tables', methods=['GET'])
def get_tables_summary():
    try:
        results = []
        for tbl in ALLOWED_TABLES:
            meta = db.get_table_metadata(tbl)
            results.append(meta)

        return jsonify({"status": "success", "tables": results}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@database_bp.route('/api/database/tables/<table_name>', methods=['GET'])
def get_table_details_and_rows(table_name):
    try:
        canonical_name = None
        for tbl in ALLOWED_TABLES:
            if tbl.lower() == table_name.lower():
                canonical_name = tbl
                break

        if not canonical_name:
            return jsonify({"status": "error", "message": f"Table '{table_name}' does not exist in schema."}), 404

        # Schema metadata
        meta = db.get_table_metadata(canonical_name)

        # Query options: search, sort, pagination
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort_by', '').strip()
        order = request.args.get('order', 'ASC').upper()
        page = max(1, int(request.args.get('page', 1)))
        limit = max(1, min(200, int(request.args.get('limit', 20))))
        offset = (page - 1) * limit

        # Validate sort_by against actual columns
        valid_cols = [c['name'] for c in meta['columns']]
        if sort_by and sort_by not in valid_cols:
            sort_by = valid_cols[0]
        elif not sort_by:
            sort_by = valid_cols[0]

        order_dir = 'DESC' if order == 'DESC' else 'ASC'

        # WHERE clause for search
        where_sql = ""
        params = []
        if search:
            search_parts = [f"CAST({col} AS TEXT) LIKE ?" for col in valid_cols]
            where_sql = "WHERE " + " OR ".join(search_parts)
            wildcard = f"%{search}%"
            params = [wildcard] * len(valid_cols)

        # Total count
        cnt_query = f"SELECT COUNT(*) AS total FROM {canonical_name} {where_sql}"
        filtered_count = db.fetch_one(cnt_query, params)['total']

        # Fetch records
        query = f"""
            SELECT * FROM {canonical_name}
            {where_sql}
            ORDER BY {sort_by} {order_dir}
            LIMIT ? OFFSET ?
        """
        rows = db.fetch_all(query, params + [limit, offset])

        return jsonify({
            "status": "success",
            "metadata": meta,
            "data": rows,
            "pagination": {
                "total": filtered_count,
                "page": page,
                "limit": limit,
                "total_pages": (filtered_count + limit - 1) // limit if filtered_count > 0 else 1
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@database_bp.route('/api/database/reset', methods=['POST'])
def reset_database():
    try:
        res = db.reset_database()
        return jsonify(res), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
