"""Single storage layer: every read/write of codes and settings goes through Storage."""
import json
import os
from pathlib import Path

DEFAULTS = {
    "active": "lg",
    "profiles": {
        "lg": {
            "power": ["NEC", 0x04, 0x08], "vol_up": ["NEC", 0x04, 0x02],
            "vol_down": ["NEC", 0x04, 0x03], "mute": ["NEC", 0x04, 0x09],
            "ch_up": ["NEC", 0x04, 0x00], "ch_down": ["NEC", 0x04, 0x01],
            "source": ["NEC", 0x04, 0x0B],
        },
        "samsung": {
            "power": ["SAMSUNG", 0x07, 0x02], "vol_up": ["SAMSUNG", 0x07, 0x07],
            "vol_down": ["SAMSUNG", 0x07, 0x0B], "mute": ["SAMSUNG", 0x07, 0x0F],
            "ch_up": ["SAMSUNG", 0x07, 0x12], "ch_down": ["SAMSUNG", 0x07, 0x10],
            "source": ["SAMSUNG", 0x07, 0x01],
        },
        "sony": {
            "power": ["SONY", 0x01, 0x15], "vol_up": ["SONY", 0x01, 0x12],
            "vol_down": ["SONY", 0x01, 0x13], "mute": ["SONY", 0x01, 0x14],
            "ch_up": ["SONY", 0x01, 0x10], "ch_down": ["SONY", 0x01, 0x11],
            "source": ["SONY", 0x01, 0x25],
        },
    },
}


def _home() -> Path:
    return Path(os.environ.get("TVLINK_HOME", Path.home() / ".tvlink"))


class Storage:
    def __init__(self, path=None):
        self.path = Path(path) if path else _home() / "codes.json"
        self.data = self._load()

    def _load(self):
        if self.path.exists():
            return json.loads(self.path.read_text())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = json.loads(json.dumps(DEFAULTS))
        self._save()
        return self.data

    def _save(self):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, indent=2))
        tmp.replace(self.path)

    @property
    def active(self) -> str:
        return self.data["active"]

    def profiles(self):
        return sorted(self.data["profiles"])

    def set_active(self, name: str):
        if name not in self.data["profiles"]:
            raise KeyError(f"no such profile: {name}")
        self.data["active"] = name
        self._save()

    def buttons(self, profile=None):
        return list(self.data["profiles"][profile or self.active])

    def get_code(self, button: str, profile=None):
        prof = self.data["profiles"][profile or self.active]
        if button not in prof:
            raise KeyError(f"unknown button '{button}' in profile '{profile or self.active}'")
        proto, addr, cmd = prof[button]
        return proto, int(addr), int(cmd)

    def put_code(self, button: str, code, profile=None):
        name = profile or self.active
        self.data["profiles"].setdefault(name, {})[button] = [code[0], int(code[1]), int(code[2])]
        self._save()

    def delete_code(self, button: str, profile=None):
        self.data["profiles"][profile or self.active].pop(button, None)
        self._save()
