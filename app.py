from flask import Flask, request, jsonify, render_template_string
import sqlite3

app = Flask(__name__)

# ----------------------------
# DATABASE SETUP
# ----------------------------
import csv

def init_db():
    conn = sqlite3.connect("ipl.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS players(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        photo TEXT,
        role TEXT,
        team TEXT,
        strike_rate REAL,
        current_bid INTEGER
    )
    """)

    cur.execute("SELECT COUNT(*) FROM players")
    count = cur.fetchone()[0]

    if count == 0:

        with open("players.csv", newline='', encoding="utf-8") as file:
            reader = csv.DictReader(file)

            players = []

            for row in reader:
                players.append((
                    row["name"],
                    row["photo"],
                    row["role"],
                    row["team"],
                    float(row["strike_rate"]),
                    int(row["current_bid"])
                ))

        cur.executemany("""
        INSERT INTO players(name,photo,role,team,strike_rate,current_bid)
        VALUES(?,?,?,?,?,?)
        """, players)

    conn.commit()
    conn.close()

        

       


# ----------------------------
# FRONTEND HTML
# ----------------------------

HTML = """

<!DOCTYPE html>
<html>

<head>

<title>IPL Auction</title>

<style>

body{
font-family:Arial;
background:#0f172a;
color:white;
text-align:center;
}

h1{
margin-top:20px;
}

.filters{
margin:30px;
}

input,select{
padding:10px;
border-radius:6px;
border:none;
margin:5px;
}

button{
padding:10px 15px;
background:#ff9800;
border:none;
border-radius:6px;
color:white;
font-weight:bold;
cursor:pointer;
}

#players{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
gap:20px;
padding:40px;
}

.card{
background:#1e293b;
padding:20px;
border-radius:10px;
box-shadow:0 10px 20px rgba(0,0,0,0.3);
}

.photo{
width:120px;
height:120px;
border-radius:50%;
object-fit:cover;
margin-bottom:10px;
}

</style>

</head>

<body>

<h1>IPL Auction System</h1>

<div class="filters">

<input id="search" placeholder="Search player">

<select id="role">
<option value="">All Roles</option>
<option value="Batsman">Batsman</option>
<option value="Bowler">Bowler</option>
<option value="All-Rounder">All-Rounder</option>
<option value="Wicket Keeper">Wicket Keeper</option>
</select>

<button onclick="loadPlayers()">Search</button>

</div>

<div id="players"></div>


<script>

function loadPlayers(){

let search=document.getElementById("search").value
let role=document.getElementById("role").value

fetch(`/players?search=${search}&role=${role}`)
.then(res=>res.json())
.then(data=>{

let html=""

data.forEach(p=>{

html+=`

<div class="card">

<img src="${p.photo}" class="photo">

<h3>${p.name}</h3>

<p><b>Team:</b> ${p.team}</p>
<p><b>Role:</b> ${p.role}</p>
<p><b>Strike Rate:</b> ${p.strike_rate}</p>

<p><b>Current Bid:</b> ₹${p.current_bid}</p>

<input id="bid_${p.id}" placeholder="Enter bid">

<button onclick="bid(${p.id})">Bid</button>

</div>

`

})

document.getElementById("players").innerHTML=html

})

}

function bid(id){

let bid=document.getElementById("bid_"+id).value

fetch("/bid",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
id:id,
bid:bid
})
})
.then(res=>res.json())
.then(data=>{
alert(data.message || data.error)
loadPlayers()
})

}

loadPlayers()

</script>

</body>
</html>

"""


# ----------------------------
# ROUTES
# ----------------------------

@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/players")
def players():

    search = request.args.get("search","")
    role = request.args.get("role","")

    conn = sqlite3.connect("ipl.db")
    cur = conn.cursor()

    query = "SELECT * FROM players WHERE name LIKE ?"
    params = [f"%{search}%"]

    if role:
        query += " AND role=?"
        params.append(role)

    cur.execute(query,params)
    rows = cur.fetchall()

    players = []

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

    conn=sqlite3.connect("ipl.db")
    cur=conn.cursor()

    cur.execute("SELECT current_bid FROM players WHERE id=?",(player_id,))
    current=cur.fetchone()[0]

    if bid_amount <= current:
        return jsonify({"error":"Bid must be higher than current bid"})

    cur.execute(
        "UPDATE players SET current_bid=? WHERE id=?",
        (bid_amount,player_id)
    )

    conn.commit()
    conn.close()

    return jsonify({"message":"Bid successful"})


# ----------------------------
# RUN APP
# ----------------------------

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
