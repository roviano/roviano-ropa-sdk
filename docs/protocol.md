# ROPA Protocol Reference

> Source: *Upper Computer Communication Protocol* (72-page official document)
> Transport: WebSocket (default port **9090**), JSON format, full-duplex
> Compatible models: iMRP400 / iMRP500 / iMRP600 / iMRP800

---

## 1. Operation Types

Every message has an `op` field identifying its type:

| `op` | Direction | Description |
|------|-----------|-------------|
| `advertise` | Client → Robot | Register as a publisher for a topic |
| `publish` | Client → Robot | Send data to a topic |
| `unadvertise` | Client → Robot | Stop publishing to a topic |
| `subscribe` | Client → Robot | Subscribe to a topic (robot will push data) |
| `unsubscribe` | Client → Robot | Stop receiving a topic |
| `call_service` | Client → Robot | Request a service execution |
| `service_response` | Robot → Client | Service execution result |

---

## 2. Subscribe Topics

Subscribe to receive real-time data from the robot. Send:

```json
{
  "op": "subscribe",
  "topic": "/robot_pose",
  "type": "geometry_msgs/Pose2D",
  "throttle_rate": 100
}
```

Unsubscribe:

```json
{
  "op": "unsubscribe",
  "topic": "/robot_pose"
}
```

### 2.1 `/robot_pose` — Robot Position (Pose2D)

