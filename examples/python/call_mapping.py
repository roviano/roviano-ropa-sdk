"""
call_mapping.py — Call ROPA services for mapping and navigation.

Real ROPA services (from 72-page protocol):
  /node_manager_control  → cmd: 0(start mapping) / 3(pause) / 4(resume) / 7(stop)
  /poi                   → Navigate to a named point: {op:"call_service", topic:"/poi", type:"poi", args:{poi_name}}
  /get_map_info          → Get current map metadata
  /layered_map_cmd       → op: 0(list maps)

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
    print(f"📞 Calling {service_name} with args={json.dumps(args or {})}")

    # Wait for service_response with matching id
    for _ in range(timeout * 10):
        with result_lock:
            if msg_id in service_results:
                return service_results.pop(msg_id)
        time.sleep(0.1)

    print(f"⚠️  Timeout waiting for response to {msg_id}")
    return None


def on_message(ws, message):
    data = json.loads(message)
    op = data.get("op")

    if op == "service_response":
        msg_id = data.get("id", "")
        result = data.get("result", False)
        values = data.get("values", {})
        print(f"   📩 Service response: id={msg_id}, result={result}")
        if values:
            print(f"   Values: {json.dumps(values, indent=2)[:300]}")
        with result_lock:
            service_results[msg_id] = {"result": result, "values": values}

    elif op == "publish":
        topic = data.get("topic", "")
        if topic == "/navi_status":
            print(f"   🧭 Navigation: goal_status={data.get('msg', {}).get('goal_status')}")

    elif op == "advertise":
        print(f"   📢 Advertise: {data.get('topic')}")


def on_error(ws, error):
    print(f"❌ Error: {error}")


def on_close(ws, code, msg):
    print(f"🔌 Closed: code={code}")


def on_open(ws):
    print("✅ Connected. Running mapping + navigation demo...")

    # Subscribe to navigation status for real-time feedback
    ws.send(json.dumps({
        "op": "subscribe",
        "topic": "/navi_status",
        "type": "navi_status"
    }))
    print("   → Subscribed to /navi_status")

    time.sleep(1)

    # Step 1: Start mapping (cmd=0)
    result = call_service(ws, "/node_manager_control", "node_manager_control", {"cmd": 0})
    if result and result.get("result"):
        print("✅ Mapping started — drive the robot around to build the map")
    else:
        print("⚠️  Mapping start failed")

    time.sleep(3)

    # Step 2: Get map info
    result = call_service(ws, "/get_map_info", "get_map_info")
    if result and result.get("result"):
        print(f"✅ Map info: {json.dumps(result.get('values', {}), indent=2)[:200]}")

    time.sleep(2)

    # Step 3: List available maps (layered_map_cmd op=0)
    result = call_service(ws, "/layered_map_cmd", "layered_map_cmd", {"op": 0})
    if result and result.get("result"):
        print(f"✅ Available maps: {json.dumps(result.get('values', {}), indent=2)[:200]}")

    time.sleep(2)

    # Step 4: Navigate to a named POI (requires a map with POIs defined)
    # This will only work if you have previously saved a POI named "dock"
    result = call_service(ws, "/poi", "poi", {"poi_name": "dock"})
    if result and result.get("result"):
        print("✅ Navigation to 'dock' initiated")
    else:
        print("ℹ️  POI 'dock' not found — define POIs via marker_operation first")

    time.sleep(5)

    # Step 5: Stop mapping (cmd=7)
    result = call_service(ws, "/node_manager_control", "node_manager_control", {"cmd": 7})
    if result and result.get("result"):
        print("✅ Mapping stopped")
    else:
        print("⚠️  Mapping stop failed")

    print("\n--- Demo complete ---")
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
