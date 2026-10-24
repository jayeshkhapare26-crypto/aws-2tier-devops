import os
import time
import pymysql
from flask import Flask, jsonify

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "mysql"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.environ["DB_PASSWORD"],
        database=os.getenv("DB_NAME", "appdb"),
        connect_timeout=3,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.get("/")
def home():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS messages "
                    "(id INT AUTO_INCREMENT PRIMARY KEY, "
                    "message VARCHAR(255) NOT NULL)"
                )
                cursor.execute("SELECT COUNT(*) AS total FROM messages")
                count = cursor.fetchone()["total"]

                if count == 0:
                    cursor.execute(
                        "INSERT INTO messages (message) VALUES (%s)",
                        ("Hello from AWS 2-Tier Application!",)
                    )
                    conn.commit()

                cursor.execute("SELECT message FROM messages LIMIT 1")
                result = cursor.fetchone()

        return (
            "<h1>AWS 2-Tier Web Application</h1>"
            f"<p>{result['message']}</p>"
            "<p>Flask + Docker + Kubernetes + MySQL</p>"
        )
    except Exception:
        app.logger.exception("Database request failed")
        return "Application is running, but database is unavailable.", 503

@app.get("/health")
def health():
    return jsonify(status="ok"), 200

@app.get("/ready")
def ready():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
        return jsonify(status="ready"), 200
    except Exception:
        return jsonify(status="not_ready"), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
