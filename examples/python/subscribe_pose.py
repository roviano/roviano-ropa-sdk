"""
subscribe_pose.py — Subscribe to /robot_pose and /robot_status via ROPA.

Real ROPA topics (from 72-page protocol):
  /robot_pose  → geometry_msgs/Pose2D  {x, y, theta}
  /robot_status → {battery, charger, nav_status, control_state, velocity, estop, building, floor}

Requirements: pip install websocket-client
"""

import websocket
import json
import sys
import time

ROBOT_IP = "192.168.1.100"  # Replace with your chassis IP
ROPA_PORT = 9090


def on_message(ws, message):
    data = json.loads(message)
    op = data.get("op")

    if op == "publish":
        topic = data.get("topic", "")
        msg = data.get("msg", {})

        if topic == "/robot_pose":
            # Pose2D: x (meters), y (meters), theta (radians)
            x = msg.get("x", 0.0)
            y = msg.get("y", 0.0)
            theta = msg.get("theta", 0.0)
            print(f"📍 Pose: x={x:.3f} m, y={y:.3f} m, θ={theta:.4f} rad ({theta * 57.2958:.1f}°)")

        elif topic == "/robot_status":
            # Robot status: battery, nav_state, velocity, estop, etc.
            battery = msg.get("battery", "?")
            charger = msg.get("charger", "?")
            nav_status = msg.get("nav_status", "?")
            control_state = msg.get("control_state", "?")
            velocity = msg.get("velocity", {})
            estop = msg.get("estop", False)
            building = msg.get("building", "?")
            floor = msg.get("floor", "?")

            print(f"🔋 Status: battery={battery}% | charger={charger} | nav={nav_status} | ctrl={control_state}")
            if estop:
                print("⚠️  E-STOP ACTIVE!")
            print(f"   🏢 Building={building}, Floor={floor}")
            if velocity:
                vx = velocity.get("vx", 0)
                wz = velocity.get("wz", 0)
                print(f"   🏃 Velocity: vx={vx} m/s, wz={wz} rad/s")

        elif topic == "/laser_data":
            px_count = len(msg.get("px", []))
            py_count = len(msg.get("py", []))
            print(f"🔴 Laser: {px_count} points received")

        elif topic == "/navi_status":
            goal_status = msg.get("goal_status", "?")
            print(f"🧭 Navigation status: {goal_status}")

        elif topic == "/localization_confidence":
            conf = msg.get("confidence", 0.0)
            print(f"🎯 Localization confidence: {conf:.2f}")

        else:
            print(f"[{topic}] {json.dumps(msg)[:150]}")


def on_error(ws, error):
    print(f"❌ Error: {error}")


def on_close(ws, code, msg):
    print(f"🔌 Closed: code={code}")


def on_open(ws):
    print("✅ Connected. Subscribing to real-time data...")

    # Subscribe to pose (geometry_msgs/Pose2D format)
    ws.send(json.dumps({
        "op": "subscribe",
        "topic": "/robot_pose",
        "type": "geometry_msgs/Pose2D"
    }))
    print("   → /robot_pose (Pose2D: x, y, theta)")

    # Subscribe to robot status
    ws.send(json.dumps({
        "op": "subscribe",
        "topic": "/robot_status",
        "type": "robot_status"
    }))
    print("   → /robot_status (battery, nav, velocity, estop, building, floor)")

    # Subscribe to navigation status
    ws.send(json.dumps({
        "op": "subscribe",
        "topic": "/navi_status",
        "type": "navi_status"
    }))
    print("   → /navi_status (goal_status)")

    # Subscribe to localization confidence
    ws.send(json.dumps({
        "op": "subscribe",
        "topic": "/localization_confidence",
        "type": "localization_confidence"
    }))
    print("   → /localization_confidence")


def main():
    url = f"ws://{ROBOT_IP}:{ROPA_PORT}"
    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    try:
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ROBOT_IP = sys.argv[1]
    main()
