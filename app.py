import os
import pandas as pd
from flask import Flask, request, jsonify, render_template, session, redirect
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = "secret123"

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode="require", cursor_factory=RealDictCursor)


# ----------------------------
# HOME PAGE
# ----------------------------
@app.route("/")
def home():
    if "user_id" not in session:
        return render_template("login.html")
    return render_template("app.html")


@app.route("/register-page")
def register_page():
    return render_template("register.html")


# ----------------------------
# AUTH
# ----------------------------
@app.route("/login", methods=["POST"])
def login():

    data = request.json
    username = data["username"]
    password = data["password"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cur.fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 401

    if user["password"] != password:
        return jsonify({"error": "Wrong password"}), 401

    session["user_id"] = user["id"]

    return jsonify({"success": True})


@app.route("/register", methods=["POST"])
def register():

    data = request.json
    username = data["username"]
    password = data["password"]

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users(username,password) VALUES(%s,%s)",
            (username, password),
        )
        conn.commit()
    except:
        return jsonify({"error": "User exists"}), 400

    return jsonify({"success": True})


# ----------------------------
# PLAYERS API
# ----------------------------
@app.route("/players")
def players():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM players")
    players = cur.fetchall()

    return jsonify(players)


# ----------------------------
# HEALTH CHECK
# ----------------------------
@app.route("/health")
def health():
    return {"status": "ok"}
