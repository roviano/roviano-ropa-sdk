/**
 * connect.js — Connect to an iMRP chassis via ROPA WebSocket.
 *
 * ROPA: WebSocket port 9090, JSON format, full-duplex.
 * This example connects and logs all incoming messages.
 *
 * Run: node connect.js [ROBOT_IP]
 */

const WebSocket = require("ws");

const ROBOT_IP = process.argv[2] || "192.168.1.100";
const ROPA_PORT = 9090;
const url = `ws://${ROBOT_IP}:${ROPA_PORT}`;

console.log(`Connecting to ${url} ...`);

const ws = new WebSocket(url);

ws.on("open", () => {
  console.log("✅ Connected to iMRP chassis via ROPA!");
  console.log(`   WebSocket: ${url}`);
  console.log("   Listening for all incoming messages...");

  // Subscribe to robot status as a basic heartbeat
  ws.send(JSON.stringify({
    op: "subscribe",
    topic: "/robot_status",
    type: "robot_status"
  }));
  console.log("   → Subscribed to /robot_status");
});

ws.on("message", (raw) => {
  try {
    const data = JSON.parse(raw);
    const op = data.op || "unknown";

    if (op === "publish") {
      const topic = data.topic || "";
      const msg = data.msg || {};
      console.log(`[TOPIC] ${topic} → ${JSON.stringify(msg).substring(0, 200)}`);
    } else if (op === "service_response") {
      console.log(`[SERVICE] result=${data.result}, values=${JSON.stringify(data.values || {}).substring(0, 200)}`);
    } else {
      console.log(`[${op}] ${JSON.stringify(data).substring(0, 200)}`);
    }
  } catch (e) {
    console.log(`[RAW] ${raw.toString().substring(0, 200)}`);
  }
});

ws.on("error", (err) => {
  console.log(`❌ WebSocket error: ${err.message}`);
});

ws.on("close", (code, reason) => {
  console.log(`🔌 Connection closed (code=${code}, reason=${reason || "none"})`);
});

// Keep the process alive
process.on("SIGINT", () => {
  console.log("\nDisconnecting...");
  ws.close();
  process.exit(0);
});
