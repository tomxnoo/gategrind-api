from flask import Flask, request, jsonify
import os
import psycopg2  # Or use SQLAlchemy if you prefer

def create_app():
    app = Flask(__name__)

    @app.route("/api/health", methods=["GET", "POST"])
    def receive_health():
        if request.method == "GET":
            # Health check endpoint for Fly.io or browser
            return jsonify({"status": "ok", "message": "API live"}), 200

        # POST: Receive health data from iOS Shortcuts or other clients
        data = request.get_json()
        try:
            conn = psycopg2.connect(os.environ["DATABASE_URL"])
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO health_data (user_id, steps, sync_date) VALUES (%s, %s, %s)",
                (data["user_id"], data["steps"], data["date"])
            )
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Add more endpoints as needed...

    return app
