import os
import pandas as pd
from flask import Flask, request, jsonify, render_template, session, redirect
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "auction-secret"

DATABASE_URL = os.getenv("DATABASE_URL")


# ---------------------------
# DATABASE CONNECTION
# ---------------------------
def get_db():
    conn = psycopg2.connect(
        DATABASE_URL,
        sslmode="require",
        cursor_factory=RealDictCursor
    )
    return conn


# ---------------------------
# DATABASE SETUP
# ---------------------------
def setup_database():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS players(
        id SERIAL PRIMARY KEY,
        name TEXT,
        team TEXT,
        nationality TEXT,
        strike_rate FLOAT,
        base_price INT,
        current_bid INT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bids(
        id SERIAL PRIMARY KEY,
        user_id INT,
        player_id INT,
        amount INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("SELECT COUNT(*) FROM players")
    count = cur.fetchone()["count"]

    if count == 0:

        df = pd.read_csv("players.csv")

        for _, row in df.iterrows():

            cur.execute("""
            INSERT INTO players(name,team,nationality,strike_rate,base_price,current_bid)
            VALUES(%s,%s,%s,%s,%s,%s)
            """,
            (
                row["name"],
                row["team"],
                row["nationality"],
                row["strike_rate"],
                row["base_price"],
                row["current_bid"]
            ))

    conn.commit()
    cur.close()
    conn.close()


# ---------------------------
# PAGE ROUTES
# ---------------------------
@app.route("/")
def home():

    if "user_id" not in session:
        return render_template("login.html")

    return render_template("app.html")


@app.route("/login-page")
def login_page():
    return render_template("login.html")


@app.route("/register-page")
def register_page():
    return render_template("register.html")


# ---------------------------
# AUTH ROUTES
# ---------------------------
@app.route("/register", methods=["POST"])
def register():

    data = request.json
    username = data["username"]
    password = generate_password_hash(data["password"])

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users(username,password) VALUES(%s,%s)",
            (username, password)
        )
        conn.commit()

    except:
        return jsonify({"error": "User already exists"}), 400

    return jsonify({"success": True})


@app.route("/login", methods=["POST"])
def login():

    data = request.json

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=%s",
        (data["username"],)
    )

    user = cur.fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 401

    if not check_password_hash(user["password"], data["password"]):
        return jsonify({"error": "Wrong password"}), 401

    session["user_id"] = user["id"]

    return jsonify({"success": True})


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------------------
# PLAYERS API
# ---------------------------
@app.route("/players")
def players():

    nationality = request.args.get("type")

    conn = get_db()
    cur = conn.cursor()

    if nationality == "Indian":
        cur.execute("SELECT * FROM players WHERE nationality='Indian'")

    elif nationality == "Overseas":
        cur.execute("SELECT * FROM players WHERE nationality='Overseas'")

    else:
        cur.execute("SELECT * FROM players")

    players = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(players)


# ---------------------------
# BIDDING API
# ---------------------------
@app.route("/bid", methods=["POST"])
def bid():

    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    data = request.json
    player_id = data["player_id"]
    bid_amount = int(data["bid"])

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT current_bid FROM players WHERE id=%s",
        (player_id,)
    )

    current = cur.fetchone()["current_bid"]

    if bid_amount <= current:
        return jsonify({"error": "Bid must be higher"}), 400

    cur.execute(
        "UPDATE players SET current_bid=%s WHERE id=%s",
        (bid_amount, player_id)
    )

    cur.execute(
        "INSERT INTO bids(user_id,player_id,amount) VALUES(%s,%s,%s)",
        (session["user_id"], player_id, bid_amount)
    )

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"success": True})


# ---------------------------
# HEALTH CHECK
# ---------------------------
@app.route("/health")
def health():
    return {"status": "running"}


# ---------------------------
# STARTUP
# ---------------------------
setup_database()

if __name__ == "__main__":
    app.run(debug=True)
