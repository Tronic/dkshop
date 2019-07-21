"use strict";

function setting(width, height) {
	let game = document.getElementById("game");
	game.width = width;
	game.height = height;
}

function loadRequest() {
	sendServer({
		messageType: "LOAD_REQUEST",
	});
}

function hiscore(score) {
	sendServer({
		messageType: "SCORE",
		score: score,
	});
}

function saveGame(gameState) {
	sendServer({
		messageType: "SAVE",
		gameState: gameState,
	});
}

window.addEventListener("message", ev => gameMessage(ev.data));

// Handle a message from game iframe
function gameMessage(data) {
	let t = data.messageType;
	if (t == "SCORE") hiscore(data.score);
	else if (t == "SAVE") saveGame(data.gameState);
	else if (t == "LOAD_REQUEST") loadRequest();
	else if (t == "SETTING") setting(data.options.width, data.options.height);
	else console.log("Unknown message ignored", data);
}

// Handle the server's response to a game message
function serverMessage(data) {
	let t = data.messageType, m = data.siteMeta;
	delete data.siteMeta;  // siteMeta is handled here, avoid passing it to game
	if (m) {
		if (m.refresh) refresh(m.refresh);
	}
	if (!t) return;
	else if (t == "LOAD") sendGame(data);
	else if (t == "ERROR") sendGame(data);  // Errors are displayed by game
	else if (t == "REFRESH") refresh(data.element);  // Refresh a named element on page
	else console.log("Unknown response message ignored", data);
}

// Refresh an element by its id from a reloaded copy of the current document
function refresh(id) {
	let target = document.getElementById(id);
	console.log("Refresh requested for", target || id);
	if (!target) return;
	fetch(document.location).then(resp => resp.text()).then(text => {
		// Construct a temporary div where the fetched document goes
		let tmp = document.createElement("div");
		tmp.innerHTML = text;
		// Find the requested ID
		let refreshed = tmp.querySelector("#" + id);
		target.replaceWith(refreshed);
		// Replace messages
		document.getElementById("messages").replaceWith(tmp.querySelector("#messages"));
	});
}

function sendGame(data) {
	console.log("Message to game", data);
	let game = document.getElementById("game");
	game.contentWindow.postMessage(data, "*");  // Must be * because CORS blocks origin info
}

function sendServer(data) {
	console.log("Message to server", data);
	fetch(document.location, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": document.cookie.match(/csrftoken=([a-zA-Z0-9]*)/)[1],
		},
		body: JSON.stringify(data),
	}).then(resp => resp.text()).then(text => {
		if (text == "") return;
		data = JSON.parse(text);
		console.log("Server response", data);
		serverMessage(JSON.parse(text));
	});
}
