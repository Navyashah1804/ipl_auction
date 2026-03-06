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
