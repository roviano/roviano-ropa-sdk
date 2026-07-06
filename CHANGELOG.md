# Changelog

All notable changes to the ROPA SDK documentation and examples will be documented here.

## v0.1.0 — 2026-07-06

### Added
- Complete ROPA protocol reference (`docs/protocol.md`) from official 72-page specification
- 4-model hardware specification table (`docs/models.md`) with verified parameters
- Android DeploymentTool field guide (`docs/android-deployment.md`) from official 23-page deployment manual
- Python examples: `connect.py`, `subscribe_pose.py`, `call_mapping.py`, `move_command.py`
- JavaScript examples: `connect.js`, `subscribe.js`
- Quick Start code in README using real ROPA topics (`/robot_pose`, `geometry_msgs/Pose2D`)
- Developer Kit and Integrator Package descriptions
- MIT license

### Verified
- iMRP500 positioning accuracy: ±5 cm (confirmed from official spec sheet)
- iMRP500 navigation accuracy: ±5 cm
- iMRP500 sensors: TOF LiDAR 40m × 1, RGBD × 2 (optional), ultrasonic × 1, X86 PC, IMU 6-axis
- iMRP500 physical speed: 1.5 m/s, navigation speed: 0.8 m/s
- iMRP500 drive: differential (2×6.5" servo hub + 4×universal + 1×directional)
- All ROPA topic names, service names, and status codes sourced from official protocol PDF
