# TV Link

Control a television from your laptop using an Arduino-powered infrared blaster.

```text
Laptop --USB serial--> Arduino --IR LED--> TV
```

The laptop sends button commands over USB. The Arduino converts them to infrared
signals for the TV. The Arduino needs a USB connection to the laptop; the TV does
not communicate with the Arduino.

## Features

- Send common remote-control buttons from the command line or an interactive prompt.
- Learn infrared codes from a physical remote (with an optional receiver module).
- Switch between TV profiles and save learned codes locally.
- Use a small browser-based remote.
- Run the Python tests without an Arduino attached.

Supported replay protocols: NEC, Samsung, LG, Sony SIRC (12-bit), and RC5.
Starter codes are examples and may need to be learned from your own remote.

## Hardware

- Arduino Uno or Nano
- 940 nm infrared LED
- 100 Ω resistor and 2N2222 (or similar NPN) transistor, plus a 1 kΩ resistor
  for the recommended higher-range transmitter
- Optional IR receiver module for learning, such as VS1838B or TSOP38238

### Transmitter wiring

Recommended transistor driver:

```text
D3 --[1 kΩ]--> transistor BASE
transistor EMITTER --> GND
transistor COLLECTOR --> IR LED cathode (-)
IR LED anode (+) --[100 Ω]--> 5V
```

For a short-range test, connect D3 through a 220 Ω resistor to the LED anode and
connect the cathode to GND. Optional receiver wiring: OUT to D11, VCC to 5V, and
GND to GND.

Point the IR LED at the TV's infrared window, usually near the bottom center of
the bezel.

## Installation

1. In the Arduino IDE Library Manager, install **IRremote 4.x**.
2. Open `firmware/tv_link/tv_link.ino`, select your board and port, then upload.
3. Install TV Link on your laptop (Python 3.9 or later):

   ```sh
   python3 -m pip install .
   ```

For development, use `python3 -m pip install -e .` instead.

## Usage

List profiles and buttons, then select your TV profile and send a command:

```sh
tvlink list
tvlink profile samsung
tvlink send power
tvlink send vol_up --repeat 5
tvlink repl
tvlink serve
```

The web remote is available at <http://127.0.0.1:8765>. To use a specific serial
port, pass `--port` before the subcommand, for example:

```sh
tvlink --port /dev/ttyUSB0 send power
tvlink --port COM3 ports
```

Port auto-detection is used by default. `tvlink ports` lists available serial
ports.

### Learn codes from your remote

Learning requires the optional IR receiver wired to D11:

```sh
tvlink learn power --profile mytv
tvlink learn vol_up --profile mytv
tvlink profile mytv
```

Codes are saved in `~/.tvlink/codes.json`. Set the `TVLINK_HOME` environment
variable to use a different directory.

## Development

Run the test suite with Python's standard library test runner:

```sh
python3 -m unittest discover -s tests
```

The tests use a simulated Arduino and do not require connected hardware.

## Troubleshooting

- **No Arduino found:** Check the USB connection, confirm the serial port, or
  pass it explicitly with `--port`.
- **Arduino does not answer PING:** Re-upload the sketch and check that the
  selected board and serial port are correct.
- **The TV does not respond to a starter code:** Select the right profile or
  learn codes from the TV's original remote.
- **Short range:** Use the transistor-driver circuit instead of driving the IR
  LED directly from D3.

The web server binds to `127.0.0.1` by default. If you choose another host,
remember that the remote has no authentication; only expose it on a network you
trust.

## License

TV Link is distributed under the MIT License. See [LICENSE](LICENSE).