```json
{
  "op": "publish",
  "topic": "/robot_pose",
  "msg": {
    "x": 1.23,
    "y": 4.56,
    "theta": 0.78
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `x` | float | X coordinate in world frame (meters) |
| `y` | float | Y coordinate in world frame (meters) |
| `theta` | float | Heading angle (radians, counterclockwise positive) |

### 2.2 `/laser_data` — LiDAR Point Cloud

```json
{
  "op": "publish",
  "topic": "/laser_data",
  "msg": {
    "px": [0.1, 0.2, ...],
    "py": [0.3, 0.4, ...]
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `px` | float[] | X coordinates of scan points (robot frame) |
| `py` | float[] | Y coordinates of scan points (robot frame) |

> Point cloud is in the **robot coordinate system**. To convert to world coordinates, see §8.

### 2.3 `/global_path` — Navigation Path

```json
{
  "op": "publish",
  "topic": "/global_path",
  "msg": {
    "poses": [{"x": 1.0, "y": 2.0}, ...]
  }
}
```

### 2.4 `/map` — Occupancy Grid Map

```json
{
  "op": "publish",
  "topic": "/map",
  "msg": {
    "data": "<base64-encoded PNG>",
    "width": 1024,
    "height": 1024,
    "resolution": 0.05,
    "origin_x": -25.6,
    "origin_y": -25.6
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `data` | string | PNG image, base64-encoded |
| `width` | int | Map width in pixels |
| `height` | int | Map height in pixels |
| `resolution` | float | Meters per pixel |
| `origin_x` | float | World X coordinate of pixel [0][0] |
| `origin_y` | float | World Y coordinate of pixel [0][0] |

> Large maps may be fragmented. Each fragment has a `fragment_size` field. Reassemble before decoding.

### 2.5 `/robot_status` — Full Robot Status

```json
{
  "op": "publish",
  "topic": "/robot_status",
  "msg": {
    "battery": 85,
    "charger": 0,
    "nav_status": 601,
    "control_state": 30,
    "velocity": {"vx": 0.5, "wz": 0.0},
    "estop": false
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `battery` | int | Battery percentage (0–100) |
| `charger` | int | 0 = not charging, 1 = charging |
| `nav_status` | int | Navigation status code (see §7) |
| `control_state` | int | 20 = mapping, 30 = navigation, 99 = error |
| `velocity` | object | `{vx: linear m/s, wz: angular rad/s}` |
| `estop` | bool | Emergency stop active |
| `building` | string | Current building name (if multi-floor) |
| `floor` | string | Current floor name |

### 2.6 `/navi_status` — Navigation Goal Status

```json
{
  "op": "publish",
  "topic": "/navi_status",
  "msg": {
    "status": 601
  }
}
```

| Status | Meaning |
|--------|---------|
| 600 | Waiting |
| 601 | Running (in service) |
| 602 | Cancelled |
| 603 | Success |
| 604 | Failed |

### 2.7 `/obstacle_region` — Obstacle Detection Zones

```json
{
  "op": "publish",
  "topic": "/obstacle_region",
  "msg": {
    "region": 0
  }
}
```

| Region | Meaning |
|--------|---------|
| 0 | Clear (no obstacles) |
| 1 | Obstacle on right |
| 2 | Obstacle in front |
| 4 | Obstacle on left |

> Values can combine (bitmask): e.g. `6` = front + left.

### 2.8 `/localization_confidence` — Localization Quality

```json
{
  "op": "publish",
  "topic": "/localization_confidence",
  "msg": {
    "confidence": 0.92
  }
}
```

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `confidence` | float | 0.0–1.0 | Localization match confidence |

> Default threshold is 0.8. Below this, the `safety_controller` notification fires.

### 2.9 `/notification` — System Alerts

```json
{
  "op": "publish",
  "topic": "/notification",
  "msg": {
    "name": "system_monitor",
    "level": 16,
    "msg": "激光雷达异常"
  }
}
```

### 2.10 `/mobile_base/sensors/core` — Chassis Core Sensors

```json
{
  "op": "publish",
  "topic": "/mobile_base/sensors/core",
  "msg": {
    "battery": 85,
    "charger": 0,
    "over_current": false,
    "buttons": {"power": false, "estop": false},
    "encoder": {"left": 1200, "right": 1198},
    "ultrasound": {"left": 0.5, "mid": 2.0, "right": 0.3}
  }
}
```

---

## 3. Publish Topics

Send commands to the robot by publishing to these topics.

### 3.1 `/cmd_vel_mux/input/teleop` — Motion Control (Twist)

```json
{
  "op": "publish",
  "topic": "/cmd_vel_mux/input/teleop",
  "msg": {
    "linear": {"x": 0.3, "y": 0, "z": 0},
    "angular": {"x": 0, "y": 0, "z": 0.1}
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `linear.x` | float | Forward/backward speed (m/s) |
| `angular.z` | float | Rotation speed (rad/s) |

> **Hold time**: Commands are held for **0.6 seconds**. For continuous motion, re-publish within this window.

### 3.2 `/move_base/cancel` — Cancel Navigation

```json
{
  "op": "publish",
  "topic": "/move_base/cancel",
  "msg": {}
}
```

### 3.3 `/soft_stop` — Soft Emergency Stop

```json
{
  "op": "publish",
  "topic": "/soft_stop",
  "msg": {
    "data": true
  }
}
```

| `data` | Effect |
|--------|--------|
| `true` | Engage soft stop (decelerate to halt) |
| `false` | Release soft stop |

### 3.4 `/insert_current_pose_marker` — Mark Current Position as POI

```json
{
  "op": "publish",
  "topic": "/insert_current_pose_marker",
  "msg": {
    "name": "dock_A",
    "behavior_code": 0,
    "time_out": 10,
    "rest_time": 5
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | POI name |
| `behavior_code` | int | Behavior type at this point |
| `time_out` | int | Timeout in seconds |
| `rest_time` | int | Rest duration in seconds |

### 3.5 `/get_current_map` — Trigger Map Callback

```json
{
  "op": "publish",
  "topic": "/get_current_map",
  "msg": {}
}
```

> After publishing, the robot will push `/map` data to all subscribers.

### 3.6 `/node_manager/laser_safety_controller` — Laser Safety Toggle

```json
{
  "op": "publish",
  "topic": "/node_manager/laser_safety_controller",
  "msg": {
    "data": true
  }
}
```

### 3.7 `/node_manager/laser_safety_range` — Laser Safety Distance Threshold

```json
{
  "op": "publish",
  "topic": "/node_manager/laser_safety_range",
  "msg": {
    "data": 0.3
  }
}
```

> Minimum: **0.3 m**. The robot will decelerate/stop when obstacles are within this range.

### 3.8 `/laser_safety_controller/setting_confidence_threshold` — Localization Confidence Threshold

```json
{
  "op": "publish",
  "topic": "/laser_safety_controller/setting_confidence_threshold",
  "msg": {
    "data": 0.8
  }
}
```

> Range: 0.0–1.0. Default: 0.8. Below this value, navigation is suspended for safety.

---

## 4. Service Calls

Request service execution and receive a `service_response`.

### 4.1 `/node_manager_control` — Mode Switching (Mapping / Navigation)

```json
{
  "op": "call_service",
  "id": "mode_switch_1",
  "service": "/node_manager_control",
  "args": {
    "cmd": 0
  }
}
```

| `cmd` | Action |
|-------|--------|
| 0 | Start mapping mode |
| 3 | Save current map |
| 4 | Start navigation mode (requires saved map) |
| 7 | Switch to a different map |

Response:

```json
{
  "op": "service_response",
  "id": "mode_switch_1",
  "service": "/node_manager_control",
  "result": true,
  "values": {
    "result": 0,
    "info": "this message success"
  }
}
```

### 4.2 `/velocity_control` — Speed Mode Configuration

```json
{
  "op": "call_service",
  "id": "service_velocity_control",
  "service": "/velocity_control",
  "args": {
    "cmd": 4,
    "str": ""
  }
}
```

| `cmd` | Mode |
|-------|------|
| 0 | Safety low speed |
| 1 | Safety medium speed |
| 2 | Safety high speed |
| 3 | Balance low speed |
| 4 | Balance medium speed |
| 5 | Balance high speed |
| 6 | Efficiency low speed |
| 7 | Efficiency medium speed |
| 8 | Efficiency high speed |
| -1 | Default mode (factory default, takes effect on next boot) |
| 60 | Smooth mode (food delivery mode) |
| 61 | Disable smooth mode (returns to default) |
| 99 | Get current speed mode (read-only) |

### 4.3 `/self_diagnosis` — Hardware Self-Test

```json
{
  "op": "call_service",
  "id": "service_self_diagnosis",
  "service": "/self_diagnosis",
  "args": {}
}
```

> Wait several seconds for results. The robot tests: encoders (L/R), battery voltage, charger, ultrasonic (L/M/R), LiDAR, depth camera, network, IMU, IR recharge signal.

Response `values.status` is an array:

```json
{
  "status": [
    {"hardware_id": "激光雷达", "level": 0, "message": "激光雷达正常工作"},
    {"hardware_id": "编码器左", "level": 2, "message": "编码器左 传感器数据未收到"}
  ]
}
```

| `level` | Meaning |
|---------|---------|
| 0 | Normal |
| 1 | Warning |
| 2 | Error |
| 3 | Data timeout |

### 4.4 `/robot_info` — Robot Version Information

```json
{
  "op": "call_service",
  "id": "service_robot_info",
  "service": "/robot_info",
  "args": {"cmd": 0}
}
```

Response:

```json
{
  "values": {
    "robot_id": "TY1251C003_0036",
    "firmware_version": "1.0.2",
    "robot_type": "TONG",
    "software_version": "4.1.0-alpha",
    "hardware_version": "2.0.0"
  }
}
```

### 4.5 `/poi` — Navigate to Named Point

```json
{
  "op": "call_service",
  "id": "nav_to_dock",
  "service": "/poi",
  "args": {
    "poi_name": "dock_A",
    "poi_floor": "1",
    "poi_building": "Building1"
  }
}
```

### 4.6 `/get_map_info` — Current Map Metadata

```json
{
  "op": "call_service",
  "id": "map_info_query",
  "service": "/get_map_info",
  "args": {"cmd": 0}
}
```

### 4.7 `/layered_map_cmd` — Map Management

```json
{
  "op": "call_service",
  "id": "map_list",
  "service": "/layered_map_cmd",
  "args": {"op": 0}
}
```

| `op` | Action |
|------|--------|
| 0 | List all maps (buildings + floors) |

### 4.8 `/marker_operation/get_markers` — Get All POI Markers

```json
{
  "op": "call_service",
  "id": "get_markers",
  "service": "/marker_operation/get_markers",
  "args": {}
}
```

### 4.9 `/marker_manager/delete_poi` — Delete a POI Marker

```json
{
  "op": "call_service",
  "id": "delete_poi",
  "service": "/marker_manager/delete_poi",
  "args": {
    "name": "dock_A",
    "floor": "1",
    "building": "Building1"
  }
}
```

### 4.10 `/building_operation/delete` — Delete a Building

```json
{
  "op": "call_service",
  "id": "delete_building",
  "service": "/building_operation/delete",
  "args": {
    "building": "Building1"
  }
}
```

### 4.11 `/get_match_threshold` — Map Matching Threshold

```json
{
  "op": "call_service",
  "id": "service_get_match_threshold",
  "service": "/get_match_threshold",
  "args": {"cmd": 0, "str": ""}
}
```

Response: `values.result` returns the threshold as a percentage (e.g. `80`).

### 4.12 `/calculate_distance` — Path Distance Between Two Points

```json
{
  "op": "call_service",
  "id": "service_calculate_distance",
  "service": "/calculate_distance",
  "args": {
    "start_x": 0.1,
    "start_y": 0.2,
    "start_floor": "1",
    "goal_x": 1.1,
    "goal_y": 1.2,
    "goal_floor": "1"
  }
}
```

Response: `values.distance` returns navigation path distance in **meters**.

| `result` code | Meaning |
|----------------|---------|
| 0 | Success |
| 10 | Previous command still running |
| 150 | Path planning failed (unreachable) |
| 151 | Path calculation server error |
| 152 | Cross-floor calculation not supported |

---

## 5. Map Data Fragmentation

Large map data is fragmented for transmission. Each fragment includes:

| Field | Description |
|-------|-------------|
| `fragment_size` | Number of total fragments |
| `fragment_index` | Current fragment index (0-based) |
| `data` | Base64-encoded PNG fragment |

Reassemble all fragments in order, then decode the concatenated base64 string.

---

## 6. Active Notification System

The robot autonomously pushes alerts via `/notification` topic:

| Notification Name | Trigger | Level | Message |
|-------------------|---------|-------|---------|
| `system_monitor` | LiDAR anomaly | 16 | Error-specific info |
| `system_monitor` | Chassis drive anomaly | 16 | Error sensor name array (left motor, right motor, IMU, battery) |
| `safety_controller` | Map matching threshold low | 4 | Current match value |
| `safety_controller` | Matching function toggle | 1 | Switch prompt |
| `laser_data` | Most LiDAR data invalid | 4 | Warning message |
| `laser_data` | Data validity toggle | 1 | Switch prompt |

---

## 7. Status Code Reference

### General (0–99)

| Code | Meaning |
|------|---------|
| 0 | Command executed successfully |
| 10 | Command being processed |
| 20 | Mapping mode active |
| 30 | Navigation mode active |
| 99 | Unknown input command |

### Program Control (101–110)

| Code | Meaning |
|------|---------|
| 101 | Close error (program not started) |
| 102 | Start invalid (already running) |
| 104 | No corresponding map |
| 105 | No permission to control |
| 106 | System fatal error (restart required) |
| 107 | Missing building/floor info |
| 108 | Map file damaged |
| 109 | Current mode does not support command |
| 110 | Save map error |

### Floor / Map / Virtual Wall / POI (2XX–5XX)

Shared base pattern: 2XX=floor, 3XX=map, 4XX=virtual wall, 50X=POI, 55X=area

| Code | Meaning |
|------|---------|
| 201 | Invalid path |
| 202 | No corresponding file |
| 203 | No data content |
| 204 | No access permission |
| 205 | File damaged |
| 206 | Map data acquisition timeout |
| 207 | Mapping mode does not support loading map |
| 208 | Failed to save data file |

### Navigation (600–647)

| Code | Meaning |
|------|---------|
| 600 | Initialize waiting |
| 601 | Running (in service) |
| 602 | Cancelled |
| 603 | Success |
| 604 | Failed |
| 605 | Refused |
| 606 | Cancellation in progress |
| 607 | Reset in progress |
| 608 | Reset completed |
| 609 | Status lost |
| 620 | Configuration failed |
| 621 | Emergency stop triggered |

### Cross-Floor Navigation (630–647)

| Code | Meaning |
|------|---------|
| 630 | Input error |
| 631 | Target floor invalid |
| 632 | Target marker invalid |
| 633 | Marker point retrieval error |
| 634 | Elevator-related point invalid |
| 635 | Cross-floor navigation failed |
| 636 | Cross-floor navigation cancelled |
| 637 | Elevator reservation failed |
| 639 | Cross-floor navigation waiting |
| 640 | Feasibility detection |
| 641 | Navigate to elevator exterior |
| 642 | Wait for elevator at designated floor |
| 643 | Entering elevator |
| 644 | Switching map |
| 645 | Leaving elevator |
| 646 | Navigate to target point |
| 647 | Cross-floor navigation complete |

### Multi-Point Navigation (650–660)

| Code | Meaning |
|------|---------|
| 650 | Multi-point navigation completed |
| 651 | Multi-point navigation running |
| 652 | Multi-point navigation paused |
| 653 | Multi-point navigation continuing |
| 656 | Running but some points invalid |
| 657 | Only one valid point (insufficient for cruise) |

### IR Recharge (901–920)

| Code | Meaning |
|------|---------|
| 901 | Recharge success |
| 902 | IR signal not detected |
| 903 | Charging pile not found |
| 904 | Recharge timeout |
| 905 | Recharge operation in progress |
| 906 | Recharge cancelled |

### Global Self-Localization (1001–1099)

| Code | Meaning |
|------|---------|
| 1001 | Self-localization running |
| 1002 | Area self-localization input too few vertices |
| 1005 | Too little or invalid radar data during positioning |
| 1099 | Unexpected failure (log investigation required) |

---

## 8. Coordinate System & Algorithm Notes

### 8.1 Right-Hand 3D Cartesian Coordinate System

- **X-axis**: forward direction of the robot
- **Y-axis**: left (right-hand thumb)
- **Z-axis**: upward (right-hand index finger)
- Euler angles: **roll** (X), **pitch** (Y), **yaw** (Z, counterclockwise positive)

### 8.2 Point Cloud → World Coordinate Transform

Given robot pose `(xRP, yRP, heading)` and laser point `(x_laser, y_laser)`:

```
xw = xRP + (x_laser * cos(heading)) - (y_laser * sin(heading))
yw = yRP + (x_laser * sin(heading)) + (y_laser * cos(heading))
```

### 8.3 Differential Drive Motion Control

- Only **linear.x** (forward speed, m/s) and **angular.z** (yaw rate, rad/s)
- No lateral (Y-axis) motion — differential drive constraint

### 8.4 Pixel ↔ World Coordinate Conversion

**Pixel → World:**
```
wx = origin_x + px * resolution
wy = origin_y + py * resolution
```

**World → Pixel:**
```
px = (wx - origin_x) / resolution
py = (wy - origin_y) / resolution
```

> Map data is stored in **row-major order**. The first pixel is at the **upper-left corner** of the rendered image. For human-friendly display (lower-left origin), apply a vertical flip.

---

## 9. Euler Angle ↔ Quaternion Conversion

For 3D rotation representation:

**Euler → Quaternion:**
```
q.w = cos(roll/2) * cos(pitch/2) * cos(yaw/2) + sin(roll/2) * sin(pitch/2) * sin(yaw/2)
q.x = sin(roll/2) * cos(pitch/2) * cos(yaw/2) - cos(roll/2) * sin(pitch/2) * sin(yaw/2)
q.y = cos(roll/2) * sin(pitch/2) * cos(yaw/2) + sin(roll/2) * cos(pitch/2) * sin(yaw/2)
q.z = cos(roll/2) * cos(pitch/2) * sin(yaw/2) - sin(roll/2) * sin(pitch/2) * cos(yaw/2)
```

**Quaternion → Euler:**
Use `atan2` (not `arctan`) to cover all orientations.
