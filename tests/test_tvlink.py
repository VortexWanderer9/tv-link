import json, os, sys, tempfile, threading, unittest, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tvlink.device import Device, DeviceError
from tvlink.storage import Storage
from tvlink.web import make_server


class FakeSerial:
    """Behaves like tv_link.ino."""
    def __init__(self): self.out, self.sent, self.silent = [], [], False
    def write(self, b):
        if self.silent: return
        line = b.decode().strip()
        if line == "PING": self.out.append(b"PONG\n")
        elif line.startswith("SEND"): self.sent.append(line); self.out.append(b"OK\n")
        elif line == "LEARN": self.out.append(b"CODE NEC 0x4 0x8\n")
    def readline(self): return self.out.pop(0) if self.out else b""
    def close(self): pass


class T(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.s = Storage(os.path.join(self.d, "codes.json"))
        self.f = FakeSerial()
        self.dev = Device(serial_obj=self.f).connect()

    def test_send(self):
        self.dev.send(self.s.get_code("power"))
        self.assertEqual(self.f.sent, ["SEND NEC 0x4 0x8 0"])

    def test_learn_persists(self):
        code = self.dev.learn(); self.s.put_code("custom", code, "mytv")
        self.assertEqual(Storage(self.s.path).get_code("custom", "mytv"), ("NEC", 4, 8))

    def test_unknown_button(self):
        with self.assertRaises(KeyError): self.s.get_code("nope")

    def test_timeout(self):
        self.f.silent = True
        with self.assertRaises(DeviceError): self.dev._cmd("LEARN", 0.2)

    def test_web(self):
        srv = make_server(self.s, self.dev, port=0)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{srv.server_address[1]}"
        st = json.load(urllib.request.urlopen(base + "/api/state"))
        self.assertIn("power", st["buttons"])
        r = urllib.request.urlopen(urllib.request.Request(base + "/api/send", b'{"button":"vol_up"}', method="POST"))
        self.assertEqual(r.status, 200); self.assertEqual(self.f.sent[-1], "SEND NEC 0x4 0x2 0")
        srv.shutdown()

if __name__ == "__main__": unittest.main()
