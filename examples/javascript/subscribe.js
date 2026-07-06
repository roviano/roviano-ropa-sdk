/**
 * subscribe.js — Subscribe to /robot_pose, /robot_status, /laser_data via ROPA.
 *
 * Real ROPA topics (from 72-page protocol):
 *   /robot_pose  → Pose2D {x, y, theta}
 *   /robot_status → {battery, charger, nav_status, control_state, velocity, estop, building, floor}
 *   /laser_data  → {px[], py[]} point cloud arrays
 *   /navi_status → {goal_status}
 *   /localization_confidence → {confidence} 0-1.0
 *
 * Run: node subscribe.js [ROBOT_IP]
 */

const WebSocket = require("ws");

const ROBOT_IP = process.argv[2] || "192.168.1.100";
const ROPA_PORT = 9090;
const url = `ws://${ROBOT_IP}:${ROPA_PORT}`;

console.log(`Connecting to ${url} ...`);

const ws = new WebSocket(url);

const SUBSCRIPTIONS = [
  { topic: "/robot_pose", type: "geometry_msgs/Pose2D" },
  { topic: "/robot_status", type: "robot_status" },
  { topic: "/navi_status", type: "navi_status" },
  { topic: "/localization_confidence", type: "localization_confidence" }
];

ws.on("open", () => {
  console.log("✅ Connected. Subscribing to real-time data...");

  SUBSCRIPTIONS.forEach(({ topic, type }) => {
    ws.send(JSON.stringify({ op: "subscribe", topic, type }));
    console.log(`   → ${topic}`);
  });
});

ws.on("message", (raw) => {
  const data = JSON.parse(raw);
  const op = data.op;

  if (op !== "publish") return;

  const topic = data.topic || "";
  const msg = data.msg || {};

  if (topic === "/robot_pose") {
    // Pose2D: x (m), y (m), theta (rad)
    const { x = 0, y = 0, theta = 0 } = msg;
    const deg = (theta * 57.2958).toFixed(1);
    console.log(`📍 Pose: x=${x.toFixed(3)}m, y=${y.toFixed(3)}m, θ=${theta.toFixed(4)}rad (${deg}°)`);
  }

  else if (topic === "/robot_status") {
    const battery = msg.battery ?? "?";
    const charger = msg.charger ?? "?";
    const navStatus = msg.nav_status ?? "?";
    const ctrlState = msg.control_state ?? "?";
    const estop = msg.estop ?? false;
    const building = msg.building ?? "?";
    const floor = msg.floor ?? "?";
    const velocity = msg.velocity || {};

    console.log(`🔋 Status: battery=${battery}% | charger=${charger} | nav=${navStatus} | ctrl=${ctrlState}`);
    if (estop) console.log("⚠️  E-STOP ACTIVE!");
    console.log(`   🏢 Building=${building}, Floor=${floor}`);
    if (velocity.vx !== undefined) {
      console.log(`   🏃 Velocity: vx=${velocity.vx}m/s, wz=${velocity.wz}rad/s`);
    }
  }

  else if (topic === "/laser_data") {
    const pxLen = msg.px ? msg.px.length : 0;
    const pyLen = msg.py ? msg.py.length : 0;
    console.log(`🔴 Laser: ${pxLen} points (px=${pxLen}, py=${pyLen})`);
  }

  else if (topic === "/navi_status") {
    console.log(`🧭 Navigation: goal_status=${msg.goal_status ?? "?"}`);
  }

  else if (topic === "/localization_confidence") {
    const conf = msg.confidence ?? 0;
    console.log(`🎯 Localization confidence: ${conf.toFixed(2)}`);
  }

  else {
    console.log(`[${topic}] ${JSON.stringify(msg).substring(0, 150)}`);
  }
});

ws.on("error", (err) => {
  console.log(`❌ Error: ${err.message}`);
});

ws.on("close", (code, reason) => {
  console.log(`🔌 Closed: code=${code}`);
});

process.on("SIGINT", () => {
  console.log("\nUnsubscribing...");
  SUBSCRIPTIONS.forEach(({ topic, type }) => {
    ws.send(JSON.stringify({ op: "unsubscribe", topic }));
  });
  ws.close();
  process.exit(0);
});
