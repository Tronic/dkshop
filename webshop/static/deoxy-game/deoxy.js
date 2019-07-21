"use strict";
const tau = 2.0 * Math.PI;  // One full revolution in radians
const vw = 1280, vh = 720;
const ground_y = 600;
const cx = document.querySelector("canvas").getContext("2d");

let paused = true;

let state;

function reset() {
	state = Object.create(null);
	state.t = 0;
	state.points = 0;
	// Player position and velocity
	state.x = 500.0;
	state.y = 100.0;
	state.xv = 1.0;
	state.yv = 0.0;
	state.feet_a = 0.0;
	// Oxygen array
	state.oxy = [];
	// Viewport
	state.vx = 0.0;
	state.vy = 0.0;
	state.vxv = 0.0;
	state.vyv = 0.0;
	points(0);
}

reset();

let img = document.createElement("img");
img.src = "ground.png";

let lastTime = 0;

function update(newTime) {
	if (paused) return;
	// Animations are designed for 120 Hz; repeat as necessary if running at lower rate
	let repeats = Math.round((newTime - lastTime) / 8.4 /* ms */);
	lastTime = newTime;
	if (repeats > 8) repeats = 1;  // In case of longer warps (e.g. when starting)
	while (repeats--) animate();
	draw();
	requestAnimationFrame(update);
}

function xdir() {
	let dir = 0;
	if (down.ArrowLeft) dir -= 1;
	if (down.ArrowRight) dir += 1;
	return dir;
}

function animate() {
	state.t += 1;
	// Spawn new oxy
	if (state.t % 30 == 0) {
		if (state.oxy.length > 200) {
			gameOver();
		}
		let x = Math.random() * 10000.0;
		let y = -100;
		state.oxy.push({x:x, y:y, xv:2.0 * Math.random() - 1.0, yv:Math.random()});
		document.getElementById("oxy").setAttribute("value", state.oxy.length);
	}
	// Player movement
	const playerH = 70;
	let onGround = (Math.round(state.y, -1) == ground_y - playerH);
	if (onGround) {
		state.xv += 0.3 * xdir();
		state.xv *= 0.98;
		state.feet_a += state.xv / 20.0;
	} else {
		state.feet_a += 0.1 * xdir();
	}
	if (onGround && Math.abs(state.yv) < 2.0) {
		state.xv += 0.2 * xdir() * Math.abs(state.yv);
		state.yv = (down.ArrowUp ? -10.0 : 0.0);
	}
	else if (state.y > ground_y - playerH && state.yv > 0) {
		// Bounce off ground
		state.yv = -(down.ArrowUp ? 1.1 : 0.4) * state.yv;
		if (down.ArrowUp && state.yv > -10.0) state.yv = -10.0;  // Ensure minimum jump
		state.xv += 0.8 * xdir() * Math.abs(state.yv);
		state.xv *= 0.6;
	}
	state.feet_a = state.feet_a % tau;
	state.x += state.xv;
	state.y += state.yv;
	state.xv *= 0.998; state.yv *= 0.998;  // Air friction
	state.yv += 0.2;
	// Align viewport with player
	if (state.x > state.vx + 0.5 * vw) state.vxv += 1.0;
	else if (state.x < state.vx + 0.2 * vw) state.vxv -= 1.0;
	state.vx += state.vxv;
	state.vxv *= 0.95;
	state.vy = (state.y - (ground_y - playerH)) / 10.0;
	// Oxygen animation and player collisions
	let oxy = [];
	for (const o of state.oxy) {
		// Oxy-player collision
		if (collide(state, o) < 0.0) {
			points(100);
			continue;
		}
		// Inter-oxy collisions
		for (const c of oxy) collide(c, o);
		// Ground and sky
		if (o.y > ground_y - 40) o.yv *= -1;
		if (o.y < -100) o.yv *= -1;
		// Apply motion
		o.x += o.xv;
		o.y += o.yv;
		// Preserve for next round
		oxy.push(o);
	}
	state.oxy = oxy;
}

function collide(a, b) {
	let dx = (a.x - b.x) / 80.0;
	let dy = (a.y - b.y) / 80.0;
	let dist = dx * dx + dy * dy;
	if (dist < 1.0) {
		dist = Math.sqrt(dist);
		dx /= dist;
		dy /= dist;
		let f = (b.xv - a.xv) * dx + (b.yv - a.yv) * dy;
		if (f > 0) {
			a.xv += f * dx;
			a.yv += f * dy;
			b.xv -= f * dx;
			b.yv -= f * dy;
			return dy;
		}
	}
	return false;
}

