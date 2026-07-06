# DeploymentTool Android App — Field Guide

> Source: *Roviano iMRP Deployment Manual* (23-page official document)
> Applies to: iMRP400 / iMRP500 / iMRP600 / iMRP800
> Required: DeploymentTool APK (provided with Developer Kit or Integrator Package)
> Algorithm version ≥ V4.5.0 required for speed/travel/elevator/sensor features

---

## 1. Connecting to the Robot

### WiFi Connection

The robot broadcasts a dedicated access point after boot.

| Setting | Value |
|---------|-------|
| SSID | `TY1251D-xxxxx` or `TY1251C003-xxxx` (xxxxx = serial suffix) |
| Password | `123456789` |
| Robot IP (WiFi) | `10.42.0.1` or `192.168.20.22` |

Steps:
1. Power on the robot (long-press power button until indicator glows)
2. On your Android phone, connect to the robot's WiFi SSID
3. Open DeploymentTool — it auto-detects the robot at the default IP
4. ROPA WebSocket is available at `ws://<ROBOT_IP>:9090`

### Wired Connection (Ethernet)

| Setting | Value |
|---------|-------|
| Gateway | `192.168.20.1` |
| Robot IP | `192.168.20.22` |
| Subnet | `255.255.255.0` |

Steps:
1. Connect Ethernet cable from robot to your laptop/router
2. Configure your network interface: IP `192.168.20.x` (x ≠ 1, 22), gateway `192.168.20.1`
3. Open DeploymentTool, enter robot IP `192.168.20.22`

---

## 2. Mapping Your Workspace

The robot must build a map before it can navigate. DeploymentTool offers three mapping modes:

| Mode | Recommended Area | Behavior |
|------|-----------------|----------|
| **Standard** | 1,000 – 2,000 m² | Balanced speed and detail |
| **Similar** | 2,000 – 3,000 m² | Uses template from previous map for faster coverage |
| **Large Scene** | 3,000 – 10,000 m² | Optimized for wide-area coverage |

Steps:
1. In DeploymentTool, tap **New Map** → select mapping mode
2. Manually push the robot through the area you want mapped (or use remote teleop via ROPA `/cmd_vel_mux/input/teleop`)
3. The robot scans continuously — LiDAR + RGBD + ultrasonic data feed into the map
4. When coverage is complete, tap **Save Map**
5. The map is stored on the robot and accessible via ROPA `/get_map_info` service call

> **Tip:** For large facilities, map each floor separately and link them via cross-floor navigation (see §5).

---

## 3. Point Management (POI)

### Adding Points of Interest

1. Position the robot at the desired location
2. In DeploymentTool, tap **Add Point** → name the POI (e.g., "Charging Station", "Delivery Point A")
3. The point is saved with the robot's current coordinates in the active map

### Navigation to a Point

- **Single-point navigation**: Select a POI → tap **Go** → robot navigates autonomously
- **Multi-point navigation**: Select multiple POIs → choose mode:
  - **Single pass** — visit each point once, stop at the last
  - **Round-trip** — visit each point, return to start
  - **Cycle** — visit each point in loop indefinitely

All navigation commands are also available via ROPA service calls (`/poi`, `/navi_status` topic for monitoring).

---

## 4. Map Editing

After saving a map, edit it in DeploymentTool to add safety constraints:

### Virtual Walls

Draw lines on the map that the robot will never cross. Use to:
- Block doorways the robot should not enter
- Separate zones (e.g., kitchen vs. dining area)
- Protect fragile areas

### Area Annotations

| Area Type | Color | Behavior |
|-----------|-------|----------|
| **Obstacle area** | Red | Robot treats as impassable (permanent virtual wall equivalent) |
| **Blank area** | White | Clears previously mapped obstacles (use when furniture moved) |
| **Unknown area** | Gray | Robot treats as unexplored (will not plan paths through) |

### Work Areas (Special Zones)

| Zone Type | Purpose |
|-----------|---------|
| **Strong light zone** | Robot adjusts sensor parameters for bright areas (near windows, skylights) |
| **Deceleration zone** | Robot slows down (near doorways, intersections, pedestrian areas) |
| **Dangerous zone** | Robot enters with maximum caution (near stairs, loading docks) |

---

## 5. Cross-Floor Navigation (iMRP600 Only)

The iMRP600 supports autonomous elevator riding. To set up multi-floor navigation:

1. Map each floor separately (see §2)
2. Link floors by defining elevator connection points on each floor map
3. In DeploymentTool, configure elevator parameters (see §11)
4. When sending a navigation command to a POI on another floor, the robot:
   - Navigates to the elevator
   - Calls the elevator via configured protocol
   - Enters, rides, exits on target floor
   - Navigates to the destination POI

> Cross-floor navigation requires algorithm version ≥ V4.5.0 and elevator hardware integration.

---

## 6. Self-Localization

The robot can localize itself on a saved map using two methods:

| Method | When to use | How it works |
|--------|-------------|--------------|
| **Global localization** | Robot position unknown (e.g., after manual relocation) | Robot scans environment and matches against entire map |
| **Regional localization** | Robot position approximately known | Faster: narrows search to nearby region |

Monitor localization confidence via ROPA topic `/localization_confidence`.

---

## 7. Calibration

### Point-Based Calibration

1. Place robot at a known reference point on the map
2. In DeploymentTool, tap **Calibrate** → select the reference POI
3. Robot adjusts its internal position estimate to match

### Manual Calibration

For fine-tuning when the robot drifts over time:
1. Tap **Manual Calibration**
2. Adjust X/Y offset and heading angle
3. Confirm — robot updates its pose estimate

