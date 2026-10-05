from flask import Flask, request, jsonify, redirect
import sqlite3, random, string

app = Flask(__name__)
DB_NAME = "urls.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  original_url TEXT, short_code TEXT UNIQUE)''')
    conn.commit()
    conn.close()

def generate_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

init_db()

@app.route('/')
def home():
    return "URL Shortener API running! Use POST /api/shorten"

@app.route('/api/shorten', methods=['POST'])
def shorten():
    data = request.get_json()
    original = data['url']
    code = generate_code()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO urls (original_url, short_code) VALUES (?,?)", (original, code))
    conn.commit()
    conn.close()
    return jsonify({"short_url": f"{request.host_url}{code}", "original_url": original})

@app.route('/<code>')
def redirect_url(code):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT original_url FROM urls WHERE short_code=?", (code,))
    row = c.fetchone()
    conn.close()
    if row:
        return redirect(row[0])
    return jsonify({"error": "Not found"}), 404