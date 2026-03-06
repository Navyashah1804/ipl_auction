from flask import Flask, render_template, request, jsonify
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db():
    return psycopg2.connect(DATABASE_URL)


@app.route("/health")
def health():
    return {"status": "running"}


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
        (username, password),
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
        (username, password),
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

    players = []
    for r in rows:
        players.append({
            "id": r[0],
            "name": r[1],
            "team": r[2],
            "price": r[3]
        })

    cur.close()
    conn.close()

    return jsonify(players)
