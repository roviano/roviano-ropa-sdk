# ROPA SDK — Open Platform API for iMRP Mobile Robot Chassis

WebSocket + JSON. Full data access to every sensor, every motor, every navigation command. No black box.

**One protocol, four chassis models** — iMRP400 / iMRP500 / iMRP600 / iMRP800 all share the same ROPA API on port 9090.

---

## Supported Hardware

| Model | Payload | Max Speed | Positioning Accuracy | Signature Feature |
|-------|---------|-----------|---------------------|-------------------|
| iMRP400 | 20 kg | 0.5 m/s | ±10 cm | RGBD 3D Vision · Ultra-Compact |
| iMRP500 | 50 kg | 0.8 m/s | ±5 cm | Differential Drive · Warehouse-Ready |
| iMRP600 | 100 kg | 0.8 m/s | ±10 cm | Autonomous Elevator Riding · Dual-LiDAR |
| iMRP800 | 100 kg | 1.2 m/s | ±10 cm | 1.2 m/s Fast Transit · 800 mm Wide |

See [`docs/models.md`](docs/models.md) for full specifications per model.

---

## Quick Start

```python
import websocket, json

def on_message(ws, message):
    data = json.loads(message)
    print("Received:", data["topic"], data)

def on_open(ws):
    ws.send(json.dumps({
        "op": "subscribe",
        "topic": "/robot_pose",
        "type": "geometry_msgs/Pose2D"
    }))

ws = websocket.WebSocketApp(
    "ws://<ROBOT_IP>:9090",
    on_open=on_open,
    on_message=on_message
)
ws.run_forever()
```

See [`examples/`](examples/) for Python, JavaScript, and Android examples.

---

## Documentation

- **Protocol reference**: [`docs/protocol.md`](docs/protocol.md) — core operations, topics, and service calls
- **Model specifications**: [`docs/models.md`](docs/models.md) — per-model hardware parameters
- **Android DeploymentTool**: [`docs/android-deployment.md`](docs/android-deployment.md) — field deployment guide

---

## Developer Kit & Integrator Packages

### Developer Kit (from $2,699 FOB)
Chassis + ROPA SDK + full documentation + 1-on-1 engineer support.
→ For developers who want to code their own application.

### Integrator Package (from $2,899 FOB)
Developer Kit + on-site deployment service + priority support + integration recipes.
→ For integrators who need production-ready deployment.

**Get the hardware:**

👉 [Roviano on Alibaba.com](https://roviano.en.alibaba.com) — iMRP400 / 500 / 600 / 800

**Contact:** engineering@roviano.com

---

## What ROPA Gives You

- **Full sensor access**: LiDAR scans, RGBD depth, ultrasonic, IMU, battery — all via subscribe topics
- **Full control**: velocity commands, mapping, navigation, POI management — all via service calls
- **No black box**: every topic, every service, every status code documented in [`docs/protocol.md`](docs/protocol.md)
- **ROS-bridgeable**: not "ROS2 native" — use ROPA as your data bridge into any ROS version you prefer

---

## Examples

| Example | Language | What it demonstrates |
|---------|----------|---------------------|
| [`connect.py`](examples/python/connect.py) | Python | WebSocket connection + status subscription |
| [`subscribe_pose.py`](examples/python/subscribe_pose.py) | Python | Multi-topic subscription (pose, status, localization) |
| [`call_mapping.py`](examples/python/call_mapping.py) | Python | Service calls: mapping, POI, map management |
| [`move_command.py`](examples/python/move_command.py) | Python | Velocity control + 9 speed modes + soft stop |
| [`connect.js`](examples/javascript/connect.js) | JavaScript | WebSocket connection from Node.js |
| [`subscribe.js`](examples/javascript/subscribe.js) | JavaScript | Multi-topic subscription in JS |

---

## Related

- **[ROPA Docs Repository](https://github.com/roviano/ropa-docs)** — deployment guides, integration recipes, scenario tutorials for integrators

---

## License

MIT — use commercially, modify freely, no restrictions.
