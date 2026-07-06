"""
move_command.py — Send movement commands and switch velocity modes via ROPA.

Real ROPA topics/services (from 72-page protocol):
  Publish: /cmd_vel_mux/input/teleop → {vx (m/s), wz (rad/s), hold_time (0.6s default)}
  Publish: /soft_stop → emergency soft stop
  Publish: /move_base/cancel → cancel current navigation goal
  Service: /velocity_control → 9 modes: {mode, speed_level, default_speed}

Velocity modes (from protocol page 51):
  mode 0: Normal (default)
  mode 1: Careful (slow, high precision)
  mode 2: Food Delivery (smooth acceleration)
  mode 3-8: Custom application modes
  mode 9: Read current settings

Requirements: pip install websocket-client
"""

import websocket
import json
import sys
import threading
import time

ROBOT_IP = "192.168.1.100"  # Replace with your chassis IP
ROPA_PORT = 9090

service_results = {}
result_lock = threading.Lock()


def call_service(ws, service_name, service_type, args=None, timeout=10):
    """Call a ROPA service and wait for the response."""
    msg_id = f"{service_name}_{int(time.time() * 1000)}"
    request = {
        "op": "call_service",
        "topic": service_name,
        "type": service_type,
        "id": msg_id,
        "args": args or {}
    }
    ws.send(json.dumps(request))
    print(f"📞 Calling {service_name} args={json.dumps(args or {})}")

    for _ in range(timeout * 10):
        with result_lock:
            if msg_id in service_results:
                return service_results.pop(msg_id)
        time.sleep(0.1)

    print(f"⚠️  Timeout on {msg_id}")
    return None


def send_velocity(ws, vx, wz, hold_time=0.6):
    """Send a velocity command via /cmd_vel_mux/input/teleop.

    ROPA differential drive model: vx (linear, m/s) + wz (angular, rad/s).
    hold_time: how long the command persists before auto-stopping (0.6s default).
    """
    ws.send(json.dumps({
        "op": "publish",
        "topic": "/cmd_vel_mux/input/teleop",
        "msg": {
            "vx": vx,
            "wz": wz,
            "hold_time": hold_time
        }
    }))
    direction = "forward" if vx > 0 else ("backward" if vx < 0 else "stop")
    turn = "left" if wz > 0 else ("right" if wz < 0 else "straight")
    print(f"🏃 Command: {direction} vx={vx} m/s, {turn} wz={wz} rad/s, hold={hold_time}s")


def soft_stop(ws):
    """Send emergency soft stop — immediately halts all motion."""
    ws.send(json.dumps({
        "op": "publish",
        "topic": "/soft_stop",
        "msg": {}
    }))
    print("🛑 SOFT STOP sent — all motion halted")


def cancel_navigation(ws):
    """Cancel the current navigation goal."""
    ws.send(json.dumps({
        "op": "publish",
        "topic": "/move_base/cancel",
        "msg": {}
    }))
    print("❌ Navigation goal cancelled")


def on_message(ws, message):
    data = json.loads(message)
    op = data.get("op")

    if op == "service_response":
        msg_id = data.get("id", "")
        result = data.get("result", False)
        values = data.get("values", {})
        print(f"   📩 Response: id={msg_id}, result={result}")
        if values:
            print(f"   Values: {json.dumps(values, indent=2)[:300]}")
        with result_lock:
            service_results[msg_id] = {"result": result, "values": values}

    elif op == "publish":
        topic = data.get("topic", "")
        if topic == "/robot_status":
            msg = data.get("msg", {})
            velocity = msg.get("velocity", {})
            if velocity:
                print(f"   🏃 Actual: vx={velocity.get('vx')} wz={velocity.get('wz')}")


def on_error(ws, error):
    print(f"❌ Error: {error}")


def on_close(ws, code, msg):
    print(f"🔌 Closed: code={code}")


def on_open(ws):
    print("✅ Connected. Running movement demo...")

    # First, advertise that we will publish to /cmd_vel_mux/input/teleop
    ws.send(json.dumps({
        "op": "advertise",
        "topic": "/cmd_vel_mux/input/teleop",
        "type": "geometry_msgs/Twist"
    }))
    print("   📢 Advertised /cmd_vel_mux/input/teleop")

    # Subscribe to robot status to see actual velocity
    ws.send(json.dumps({
        "op": "subscribe",
        "topic": "/robot_status",
        "type": "robot_status"
    }))
    print("   → Subscribed to /robot_status")

    time.sleep(1)

    # Step 1: Read current velocity settings (mode 9 = read)
    result = call_service(ws, "/velocity_control", "velocity_control", {
        "mode": 9
    })
    if result and result.get("result"):
        print(f"✅ Current velocity config: {json.dumps(result.get('values', {}), indent=2)[:200]}")

    time.sleep(1)

    # Step 2: Switch to Normal mode (mode 0)
    result = call_service(ws, "/velocity_control", "velocity_control", {
        "mode": 0,
        "speed_level": 0,
        "default_speed": {"vx": 0.5, "wz": 0.5}
    })
    if result and result.get("result"):
        print("✅ Velocity mode: Normal (mode 0)")

    time.sleep(1)

    # Step 3: Move forward at 0.3 m/s for 3 seconds
    send_velocity(ws, vx=0.3, wz=0.0, hold_time=0.6)
    print("   Moving forward for 3 seconds...")
    time.sleep(3)

    # Step 4: Turn left (wz > 0 in right-hand coordinate system)
    send_velocity(ws, vx=0.0, wz=0.3, hold_time=0.6)
    print("   Turning left for 2 seconds...")
    time.sleep(2)

    # Step 5: Arc turn (forward + left simultaneously)
    send_velocity(ws, vx=0.2, wz=0.15, hold_time=0.6)
    print("   Arc turn for 2 seconds...")
    time.sleep(2)

    # Step 6: Soft stop
    soft_stop(ws)
    time.sleep(1)

    # Step 7: Switch to Food Delivery mode (mode 2 — smoother acceleration)
    result = call_service(ws, "/velocity_control", "velocity_control", {
        "mode": 2,
        "speed_level": 0,
        "default_speed": {"vx": 0.3, "wz": 0.3}
    })
    if result and result.get("result"):
        print("✅ Velocity mode: Food Delivery (mode 2 — smooth accel)")

    time.sleep(1)

    # Step 8: Move forward in food delivery mode
    send_velocity(ws, vx=0.3, wz=0.0, hold_time=0.6)
    print("   Moving forward (smooth mode) for 3 seconds...")
    time.sleep(3)

    # Final stop
    soft_stop(ws)

    print("\n--- Movement demo complete ---")
    ws.close()


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
