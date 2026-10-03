import os
from pathlib import Path
from flask import Flask, render_template, jsonify, send_from_directory

from backend.config.config import Config, BASE_DIR
from backend.database.db import db

# Import all controllers
from backend.controllers.dashboard_controller import dashboard_bp
from backend.controllers.events_controller import events_bp
from backend.controllers.organizers_controller import organizers_bp
from backend.controllers.venues_controller import venues_bp
from backend.controllers.categories_controller import categories_bp
from backend.controllers.participants_controller import participants_bp
from backend.controllers.registrations_controller import registrations_bp
from backend.controllers.payments_controller import payments_bp
from backend.controllers.reports_controller import reports_bp
from backend.controllers.database_controller import database_bp
from backend.controllers.query_controller import query_bp

def create_app():
    static_folder = str(BASE_DIR / 'frontend' / 'static')
    template_folder = str(BASE_DIR / 'frontend' / 'templates')

    app = Flask(
        __name__,
        static_folder=static_folder,
        static_url_path='/static',
        template_folder=template_folder
    )

    # Register API blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(organizers_bp)
    app.register_blueprint(venues_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(participants_bp)
    app.register_blueprint(registrations_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(database_bp)
    app.register_blueprint(query_bp)

    # Initialize Database on app start
    with app.app_context():
        try:
            db.init_database(seed=True)
        except Exception as e:
            print(f"[DBMS Init Warning] {e}")

    # Frontend Route
    @app.route('/')
    def index():
        return render_template('index.html')

    # API Health Check
    @app.route('/api/health', methods=['GET'])
    def health_check():
        tables = db.get_existing_tables()
        return jsonify({
            "status": "healthy",
            "db_type": db.db_type,
            "engine": "Oracle SQL Database" if db.db_type == 'oracle' else "SQLite 3 Relational Engine",
            "tables_found": len(tables),
            "tables": tables
        }), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"status": "error", "message": "Resource or endpoint not found."}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"status": "error", "message": "Internal DBMS Server Error."}), 500

    return app

if __name__ == '__main__':
    application = create_app()
    print(f"\n===========================================================")
    print(f"  EVENT MANAGEMENT SYSTEM - DBMS Full-Stack Web Application")
    print(f"  Connected to Database Engine: {Config.DB_TYPE.upper()}")
    print(f"  Server URL: http://{Config.HOST}:{Config.PORT}")
    print(f"===========================================================\n")
    application.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
