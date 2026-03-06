// REGISTER
async function register() {

let username = document.getElementById("username").value
let password = document.getElementById("password").value

let res = await fetch("/register", {
method: "POST",
headers: {
"Content-Type": "application/json"
},
body: JSON.stringify({
username: username,
password: password
})
})

let data = await res.json()

if (data.status === "registered") {
alert("Account created!")
window.location = "/"
} else {
alert("Registration failed")
}

}


// LOGIN
async function login() {

let username = document.getElementById("username").value
let password = document.getElementById("password").value

let res = await fetch("/login", {
method: "POST",
headers: {
"Content-Type": "application/json"
},
body: JSON.stringify({
username: username,
password: password
})
})

let data = await res.json()

if (data.status === "success") {
window.location = "/app"
} else {
alert("Invalid username or password")
}

}
async function loadPlayers(){

let res = await fetch("/players")
let players = await res.json()

let container = document.getElementById("players")

container.innerHTML=""

players.forEach(p => {

container.innerHTML += `
<div style="border:1px solid white; padding:15px; margin:10px;">
<h3>${p.name}</h3>
<p>Team: ${p.team}</p>
<p>Price: ₹${p.price}</p>
</div>
`

})

}

window.onload = loadPlayers
