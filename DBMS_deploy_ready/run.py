import os
import sys

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import create_app
from backend.config.config import Config

app = create_app()

if __name__ == '__main__':
    print(f"\n" + "="*60)
    print(f"  EVENT MANAGEMENT SYSTEM - College DBMS Project")
    print(f"  Database Engine : {Config.DB_TYPE.upper()}")
    print(f"  Local Server    : http://{Config.HOST}:{Config.PORT}")
    print(f"="*60 + "\n")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
