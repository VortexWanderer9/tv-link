# TV Link — control your TV from your laptop with an Arduino

Laptop ──USB──> Arduino ──IR LED──> TV

The Arduino acts as an infrared remote. Your laptop sends it button names over USB;
the Arduino fires the matching IR code at the TV. The USB cable goes to the **laptop**
(the TV can only power the board, it can't send it commands).

## Parts
- Arduino Uno or Nano
- IR LED (940 nm) + 100 Ω resistor + 2N2222 (or similar NPN) transistor + 1 kΩ resistor  *(for good range)*
- *(optional, for Learn mode)* IR receiver module, e.g. VS1838B / TSOP38238

## Wiring
Sender (transistor driver, ~5 m range):
```
D3 ──[1kΩ]── transistor BASE
transistor EMITTER ── GND
transistor COLLECTOR ── IR LED cathode(-)
IR LED anode(+) ──[100Ω]── 5V
```
Quick test version (short range): D3 ──[220Ω]── LED anode, LED cathode ── GND.

Receiver (optional): OUT → D11, VCC → 5V, GND → GND.

Point the IR LED at the TV's IR window (usually bottom center of the bezel).

## Setup
1. Arduino IDE → Library Manager → install **IRremote** (4.x).
2. Open `firmware/tv_link/tv_link.ino`, select your board/port, Upload.
3. On the laptop: `pip install -r requirements.txt`

## Use
```
python -m tvlink list                  # profiles: lg, samsung, sony (starter codes)
python -m tvlink profile samsung       # pick your TV brand
python -m tvlink send power
python -m tvlink send vol_up -r 5
python -m tvlink repl                  # type button names
python -m tvlink serve                 # web remote at http://127.0.0.1:8765
```
Add `--port COM3` (Windows) or `--port /dev/ttyUSB0` (Linux) if auto-detect fails. `python -m tvlink ports` lists ports.

### Starter codes don't work? Learn them from your real remote
Needs the IR receiver wired up:
```
python -m tvlink learn power --profile mytv
python -m tvlink learn vol_up --profile mytv
python -m tvlink profile mytv
```
Codes are stored in `~/.tvlink/codes.json` (override with the `TVLINK_HOME` env var).

## Tests
`python -m unittest discover -s tests` (uses a simulated Arduino, no hardware needed)

## Notes
- Supported protocols: NEC, Samsung, LG, Sony (SIRC 12-bit), RC5.
- If your TV has HDMI-CEC you could instead drive the HDMI CEC line directly (different wiring) — not covered here.
