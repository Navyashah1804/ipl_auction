import os
import psycopg2
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username TEXT,
            password TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS players(
            id SERIAL PRIMARY KEY,
            name TEXT,
            team TEXT,
            price INT
        )
        """)

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print("Database init error:", e)


@app.before_first_request
def startup():
    init_db()


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/register-page")
def register_page():
    return render_template("register.html")


@app.route("/app")
def app_page():
    return render_template("app.html")


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data["username"]
    password = data["password"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (username,password) VALUES (%s,%s)",
        (username, password)
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "registered"})


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data["password"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )

    user = cur.fetchone()

    cur.close()
    conn.close()

    if user:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "fail"})


@app.route("/players")
def players():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM players")

    rows = cur.fetchall()

    players_list = []
    for r in rows:
        players_list.append({
            "id": r[0],
            "name": r[1],
            "team": r[2],
            "price": r[3]
        })

    cur.close()
    conn.close()

    return jsonify(players_list)


@app.route("/health")
def health():
    return {"status": "running"}