function points(amount) {
	if (amount) state.points += amount;
	document.getElementById('points').value = state.points;
}

function draw() {
	cx.clearRect(0, 0, vw, vh);
	drawGround();
	cx.save();
	cx.translate(-state.vx, -state.vy);
	drawOxy();
	drawPlayer();
	cx.restore();
}

function drawGround() {
	const tilew = 1280, tileh = 128;
	let ti = Math.round(state.vx / tilew - 0.5);
	let tx = ti * tilew - state.vx;
	for (let i = 0; i < vw / tilew + 1; ++i) {
		cx.drawImage(img, 0, 0, tilew, tileh, tx + i * tilew, ground_y - state.vy, tilew, tileh);
	}
}

function drawOxy() {
	let a0 = 0.01 * state.t;
	for (const o of state.oxy) {
		cx.save();
		cx.translate(o.x, o.y);
		cx.rotate(a0);
		a0 += 0.02;
		cx.fillStyle = "#f00"; cx.beginPath(); cx.ellipse(0, 0, 15, 15, 0, 0, tau); cx.fill();
		cx.fillStyle = "#00f";
		for (let i = 0; i < 6; ++i) {
			cx.rotate(tau/6);
			cx.beginPath();
			let a = 0.07 * state.t - i * tau / 3.0;
			a %= tau;
			cx.ellipse(35.0 * Math.cos(a), 10.0 * Math.sin(a), 5, 5, 0, 0, tau); cx.fill();
		}
		cx.restore();
	}
}

function drawPlayer() {
	cx.save();
	cx.translate(state.x, state.y);
	// Feet
	cx.fillStyle = "#f60";
	cx.lineWidth = 2;
	const feet_a = state.feet_a;
	cx.beginPath(); cx.ellipse(-5.0 * xdir() + 20.0 * Math.cos(feet_a), 60 - 2.0 * state.yv + 2.0 * Math.sin(feet_a), 15.0, 10.0, 0, 0, tau); cx.fill(); cx.stroke();
	cx.beginPath(); cx.ellipse(-5.0 * xdir() + 20.0 * Math.cos(feet_a + .5 * tau), 60 - 2.0 * state.yv + 2.0 * Math.sin(feet_a + .5 * tau), 15.0, 10.0, 0, 0, tau); cx.fill(); cx.stroke();
	// Body
	cx.save();
	if (state.xv < 0.0) cx.scale(-1.0, 1.0);
	cx.lineWidth = 5;
	cx.fillStyle = "#f60";
	cx.beginPath();
	let r = 35;
	cx.arc(0, 0, r, 0.2, 6.1);
	cx.lineTo(0, 0);
	cx.closePath();
	cx.stroke();
	cx.fill();
	// Eye
	cx.fillStyle = "#000";
	cx.beginPath();
	cx.arc(16, -19, 5, 0, 7);
	cx.fill();
	cx.restore();
	cx.restore();
}

// Keyboard tracking (readable via down.ArrowLeft etc)
const keys = ["ArrowLeft", "ArrowRight", "ArrowUp"];
let down = Object.create(null);
function track(event) {
	if (keys.includes(event.key)) {
		down[event.key] = event.type == "keydown";
		event.preventDefault();
	}
}
window.addEventListener("keydown", track);
window.addEventListener("keyup", track);

function gameOver() {
	window.parent.postMessage({messageType: "SCORE", score: state.points}, "*");
	reset();
}

function save() {
	window.parent.postMessage({messageType: "SAVE", gameState: state}, "*");
}

function load() {
	window.parent.postMessage({messageType: "LOAD_REQUEST"}, "*");
}

window.parent.postMessage({messageType: "SETTING", options: { width: vw, height: vh }}, "*");

window.addEventListener("message", (ev)=> {
	if (ev.data.messageType == "LOAD") state = ev.data.gameState;
	if (ev.data.messageType == "ERROR") alert(ev.data.info);
});

window.addEventListener("focus", (ev)=> { paused = false; requestAnimationFrame(update); });
window.addEventListener("blur", (ev)=> { paused = true; });

// Draw initial placement once loaded (but still paused)
window.addEventListener("load", draw);
