# continue.md — handoff
Project: TV Link (Arduino IR blaster controlled from laptop)

## State
- DONE: firmware (SEND/LEARN/PING over serial), Python package `tvlink` (storage, device, cli, web remote), 5 passing tests (simulated Arduino), README with wiring.
- NOT verified on real hardware or compiled with arduino-cli (no toolchain in the build sandbox). First thing to do after upload: compile, then `python -m tvlink send power`.

## Architecture
- `firmware/tv_link/tv_link.ino` — line protocol, 115200 baud.
- `tvlink/storage.py` — the only place that touches codes.json.
- `tvlink/device.py` — serial transport + protocol.
- `tvlink/cli.py`, `tvlink/web.py` — front ends; they only use Storage + Device.

## Likely next steps (one at a time)
1. Fix any IRremote API mismatch if the sketch fails to compile (written against 4.x).
2. Verify starter codes for the user's TV brand; use `learn` if wrong.
3. Optional: number keys / arrows / home / back buttons; keyboard shortcuts in web UI.
4. Optional: raw-signal learn for unsupported protocols.
