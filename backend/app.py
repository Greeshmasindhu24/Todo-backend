import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ---------------- DATABASE URL (SUPABASE) ----------------
DATABASE_URL = "postgresql://postgres.wvphmoibvycgxokjmoht:z5LLseT0rhsmxg70@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"


# ---------------- DB CONNECTION ----------------
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


# ---------------- INIT DATABASE ----------------
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            category TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- HOME ----------------
@app.route("/")
def home():
    return "Backend Running Successfully"


# ---------------- ADD TASK ----------------
@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()

    if not data or "text" not in data or "category" not in data:
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO tasks (text, category, completed) VALUES (%s, %s, %s)",
        (data["text"], data["category"], 0)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Task added successfully"})


# ---------------- GET TASKS ----------------
@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, text, category, completed FROM tasks")
    rows = cur.fetchall()

    conn.close()

    tasks = [
        {
            "id": r[0],
            "text": r[1],
            "category": r[2],
            "completed": bool(r[3])
        }
        for r in rows
    ]

    return jsonify(tasks)


# ---------------- DELETE TASK ----------------
@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM tasks WHERE id=%s", (id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Task deleted"})


# ---------------- TOGGLE COMPLETE ----------------
@app.route("/tasks/<int:id>", methods=["PUT"])
def toggle_task(id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE tasks
        SET completed = CASE
            WHEN completed = 1 THEN 0
            ELSE 1
        END
        WHERE id = %s
    """, (id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Task updated"})


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)