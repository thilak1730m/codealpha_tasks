from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB = "events.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (id INTEGER PRIMARY KEY, name TEXT, date TEXT, venue TEXT, description TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS registrations
                 (id INTEGER PRIMARY KEY, event_id INTEGER, user_name TEXT, user_email TEXT)''')
    # Add sample events if empty
    c.execute("SELECT COUNT(*) FROM events")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO events VALUES (1, 'Tech Talk 2025', '2025-11-10', 'Chennai', 'Learn Backend Development')")
        c.execute("INSERT INTO events VALUES (2, 'CodeAlpha Meetup', '2025-11-15', 'Online', 'Internship guidance')")
        c.execute("INSERT INTO events VALUES (3, 'Python Workshop', '2025-11-20', 'Coimbatore', 'Hands-on Flask')")
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return jsonify({"message": "Event Registration System API", "endpoints": ["/events", "/events/<id>", "/register", "/my-registrations?email=...", "/cancel/<registration_id>"]})

# 1. View event list
@app.route("/events", methods=["GET"])
def list_events():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM events")
    rows = c.fetchall()
    conn.close()
    events = [{"id": r[0], "name": r[1], "date": r[2], "venue": r[3], "description": r[4]} for r in rows]
    return jsonify(events)

# 2. Event details
@app.route("/events/<int:event_id>", methods=["GET"])
def event_details(event_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM events WHERE id=?", (event_id,))
    r = c.fetchone()
    conn.close()
    if r:
        return jsonify({"id": r[0], "name": r[1], "date": r[2], "venue": r[3], "description": r[4]})
    return jsonify({"error": "Event not found"}), 404

# 3. Submit registration
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    event_id = data.get("event_id")
    name = data.get("user_name")
    email = data.get("user_email")
    if not all([event_id, name, email]):
        return jsonify({"error": "event_id, user_name, user_email required"}), 400
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO registrations (event_id, user_name, user_email) VALUES (?,?,?)", (event_id, name, email))
    conn.commit()
    reg_id = c.lastrowid
    conn.close()
    return jsonify({"message": "Registered successfully", "registration_id": reg_id})

# 4. View/cancel their registrations
@app.route("/my-registrations", methods=["GET"])
def my_regs():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "email query param required"}), 400
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT r.id, e.name, e.date, e.venue FROM registrations r JOIN events e ON r.event_id=e.id WHERE r.user_email=?", (email,))
    rows = c.fetchall()
    conn.close()
    result = [{"registration_id": r[0], "event_name": r[1], "date": r[2], "venue": r[3]} for r in rows]
    return jsonify(result)

@app.route("/cancel/<int:reg_id>", methods=["DELETE"])
def cancel(reg_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM registrations WHERE id=?", (reg_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Registration cancelled"})

if __name__ == "__main__":
    app.run(debug=True)