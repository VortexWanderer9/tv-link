"""Serial link to the Arduino."""
import time


class DeviceError(Exception):
    pass


def find_port():
    from serial.tools import list_ports
    ports = list(list_ports.comports())
    for p in ports:
        text = f"{p.description} {p.manufacturer or ''}".lower()
        if any(k in text for k in ("arduino", "ch340", "ch341", "usb serial", "ftdi", "cp210")):
            return p.device
    return ports[0].device if len(ports) == 1 else None


class Device:
    def __init__(self, port=None, baud=115200, serial_obj=None, boot_delay=2.0):
        self._ser = serial_obj
        self.port, self.baud, self.boot_delay = port, baud, boot_delay

    def connect(self):
        if self._ser is None:
            import serial
            port = self.port or find_port()
            if not port:
                raise DeviceError("No Arduino found. Plug it in or pass --port (see `tvlink ports`).")
            self._ser = serial.Serial(port, self.baud, timeout=1)
            time.sleep(self.boot_delay)  # Arduino resets when the port opens
            self._ser.reset_input_buffer()
        if self._cmd("PING", 3) != "PONG":
            raise DeviceError("Arduino did not answer PING. Is tv_link.ino uploaded?")
        return self

    def close(self):
        if self._ser:
            self._ser.close()
            self._ser = None

    def _cmd(self, text, timeout):
        self._ser.write((text + "\n").encode())
        deadline = time.time() + timeout
        while time.time() < deadline:
            line = self._ser.readline().decode(errors="ignore").strip()
            if line and line != "READY":
                return line
        raise DeviceError(f"Timed out waiting for reply to '{text}'")

    def send(self, code, repeats=0):
        proto, addr, cmd = code
        reply = self._cmd(f"SEND {proto} {addr:#x} {cmd:#x} {repeats}", 3)
        if reply != "OK":
            raise DeviceError(f"Arduino said: {reply}")

    def learn(self, timeout=12):
        reply = self._cmd("LEARN", timeout)
        if reply == "TIMEOUT":
            raise DeviceError("No IR signal received. Point the remote at the receiver and press a button.")
        parts = reply.split()
        if len(parts) != 4 or parts[0] != "CODE":
            raise DeviceError(f"Unexpected reply: {reply}")
        proto = parts[1].upper()
        if proto.startswith("NEC"):
            proto = "NEC"
        if proto not in ("NEC", "SAMSUNG", "LG", "SONY", "RC5"):
            raise DeviceError(f"Protocol '{proto}' is not supported for replay.")
        return proto, int(parts[2], 16), int(parts[3], 16)
