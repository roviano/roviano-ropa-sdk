# iMRP Series Hardware Specifications

> All parameters below are sourced from official product specification sheets.
> Unconfirmed values are marked **"Contact us for specs"** — we prioritize honesty over guesswork.

All four models share the **same ROPA protocol** (WebSocket port 9090, JSON format). One SDK works across the entire series.

---

## Quick Comparison

| | iMRP400 | iMRP500 | iMRP600 | iMRP800 |
|---|---------|---------|---------|---------|
| **Tagline** | Compact Builder's Base | The Builder's Chassis | Heavy-Duty Elevator Chassis | Fast Wide-Base Chassis |
| **Payload** | 20 kg | 50 kg | 100 kg | 100 kg |
| **Max Speed** | 0.5 m/s | 0.8 m/s | 0.8 m/s | 1.2 m/s |
| **Positioning Accuracy** | ±10 cm | ±5 cm | ±10 cm | ±10 cm |
| **Mapping Area** | 10,000 m² | 10,000 m² | 30,000 m² | 10,000 m² |
| **Endurance (light load)** | 12 h | 12 h | 12 h | 10 h |
| **Endurance (full load)** | Contact us for specs | Contact us for specs | Contact us for specs | 3.5 h |
| **Dimensions** | 450×430×255 mm | D500×H310 mm | 600×450×260 mm | 800×550×260 mm |
| **Weight (chassis only)** | 20 kg | 35 kg | 45 kg | 50 kg |
| **Signature Feature** | RGBD 3D Vision · Ultra-Compact | Differential Drive · Warehouse-Ready | Autonomous Elevator Riding · Dual-LiDAR | 1.2 m/s Fast Transit · 800 mm Wide |
| **Target Scenario** | Education / Indoor Service / Small Spaces | Warehouse / Service / Light Logistics | Multi-Floor / Heavy Payload | Factory / Cleanroom / Rapid Transit |

---

## iMRP400 — Compact Builder's Base

The smallest chassis in the series. RGBD 3D vision makes it ideal for tight indoor spaces where depth perception matters.

| Parameter | Value |
|-----------|-------|
| Payload capacity | 20 kg |
| Dimensions | 450 × 430 × 255 mm |
| Weight (chassis) | 20 kg |
| Max speed | 0.5 m/s |
| Positioning accuracy | ±10 cm |
| Mapping area | 10,000 m² |
| Endurance (light load) | 12 h |
| Primary sensor | RGBD 3D Vision |
| LiDAR | Contact us for specs |
| Battery | 29.4V / 20AH |
| Autonomous elevator | Not supported |
| ROPA protocol | Full support (same as all iMRP models) |

**Best for:** Education labs, indoor service robots, greeting/delivery in small spaces.

---

## iMRP500 — The Builder's Chassis

The core model. 50 kg payload, differential drive, 12-hour endurance. The Developer Kit ($2,699 FOB) and Integrator Package ($2,899 FOB) are built around this chassis.

| Parameter | Value |
|-----------|-------|
| Payload capacity | 50 kg |
| Dimensions | D500 × H310 mm |
| Weight (chassis) | 35 kg |
| Max speed | 0.8 m/s |
| Positioning accuracy | ±5 cm |
| Navigation accuracy | ±5 cm |
| Mapping area | 10,000 m² |
| Endurance (light load) | 12 h |
| Primary sensor | TOF LiDAR (40 m range × 1) + RGBD × 2 (optional) + Ultrasonic × 1 |
| LiDAR | TOF 40 m × 1 |
| RGBD cameras | × 2 (optional) |
| Ultrasonic sensor | × 1 |
| Compute unit | X86 PC × 1 |
| IMU | 6-axis × 1 |
| Drive type | Differential: 2×6.5″ servo hub + 4×universal + 1×directional |
| Battery | 24V / 20AH |
| Max speed | 1.5 m/s (physical), 0.8 m/s (navigation) |
| Obstacle clearance | 10 mm |
| Slope capability | 5° |
| Trench crossing | 40 mm |
| Turning radius | 0 mm (differential drive, zero-radius turn) |
| Max rotation speed | 60°/s |
| Autonomous elevator | Not supported |
| ROPA protocol | Full support (same as all iMRP models) |

**Pricing:**

