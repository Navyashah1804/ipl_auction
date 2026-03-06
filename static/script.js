

const container=document.getElementById("players")
const filter=document.getElementById("filter")

async function loadPlayers(){

let type=filter.value

let res=await fetch(`/players?type=${type}`)
let data=await res.json()

container.innerHTML=""

data.forEach(p=>{

let card=document.createElement("div")
card.className="card"

card.innerHTML=`

<h3>${p.name}</h3>
<p>Team: ${p.team}</p>
<p>Strike Rate: ${p.strike_rate}</p>
<p>Current Bid: ₹${p.current_bid}</p>

<input id="bid-${p.id}" placeholder="Enter bid">

<button onclick="bid(${p.id})">Place Bid</button>

`

container.appendChild(card)

})

}

async function bid(id){

let bid=document.getElementById(`bid-${id}`).value

await fetch("/bid",{
method:"POST",
headers:{ "Content-Type":"application/json" },
body:JSON.stringify({
player_id:id,
bid:bid
})
})

loadPlayers()

}

filter.addEventListener("change",loadPlayers)

loadPlayers()
