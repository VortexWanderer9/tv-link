import argparse
import sys

from .device import Device, DeviceError
from .storage import Storage


def main(argv=None):
    ap = argparse.ArgumentParser(prog="tvlink", description="Control a TV through an Arduino IR blaster.")
    ap.add_argument("--port", help="serial port, e.g. COM3 or /dev/ttyUSB0 (auto-detected by default)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ports", help="list serial ports")
    sub.add_parser("list", help="list profiles and buttons")
    p = sub.add_parser("profile", help="switch active profile"); p.add_argument("name")
    p = sub.add_parser("send", help="send a button"); p.add_argument("button"); p.add_argument("-r", "--repeat", type=int, default=1)
    p = sub.add_parser("learn", help="learn a button from your real remote"); p.add_argument("button")
    p.add_argument("--profile", help="save into this profile (created if new)")
    sub.add_parser("repl", help="type button names interactively")
    p = sub.add_parser("serve", help="start the web remote"); p.add_argument("--host", default="127.0.0.1"); p.add_argument("--web-port", type=int, default=8765)
    a = ap.parse_args(argv)

    store = Storage()
    try:
        if a.cmd == "ports":
            from serial.tools import list_ports
            for x in list_ports.comports():
                print(f"{x.device}\t{x.description}")
        elif a.cmd == "list":
            for name in store.profiles():
                print(f"{'*' if name == store.active else ' '} {name}: {', '.join(store.buttons(name))}")
        elif a.cmd == "profile":
            store.set_active(a.name); print(f"active profile: {a.name}")
        elif a.cmd == "send":
            code = store.get_code(a.button)
            dev = Device(a.port).connect()
            for _ in range(max(1, a.repeat)):
                dev.send(code)
            print(f"sent {a.button} {code}")
        elif a.cmd == "learn":
            dev = Device(a.port).connect()
            print(f"Point your remote at the IR receiver and press the button for '{a.button}'...")
            code = dev.learn()
            store.put_code(a.button, code, a.profile)
            print(f"saved {a.button} = {code} in profile '{a.profile or store.active}'")
        elif a.cmd == "repl":
            dev = Device(a.port).connect()
            print(f"profile '{store.active}' - buttons: {', '.join(store.buttons())}  (q to quit)")
            for line in sys.stdin:
                b = line.strip()
                if b in ("q", "quit", "exit"):
                    break
                if not b:
                    continue
                try:
                    dev.send(store.get_code(b)); print("ok")
                except (KeyError, DeviceError) as e:
                    print(f"error: {e}")
        elif a.cmd == "serve":
            from .web import make_server
            dev = Device(a.port).connect()
            srv = make_server(store, dev, a.host, a.web_port)
            print(f"Web remote: http://{a.host}:{a.web_port}  (Ctrl+C to stop)")
            try:
                srv.serve_forever()
            except KeyboardInterrupt:
                pass
    except (DeviceError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