| Package | FOB Price | Includes |
|---------|-----------|----------|
| Developer Kit | $2,699 | Chassis + ROPA SDK + full docs + 1-on-1 engineer support |
| Integrator Package | $2,899 | Developer Kit + on-site deployment + priority support |

**Best for:** Warehouse material handling, indoor service, light logistics, general AMR applications.

---

## iMRP600 — Heavy-Duty Elevator Chassis

The only model with autonomous elevator riding capability. 100 kg payload, dual-LiDAR, 30,000 m² mapping — designed for multi-floor building logistics.

| Parameter | Value |
|-----------|-------|
| Payload capacity | 100 kg (rated), 50 kg (recommended) |
| Dimensions | 600 × 450 × 260 mm |
| Weight (chassis) | 45 kg |
| Max speed | 0.8 m/s |
| Positioning accuracy | ±10 cm |
| Mapping area | 30,000 m² |
| Endurance (light load) | 12 h |
| LiDAR | TOF 40 m × 2 (Dual-LiDAR) |
| RGBD sensor | × 1 |
| IMU | × 1 |
| Battery | 24V / 20AH (optional 30AH / 45AH) |
| Autonomous elevator riding | ✅ Supported (exclusive to iMRP600) |
| ROPA protocol | Full support (same as all iMRP models) |

**Elevator riding** is an iMRP600-exclusive capability. Through ROPA service calls, the chassis autonomously calls elevators, enters, exits, and navigates across floors — no manual intervention required.

**Best for:** Multi-floor hospital/hotel delivery, high-rise warehouse logistics, heavy payload transport across floors.

---

## iMRP800 — Fast Wide-Base Chassis

1.2 m/s max speed and 800 mm wide base. Designed for factory floors and cleanrooms where rapid transit and stability under load matter.

| Parameter | Value |
|-----------|-------|
| Payload capacity | 100 kg (rated), 50 kg (recommended) |
| Dimensions | 800 × 550 × 260 mm |
| Weight (chassis) | 50 kg |
| Max speed | 1.2 m/s |
| Positioning accuracy | ±10 cm |
| Mapping area | 10,000 m² |
| Endurance (light load) | 10 h |
| Endurance (full load) | 3.5 h |
| LiDAR | TOF 40 m × 2 |
| Battery | 29.4V / 20AH |
| Autonomous elevator | Not supported (iMRP600 exclusive) |
| ROPA protocol | Full support (same as all iMRP models) |

**Best for:** Factory material handling, cleanroom logistics, rapid point-to-point transit in wide corridors.

---

## ROPA Protocol Coverage

All four models expose the same ROPA WebSocket+JSON interface on port 9090:

- **10+ subscribe topics** — `/robot_pose`, `/laser_data`, `/robot_status`, `/navi_status`, `/map`, `/global_path`, `/obstacle_region`, `/localization_confidence`, `/notification`, `/mobile_base/sensors/core`
- **8 publish topics** — `/cmd_vel_mux/input/teleop`, `/move_base/cancel`, `/soft_stop`, `/insert_current_pose_marker`, `/get_current_map`, `/node_manager/laser_safety_controller`, `/node_manager/laser_safety_range`, `/laser_safety_controller/setting_confidence_threshold`
- **12 service calls** — `/node_manager_control`, `/velocity_control`, `/self_diagnosis`, `/robot_info`, `/poi`, `/get_map_info`, `/layered_map_cmd`, `/marker_operation/get_markers`, `/marker_manager/delete_poi`, `/building_operation/delete`, `/get_match_threshold`, `/calculate_distance`

> Full protocol reference: [`docs/protocol.md`](protocol.md)

---

## Compliance Notes

| What we certify | What we do NOT certify |
|-----------------|----------------------|
| Battery: UN38.3 + MSDS compliant | Full machine CE / FCC (not yet obtained) |
| ROPA protocol: fully documented, no NDA | ROS2 Native support (ROPA is a separate WebSocket protocol) |

**For CE/FCC certification timelines, contact us directly.**

---

## Get the Hardware

👉 [Roviano on Alibaba.com](https://roviano.en.alibaba.com) — iMRP400 / 500 / 600 / 800

**Contact:** engineering@roviano.com
 iMRP400 / 500 / 600 / 800

**Contact:** engineering@roviano.com