---

## 8. Settings

Access via DeploymentTool → **Settings** (requires algorithm ≥ V4.5.0).

### Speed Modes

| Mode | Max Navigation Speed | Use Case |
|------|---------------------|----------|
| **Low** | 0.3 m/s | Crowded areas, narrow corridors |
| **Medium** | 0.5 m/s | General indoor navigation |
| **High** | 0.8 m/s | Open warehouse, long corridors |

Speed can also be changed via ROPA `/velocity_control` service call (9 modes including safe/balanced/efficient).

### Travel Modes

| Mode | Obstacle Avoidance Aggressiveness | Behavior |
|------|-----------------------------------|----------|
| **Safe** | High | Slow, frequent re-planning. Avoids all detected obstacles with wide margin |
| **Balanced** | Medium | Default. Plans efficient paths while maintaining safety margin |
| **Efficient** | Low | Fast, minimal re-planning. Narrower obstacle margin for speed |

### Sensor Configuration

Toggle individual sensors on/off:
- LiDAR (always recommended ON)
- RGBD cameras (optional — enable for 3D obstacle detection)
- Ultrasonic (optional — enable for transparent-object detection)

### Safety Thresholds

Adjust detection sensitivity:
- Obstacle distance threshold (how close before robot reacts)
- Deceleration distance (how far before robot slows)
- Emergency stop distance (how close before hard stop)

---

## 9. Charging Pile Setup

Each map supports **one charging pile**.

| Parameter | Requirement |
|-----------|------------|
| Location | Wall-mounted, accessible to robot |
| Clearance | ≥ 1.5 m open space around dock |
| Infrared | Auto-dock beacon must face robot approach path |

Steps:
1. Install charging pile at designated location
2. In DeploymentTool, add the pile as a POI on the map
3. Robot auto-docks when battery drops below threshold
4. Monitor charging status via ROPA topic `/robot_status` → `battery_status` field

---

## 10. Emergency Stop

| Type | Trigger | Behavior |
|------|---------|----------|
| **Hardware E-stop** | Physical button on robot chassis | Immediate motor cutoff. Robot can be pushed manually |
| **Software E-stop** | DeploymentTool button or ROPA `/soft_stop` publish | Immediate stop command. Robot remains stationary (cannot be pushed) |

> Always use **hardware E-stop** for physical emergencies (person in path, tip-over risk).
> Use **software E-stop** for navigation pauses (route needs adjustment, temporary hold).

---

## 11. Elevator Configuration (iMRP600)

Requires algorithm ≥ V4.5.0 and compatible elevator controller.

| Parameter | Description |
|-----------|------------|
| Elevator ID | Unique identifier for each elevator in the building |
| Floor mapping | Map each elevator floor number to the robot's floor maps |
| Door wait time | How long the robot waits for elevator doors to open |
| Communication protocol | Serial/CAN/TCP interface to elevator controller |

Configure via DeploymentTool → **Settings** → **Elevator** or via ROPA service calls.

---

## 12. Version Update

1. DeploymentTool checks for algorithm updates when connected
2. Tap **Update** → download and install new firmware
3. Robot restarts automatically after update
4. Verify version via ROPA `/robot_info` service call → `algorithm_version` field

---

## 13. Fault Diagnosis

Common issues and troubleshooting:

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Robot won't connect | WiFi SSID not visible | Reboot robot; check WiFi on phone |
| Map quality poor | Insufficient LiDAR coverage | Re-map with slower, more thorough path |
| Localization drift | Accumulated odometry error | Run global localization or point calibration |
| Navigation fails | Map obstacle areas changed | Re-map or edit map (add/remove obstacles) |
| Battery drains fast | High speed mode + heavy payload | Switch to balanced/low speed; reduce payload |
| Emergency stop triggered | Sensor threshold too sensitive | Adjust safety threshold in Settings |
| Charging pile not found | IR beacon misaligned | Reinstall pile; ensure 1.5 m clearance; check beacon direction |

---

## 14. Power On / Off

| Action | Method |
|--------|--------|
| **Power on** | Long-press power button (≈3s) until indicator glows solid |
| **Power off** | Long-press power button (≈3s) until indicator fades; wait for shutdown |
| **Force off** | If software shutdown hangs, hold power button 10s for hard cutoff |

> Always allow the robot to complete software shutdown before transporting. Hard cutoff may corrupt map data.

---

## ROPA Integration

All DeploymentTool functions have equivalent ROPA API calls:

| DeploymentTool Feature | ROPA Equivalent |
|------------------------|-----------------|
| New map (mapping mode) | `call_service /node_manager_control` + `/layered_map_cmd` |
| Save map | `call_service /get_map_info` |
| Add POI | `call_service /poi` (op: add) |
| Navigate to POI | `call_service /poi` (op: navigate) |
| Virtual walls | Map editing via `call_service /layered_map_cmd` |
| Speed mode | `call_service /velocity_control` |
| Software E-stop | `publish /soft_stop` |
| Robot pose | `subscribe /robot_pose` |
| Robot status | `subscribe /robot_status` |
| Localization confidence | `subscribe /localization_confidence` |
| Navigation status | `subscribe /navi_status` |
| Robot info (version) | `call_service /robot_info` |

See [Protocol Reference](protocol.md) for complete API documentation.

---

## Contact

- **Engineering support**: engineering@roviano.com
- **Integrator Package (on-site deployment)**: [Roviano on Alibaba.com](https://roviano.en.alibaba.com)
