
from flask import Flask, render_template, request, jsonify
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def home():
    return render_template("app.html")

@app.route("/players")
def players():
    search = request.args.get("search","")
    role = request.args.get("role","")

    conn = get_db()
    cur = conn.cursor()

    query = '''
    SELECT id,name,photo,role,team,strike_rate,current_bid
    FROM players
    WHERE name ILIKE %s
    '''
    params = [f"%{search}%"]

    if role != "":
        query += " AND role=%s"
        params.append(role)

    cur.execute(query,params)
    rows = cur.fetchall()

    players=[]
    for r in rows:
        players.append({
            "id":r[0],
            "name":r[1],
            "photo":r[2],
            "role":r[3],
            "team":r[4],
            "strike_rate":r[5],
            "current_bid":r[6]
        })

    conn.close()
    return jsonify(players)

@app.route("/bid",methods=["POST"])
def bid():
    data=request.json
    player_id=data["id"]
    bid_amount=int(data["bid"])

    conn=get_db()
    cur=conn.cursor()

    cur.execute("SELECT current_bid FROM players WHERE id=%s",(player_id,))
    current=cur.fetchone()[0]

    if bid_amount<=current:
        return jsonify({"error":"Bid must be higher than current bid"}),400

    cur.execute(
        "UPDATE players SET current_bid=%s WHERE id=%s",
        (bid_amount,player_id)
    )

    conn.commit()
    conn.close()

    return jsonify({"message":"Bid successful"})

if __name__ == "__main__":
    app.run()
