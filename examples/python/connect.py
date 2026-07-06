"""
connect.py — Establish a WebSocket connection to an iMRP chassis via ROPA.

ROPA uses WebSocket on port 9090, JSON message format, full-duplex.
This example connects and prints every incoming message.

Requirements: pip install websocket-client
"""

import websocket
import json
import sys

ROBOT_IP = "192.168.1.100"  # Replace with your chassis IP
ROPA_PORT = 9090


def on_message(ws, message):
    """Handle every message pushed by the robot."""
    try:
        data = json.loads(message)
        op = data.get("op", "unknown")
        if op == "publish":
            print(f"[TOPIC] {data.get('topic')} → {json.dumps(data.get('msg', {}), indent=2)[:200]}")
        elif op == "service_response":
            print(f"[SERVICE] result={data.get('result')}, values={data.get('values', {})}")
        else:
            print(f"[{op}] {json.dumps(data)[:200]}")
    except json.JSONDecodeError:
        print(f"[RAW] {message[:200]}")


def on_error(ws, error):
    print(f"❌ WebSocket error: {error}")


def on_close(ws, close_status_code, close_msg):
    print(f"🔌 Connection closed (code={close_status_code}, msg={close_msg})")


def on_open(ws):
    print("✅ Connected to iMRP chassis via ROPA!")
    print(f"   WebSocket: ws://{ROBOT_IP}:{ROPA_PORT}")
    print("   Listening for all incoming messages...")

    # Subscribe to robot status as a basic heartbeat check
    ws.send(json.dumps({
        "op": "subscribe",
        "topic": "/robot_status",
        "type": "robot_status"
    }))
    print("   → Subscribed to /robot_status")


def main():
    url = f"ws://{ROBOT_IP}:{ROPA_PORT}"
    print(f"Connecting to {url} ...")

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
        print("\nDisconnecting...")
        ws.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ROBOT_IP = sys.argv[1]
    main()
