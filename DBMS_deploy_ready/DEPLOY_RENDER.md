# Deploy to Render

1. Upload this project to a GitHub repository.
2. In Render, create a **Web Service** from that repository.
3. Render will use:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn --bind 0.0.0.0:$PORT run:app`
4. Set `DB_TYPE=sqlite` and `DEBUG=False` if Render does not import them from `render.yaml`.
5. Deploy.

The application creates/initializes the SQLite database from `database/schema/schema_sqlite.sql`
and `database/seed/seed_sqlite.sql` when it starts.

## Important database note

This project uses SQLite by default. On hosting platforms with an ephemeral filesystem,
SQLite changes may not survive a redeploy/restart. The seeded demo data will be recreated as
needed. For persistent production data, use a persistent database/service and adapt the
database configuration accordingly.

## GitHub safety

Do not commit `.env`, `.venv`, passwords, API keys, or other secrets. `.gitignore` is included.
