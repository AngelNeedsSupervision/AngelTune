import os
import re
import json
import random
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog

APP_NAME = "AngelTune"
APP_VERSION = "2.4"

HUD_STYLES = {
    "Default": "NewEnumerator0",
    "TU Alpha": "NewEnumerator5",
    "Minimalistic": "NewEnumerator6",
    "Cute": "NewEnumerator7",
    "Cursive": "NewEnumerator8",
}
HUD_STYLES_REV = {v: k for k, v in HUD_STYLES.items()}

DEFAULT_PATH = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Tower"
    / "Saved"
    / "Config"
    / "WindowsNoEditor"
    / "Game.ini"
)

DEFAULT_USER_SETTINGS_PATH = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Tower"
    / "Saved"
    / "Config"
    / "WindowsNoEditor"
    / "GameUserSettings.ini"
)

DISPLAY_MODE_LABELS = {
    "Fullscreen": "0",
    "Borderless Windowed": "1",
    "Windowed": "2",
}
DISPLAY_MODE_VALUES = {v: k for k, v in DISPLAY_MODE_LABELS.items()}

COMMON_RESOLUTIONS = [
    "1280 x 720",
    "1600 x 900",
    "1920 x 1080",
    "2560 x 1080",
    "2560 x 1440",
    "3440 x 1440",
    "3840 x 2160",
]

APP_SETTINGS_DIR = (
    Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "AngelTune"
)
APP_SETTINGS_FILE = APP_SETTINGS_DIR / "settings.json"

BUILTIN_COLOR_PRESETS = {
    "Angel Pink": "#F07BA7",
    "Soft Pink": "#F2A1BE",
    "Deep Berry": "#9D4268",
    "Lavender": "#C7A7FF",
    "Purple": "#A56BFF",
    "White": "#FFFFFF",
    "Black": "#000000",
}


def load_app_settings():
    try:
        if APP_SETTINGS_FILE.exists():
            data = json.loads(APP_SETTINGS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def save_app_settings(data):
    try:
        APP_SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        APP_SETTINGS_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return True
    except Exception:
        return False


# Player-emote display names documented in the Tower Unite emote menu /
# official update notes. The exact Game.ini shortcut token is not publicly
# documented for every display name, so the editor deliberately keeps UI
# names separate from verified shortcut IDs.
EMOTE_DISPLAY_NAMES = {
    "Dances": [
        "Chill Dance",
        "The Wave",
        "Squat Kick",
        "Spooky Dance",
        "Dab Loop",
        "Frog",
        "Lighter Sway",
        "Rough Convict",
        "Vibin'",
    ],
    "General": [
        "Cheer",
        "Disappointed",
        "Pointing",
        "Shrug",
        "Waiting",
        "Agree",
        "Disagree",
        "Dab",
        "Facepalm",
        "Worship",
        "Wave (far)",
        "Wave (near)",
        "Peace",
        "Clap",
    ],
    "Special": [
        "Fireball",
        "Golf Drive",
        "Anonymous",
        "T Pose",
        "Face Splat",
    ],
    "Poses": [
        "Sleep",
        "Sit",
        "Lay Back",
        "Thinker",
    ],
}

# These exact tokens are verified from the user's Game.ini.
VERIFIED_EMOTE_SHORTCUT_IDS = ["layback", "Sit", "sleep", "anonymous"]

COLOR_KEYS = {
    "Inventory color": "Inventory.Color",
    "Key prompt color": "HUD.KeyPrompt.Color",
    "Friend name color": "HUD.PlayerNames.FriendColor",
    "Name outline color": "HUD.PlayerNames.OutlineColor",
}

FLOAT_KEYS = {
    "Graphics.UIScale",
    "Graphics.FOV",
    "Graphics.Gamma",
    "Camera.ViewBob",
    "Graphics.MirrorResolution",
    "Lobby.PlayerFadeAmount",
    "Nightclub.Brightness",
    "Gameplay.MouseSensitivity",
    "Gamepad.Sensitivity",
}

INT_KEYS = {
    "Graphics.ResolutionScale",
    "Chat.Width",
    "Graphics.MediaResolution",
    "Graphics.HighQualityShaders",
    "Graphics.HighQualityShaders2",
    "Graphics.OceanQuality",
    "Settings.AAMode",
    "Graphics.IconScale",
    "Graphics.WaterSimulation",
    "Workshop.CacheLimit",
    "Canvas.DiskCacheLimit",
    "Canvas.SafetyLevel",
    "Condo.MaxBackups",
    "Libretro.ResolutionScale",
}

VOLUME_KEYS = [
    ("Master volume", "Volume.MasterVolume"),
    ("Music volume", "Volume.MusicVolume"),
    ("Effects volume", "Volume.EffectVolume"),
    ("Instrument volume", "Volume.InstrumentVolume"),
    ("Voice volume", "Volume.VoiceVolume"),
    ("Media volume", "Volume.MediaVolume"),
    ("Noise Maker volume", "Volume.NoiseMakerVolume"),
    ("Plaza music volume", "Volume.PlazaMusicVolume"),
    ("Sound Emitter volume", "Volume.SoundEmitterVolume"),
    ("Workshop sound volume", "Volume.WorkshopSoundVolume"),
    ("Musical items volume", "Volume.MusicalItemsVolume"),
    ("Achievement unlock volume", "Volume.AchievementUnlockVolume"),
    ("Weapon volume", "Volume.WeaponVolume"),
    ("Voice-over volume", "Volume.VOVolume"),
    ("Tower Media volume", "MediaVolume"),
]

ITEM_COLOR_KEYS = {
    "Text Hat color": "Item.TextHatColor",
    "Vehicle color": "Item.VehicleColor",
    "RC vehicle color": "Item.RCColor",
    "Generic item color": "Item.Generic",
    "Libretro portable color 1": "Item.LibretroPortableColor",
    "Libretro portable color 2": "Item.LibretroPortableColor2",
    "Libretro portable color 3": "Item.LibretroPortableColor3",
    "Libretro portable color 4": "Item.LibretroPortableColor4",
    "Libretro portable color 5": "Item.LibretroPortableColor5",
}


TEXT_HAT_SYMBOLS = [
    ("♡  Heart outline", "♡"),
    ("♥  Heart", "♥"),
    ("❤  Heavy heart", "❤"),
    ("❥  Rotated heart", "❥"),
    ("ღ  Curly heart", "ღ"),
    ("★  Star", "★"),
    ("☆  Star outline", "☆"),
    ("✦  Sparkle", "✦"),
    ("✧  Sparkle outline", "✧"),
    ("♪  Music note", "♪"),
    ("♫  Music notes", "♫"),
    ("☾  Moon", "☾"),
    ("☀  Sun", "☀"),
    ("✿  Flower", "✿"),
    ("❀  Flower outline", "❀"),
    (":3  Cat face", ":3"),
    (";3  Wink cat face", ";3"),
    ("^_^  Happy face", "^_^"),
    (">_<  Scrunched face", ">_<"),
    ("UwU", "UwU"),
    ("OwO", "OwO"),
    ("(｡♥‿♥｡)", "(｡♥‿♥｡)"),
    ("(づ｡◕‿‿◕｡)づ", "(づ｡◕‿‿◕｡)づ"),
]
TEXT_HAT_SYMBOL_MAP = dict(TEXT_HAT_SYMBOLS)

HALLOWEEN_CHARACTER_TOTAL = 10
HALLOWEEN_BONES_TOTAL = 10
HALLOWEEN_PUPPY_TOTAL = 1

HALLOWEEN_CHARACTER_NAMES = [
    "Reggie",
    "Charles",
    "Rachael",
    "Spooksby",
    "Barney",
    "King Arthritis",
    "Cerebrum Gigantus",
    "Luceyefer",
    "Gabreyeal",
    "Dire Chad",
]

HALLOWEEN_PROGRESS_ID_TO_NAME = {
    "FlamingCow": "Reggie",
    "Pumpkin": "Charles",
    "Skull": "Rachael",
    "Ghost": "Spooksby",
    "ScaryBanana": "Barney",
    "Skeleton": "King Arthritis",
    "EyeBat": "Luceyefer",
    "AngelEye": "Gabreyeal",
    "Spider": "Dire Chad",
}

BACKUP_FOLDER_NAME = "AngelTune_Backups"
PRESET_FOLDER_NAME = "AngelTune_Presets"

# Older releases used these names. AngelTune keeps reading them so existing
# backups and presets are not lost when upgrading.
LEGACY_BACKUP_FOLDER_NAME = "TowerUniteConfigTool_Backups"
LEGACY_PRESET_FOLDER_NAME = "TowerUniteConfigTool_Presets"

PRESET_SCHEMA_VERSION = 1


HUD_PREVIEW_FILES = {
    "Default": "hud_default.png",
    "TU Alpha": "hud_tu_alpha.png",
    "Minimalistic": "hud_minimalistic.png",
    "Cute": "hud_cute.png",
    "Cursive": "hud_cursive.png",
}


def resource_path(*parts):
    """Resolve bundled assets both from source and from a PyInstaller EXE."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base.joinpath(*parts)


def is_tower_running():
    if os.name != "nt":
        return False
    try:
        p = subprocess.run(
            ["tasklist"],
            capture_output=True,
            text=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            timeout=3,
        )
        text = p.stdout.lower()
        return ("tower-win64-shipping.exe" in text) or ("\ntower.exe" in text)
    except Exception:
        return False


def read_text_preserving(path: Path):
    data = path.read_bytes()
    newline = "\r\n" if b"\r\n" in data else "\n"
    if data.startswith(b"\xef\xbb\xbf"):
        encoding = "utf-8-sig"
    else:
        try:
            data.decode("utf-8")
            encoding = "utf-8"
        except UnicodeDecodeError:
            encoding = "cp1252"
    return data.decode(encoding), encoding, newline


def write_text_preserving(path: Path, text: str, encoding: str, newline: str):
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if newline == "\r\n":
        normalized = normalized.replace("\n", "\r\n")
    path.write_bytes(normalized.encode(encoding))


def parse_key_values(text):
    values = {}
    for raw in text.replace("\r\n", "\n").split("\n"):
        if not raw or raw.lstrip().startswith(("#", ";", "[")) or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def replace_key(text, key, value):
    # Only replace an existing exact key. Never invent unknown config keys.
    pattern = re.compile(rf"(?m)^({re.escape(key)}\s*=).*$")
    if not pattern.search(text):
        return text, False
    return pattern.sub(lambda m: f"{m.group(1)}{value}", text, count=1), True


def delete_key(text, key):
    """Remove one exact config override so the game can fall back to its built-in default."""
    pattern = re.compile(rf"(?m)^{re.escape(key)}\s*=.*(?:\r?\n|$)")
    if not pattern.search(text):
        return text, False
    return pattern.sub("", text, count=1), True


RGBA_RE = re.compile(
    r"\(\s*R=([0-9.+-]+)\s*,\s*G=([0-9.+-]+)\s*,\s*B=([0-9.+-]+)\s*,\s*A=([0-9.+-]+)\s*\)"
)


def parse_rgba(value):
    m = RGBA_RE.fullmatch(value.strip())
    if not m:
        return (1.0, 1.0, 1.0, 1.0)
    vals = tuple(max(0.0, min(1.0, float(x))) for x in m.groups())
    return vals


def rgba_to_hex(rgba):
    r, g, b, _ = rgba
    return "#{:02X}{:02X}{:02X}".format(round(r * 255), round(g * 255), round(b * 255))


def hex_to_rgb01(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def normalize_hex_color(value):
    """Accept RGB/RRGGBB with or without # and return canonical #RRGGBB."""
    h = str(value).strip().lstrip("#")

    if re.fullmatch(r"[0-9A-Fa-f]{3}", h):
        h = "".join(ch * 2 for ch in h)

    if not re.fullmatch(r"[0-9A-Fa-f]{6}", h):
        raise ValueError("HEX color must be #RRGGBB (or #RGB).")

    return "#" + h.upper()


def rgba_string(rgb, alpha):
    r, g, b = rgb
    return f"(R={r:.6f},G={g:.6f},B={b:.6f},A={alpha:.6f})"


def parse_region_filters(value):
    result = {
        "REGION_US": False,
        "REGION_EU": False,
        "REGION_APAC": False,
        "REGION_AU": False,
    }
    if not value:
        return result
    for key in result:
        m = re.search(rf"{re.escape(key)}\s*=\s*(True|False)", value, re.IGNORECASE)
        if m:
            result[key] = m.group(1).lower() == "true"
    return result


def format_region_filters(region_values):
    order = ["REGION_US", "REGION_EU", "REGION_APAC", "REGION_AU"]
    body = ",".join(
        f"{key}={'True' if region_values.get(key, False) else 'False'}"
        for key in order
    )
    return f"({body})"


def parse_allowed_image_hosts(value):
    if not value:
        return []
    return re.findall(r'"(https?://[^"]+)"', value)


def parse_quest_progress(value):
    quests = []
    if not value:
        return quests
    pattern = re.compile(
        r'\(Name="([^"]+)",State=([A-Z]+)(?:,ProgressIDs=\(([^)]*)\))?\)'
    )
    for name, state, progress_blob in pattern.findall(value):
        progress_ids = re.findall(r'"([^"]+)"', progress_blob or "")
        quests.append({"name": name, "state": state, "progress_ids": progress_ids})
    return quests


class ColorRow:
    def __init__(self, parent, label, key):
        self.key = key
        self.label = label
        self.rgb = (1.0, 1.0, 1.0)
        self.alpha = tk.DoubleVar(value=1.0)
        self.hex_var = tk.StringVar(value="#FFFFFF")
        self.use_game_default = False
        self.state_text = tk.StringVar(value="")
        self.on_change = None
        self.dirty_callback = None
        self._suspend_change = False

        self.frame = ttk.Frame(parent)
        self.frame.columnconfigure(9, weight=1)

        ttk.Label(self.frame, text=label).grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )

        self.swatch = tk.Canvas(
            self.frame,
            width=54,
            height=24,
            highlightthickness=1,
            highlightbackground="#777",
        )
        self.swatch.grid(row=0, column=1, sticky="w")
        self.swatch.bind("<Button-1>", lambda _e: self.choose())

        ttk.Button(
            self.frame, text="Choose…", command=self.choose
        ).grid(row=0, column=2, padx=(8, 10))

        ttk.Label(self.frame, text="HEX").grid(
            row=0, column=3, padx=(0, 4)
        )
        self.hex_entry = ttk.Entry(
            self.frame,
            textvariable=self.hex_var,
            width=10,
        )
        self.hex_entry.grid(row=0, column=4, sticky="w")
        self.hex_entry.bind("<Return>", self.apply_hex)
        self.hex_entry.bind("<FocusOut>", self.apply_hex)

        ttk.Label(self.frame, text="Alpha").grid(
            row=0, column=5, padx=(10, 4)
        )
        self.alpha_spin = ttk.Spinbox(
            self.frame,
            from_=0.0,
            to=1.0,
            increment=0.05,
            width=6,
            textvariable=self.alpha,
        )
        self.alpha_spin.grid(row=0, column=6)
        self.alpha.trace_add("write", self._alpha_changed)

        ttk.Button(
            self.frame,
            text="Game default",
            command=self.set_game_default,
        ).grid(row=0, column=7, padx=(10, 8))

        ttk.Label(
            self.frame,
            textvariable=self.state_text,
            foreground="#666",
        ).grid(row=0, column=8, padx=(4, 0), sticky="w")

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def set_on_change(self, callback):
        self.on_change = callback

    def set_dirty_callback(self, callback):
        self.dirty_callback = callback

    def _notify_change(self):
        if self._suspend_change:
            return
        if callable(self.on_change):
            self.on_change(self)
        if callable(self.dirty_callback):
            self.dirty_callback()

    def _alpha_changed(self, *_args):
        if self._suspend_change or self.use_game_default:
            return
        try:
            float(self.alpha.get())
        except Exception:
            return
        self.refresh()
        self._notify_change()

    def copy_state_from(self, other):
        self._suspend_change = True
        try:
            self.use_game_default = other.use_game_default
            self.rgb = tuple(other.rgb)
            try:
                self.alpha.set(float(other.alpha.get()))
            except Exception:
                self.alpha.set(1.0)

            if self.use_game_default:
                self.state_text.set("linked default")
                self.alpha_spin.configure(state="disabled")
                self.hex_entry.configure(state="disabled")
            else:
                self.state_text.set("linked")
                self.alpha_spin.configure(state="normal")
                self.hex_entry.configure(state="normal")

            self.refresh()
        finally:
            self._suspend_change = False

    def choose(self):
        try:
            initial = normalize_hex_color(self.hex_var.get())
        except ValueError:
            initial = rgba_to_hex((*self.rgb, self.alpha.get()))

        result = colorchooser.askcolor(
            color=initial, title=f"Choose {self.key}"
        )
        if result and result[1]:
            self.rgb = hex_to_rgb01(result[1])
            self.use_game_default = False
            self.state_text.set("")
            self.alpha_spin.configure(state="normal")
            self.hex_entry.configure(state="normal")
            self.refresh()
            self._notify_change()

    def apply_hex(self, _event=None):
        if self.use_game_default:
            return None

        try:
            normalized = normalize_hex_color(self.hex_var.get())
        except ValueError:
            self.hex_var.set(
                rgba_to_hex((*self.rgb, self.alpha.get()))
            )
            self.state_text.set("invalid HEX")
            return "break" if _event is not None else None

        self.rgb = hex_to_rgb01(normalized)
        self.hex_var.set(normalized)
        self.state_text.set("")
        self.refresh()
        self._notify_change()
        if _event is not None and getattr(_event, "keysym", "") == "Return":
            return "break"
        return None

    def set_game_default(self):
        self.use_game_default = True
        self.state_text.set("default on save")
        self.alpha_spin.configure(state="disabled")
        self.hex_entry.configure(state="disabled")
        self.refresh()
        self._notify_change()

    def refresh(self):
        self.swatch.delete("all")

        if self.use_game_default:
            self.swatch.create_rectangle(
                0, 0, 54, 24, fill="#F0F0F0", outline=""
            )
            self.swatch.create_text(
                27,
                12,
                text="AUTO",
                fill="#555555",
                font=("TkDefaultFont", 7, "bold"),
            )
        else:
            current_hex = rgba_to_hex((*self.rgb, self.alpha.get()))
            self.hex_var.set(current_hex)
            self.swatch.create_rectangle(
                0, 0, 54, 24, fill=current_hex, outline=""
            )

    def load(self, value):
        self._suspend_change = True
        try:
            rgba = parse_rgba(value)
            self.rgb = rgba[:3]
            self.alpha.set(rgba[3])
            self.hex_var.set(rgba_to_hex(rgba))
            self.use_game_default = False
            self.state_text.set("")
            self.alpha_spin.configure(state="normal")
            self.hex_entry.configure(state="normal")
            self.refresh()
        finally:
            self._suspend_change = False

    def load_as_game_default(self):
        self._suspend_change = True
        try:
            self.use_game_default = True
            self.state_text.set("game default")
            self.alpha_spin.configure(state="disabled")
            self.hex_entry.configure(state="disabled")
            self.refresh()
        finally:
            self._suspend_change = False

    def value(self):
        if self.use_game_default:
            return None

        try:
            normalized = normalize_hex_color(self.hex_var.get())
            self.rgb = hex_to_rgb01(normalized)
            self.hex_var.set(normalized)
        except ValueError:
            self.hex_var.set(
                rgba_to_hex((*self.rgb, self.alpha.get()))
            )

        try:
            a = max(0.0, min(1.0, float(self.alpha.get())))
        except Exception:
            a = 1.0

        return rgba_string(self.rgb, a)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{APP_VERSION} - Tower Unite Config Editor")
        self._set_window_icon()
        self.minsize(1100, 700)
        self.geometry("1260x820")

        self.path = tk.StringVar(value=str(DEFAULT_PATH))
        self.user_settings_path = tk.StringVar(value=str(DEFAULT_USER_SETTINGS_PATH))

        self.loaded_path = None
        self.original_text = ""
        self.encoding = "utf-8"
        self.newline = "\r\n"
        self.values = {}

        self.loaded_user_settings_path = None
        self.user_settings_original_text = ""
        self.user_settings_encoding = "utf-8"
        self.user_settings_newline = "\r\n"
        self.user_settings_values = {}

        self.status = tk.StringVar(value="Choose a Game.ini file.")
        self.dirty_status = tk.StringVar(value="Saved / loaded state")
        self.is_dirty = False
        self._suppress_dirty = True
        self._loaded_snapshot = None

        self.app_settings = load_app_settings()
        self.favorite_ids = set(self.app_settings.get("favorites", []))
        self.custom_color_presets = dict(self.app_settings.get("color_presets", {}))

        self.vars = {}
        self.volume_vars = {}
        self.volume_value_labels = {}
        self.color_rows = {}
        self.link_hud_main_colors = tk.BooleanVar(value=False)
        self._syncing_hud_main_colors = False
        self.region_vars = {
            "REGION_US": tk.BooleanVar(value=True),
            "REGION_EU": tk.BooleanVar(value=True),
            "REGION_APAC": tk.BooleanVar(value=True),
            "REGION_AU": tk.BooleanVar(value=True),
        }

        self.gus_vars = {}
        self.resolution_preset = tk.StringVar(value="2560 x 1440")
        self.display_mode = tk.StringVar(value="Fullscreen")

        self.known_emote_ids = set(VERIFIED_EMOTE_SHORTCUT_IDS)
        self.emote_id_choice = tk.StringVar()
        self.emote_observed_text = tk.StringVar(
            value="Verified shortcut IDs: " + ", ".join(VERIFIED_EMOTE_SHORTCUT_IDS)
        )

        # Scroll/search bookkeeping.
        self.tab_infos = {}
        self._current_tab_name = None
        self.search_records = []
        self.search_var = tk.StringVar()
        self.search_tab_filter = tk.StringVar(value="All tabs")
        self.favorite_option_var = tk.StringVar()
        self.preset_var = tk.StringVar()
        self.preset_paths = {}

        self.text_hat_preset_var = tk.StringVar()
        self.text_hat_preset_paths = {}

        # Random Text Hat monitoring is opt-in and runtime-only.
        # When disabled, AngelTune schedules no process polling at all.
        self.random_text_hat_enabled = tk.BooleanVar(value=False)
        self.random_text_hat_status = tk.StringVar(
            value="Off - no background monitoring"
        )
        self._random_text_hat_monitor_job = None
        self._random_text_hat_saw_game = False
        self._random_text_hat_last_path = None
        self.text_hat_random_pool = set(
            self.app_settings.get("text_hat_random_pool", [])
        )
        self.text_hat_pool_status = tk.StringVar(value="Pool: all saved presets")

        self.color_preset_var = tk.StringVar(value="Angel Pink")

        self.dashboard_config = tk.StringVar(value="Config files not loaded yet")
        self.dashboard_hud = tk.StringVar(value="HUD: -")
        self.dashboard_resolution = tk.StringVar(value="Resolution: -")
        self.dashboard_text_hat = tk.StringVar(value="Text Hat: -")
        self.dashboard_backup = tk.StringVar(value="Latest backup: -")
        self.dashboard_health = tk.StringVar(value="Health: not checked")

        self.ui_theme = "angel"
        self.default_ttk_theme = ttk.Style().theme_use()

        self._build_ui()
        self._install_change_tracking()
        self._suppress_dirty = False
        self._set_clean_baseline()
        self.apply_ui_theme()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(60, self.show_startup_disclaimer)
        if DEFAULT_PATH.exists() or DEFAULT_USER_SETTINGS_PATH.exists():
            self.after(180, self.load_files)

    # ------------------------------------------------------------------ UI --
    def _build_ui(self):
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(4, weight=1)

        filebar = ttk.Frame(root)
        filebar.grid(row=0, column=0, sticky="ew")
        filebar.columnconfigure(1, weight=1)

        ttk.Label(filebar, text="Game.ini").grid(row=0, column=0, padx=(0, 8), pady=2)
        ttk.Entry(filebar, textvariable=self.path).grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Button(filebar, text="Browse…", command=self.browse).grid(row=0, column=2, padx=(8, 0), pady=2)

        ttk.Label(filebar, text="GameUserSettings.ini").grid(row=1, column=0, padx=(0, 8), pady=2)
        ttk.Entry(filebar, textvariable=self.user_settings_path).grid(row=1, column=1, sticky="ew", pady=2)
        ttk.Button(filebar, text="Browse…", command=self.browse_user_settings).grid(row=1, column=2, padx=(8, 0), pady=2)

        ttk.Button(filebar, text="Reload both", command=self.load_files).grid(
            row=0, column=3, rowspan=2, padx=(8, 0), sticky="ns"
        )
        ttk.Button(filebar, text="Open folder", command=self.open_folder).grid(
            row=0, column=4, rowspan=2, padx=(8, 0), sticky="ns"
        )

        self.theme_button = ttk.Button(
            filebar,
            text="🎨 Default",
            width=11,
            command=self.toggle_ui_theme,
        )
        self.theme_button.grid(
            row=0, column=5, rowspan=2, padx=(8, 0), sticky="ns"
        )

        note = ttk.Label(
            root,
            text=(
                "Safe scope: edits known values in Game.ini and GameUserSettings.ini only. "
                "Automatic backups are created before every successful save."
            ),
            foreground="#555",
        )
        note.grid(row=1, column=0, sticky="w", pady=(8, 8))

        searchbar = ttk.Frame(root)
        searchbar.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        searchbar.columnconfigure(1, weight=1)
        ttk.Label(searchbar, text="Find option").grid(
            row=0, column=0, padx=(0, 8)
        )
        self.search_box = ttk.Entry(
            searchbar,
            textvariable=self.search_var,
        )
        self.search_box.grid(row=0, column=1, sticky="ew")
        self.search_box.bind("<KeyRelease>", self._on_search_keyrelease)
        self.search_box.bind("<Return>", self.jump_to_search)
        self.search_box.bind("<Escape>", self._hide_search_suggestions)
        self.search_box.bind("<Tab>", self._accept_first_suggestion)
        self.search_box.bind("<Right>", self._accept_first_suggestion)

        self.search_filter_combo = ttk.Combobox(
            searchbar,
            textvariable=self.search_tab_filter,
            state="readonly",
            width=20,
            values=["All tabs"],
        )
        self.search_filter_combo.grid(row=0, column=2, padx=(8, 0))
        self.search_filter_combo.bind(
            "<<ComboboxSelected>>",
            lambda _e: self._on_search_keyrelease(None),
        )

        ttk.Button(searchbar, text="Go", command=self.jump_to_search).grid(
            row=0, column=3, padx=(8, 0)
        )
        ttk.Button(
            searchbar,
            text="★ Favorite",
            command=self.favorite_current_search,
        ).grid(row=0, column=4, padx=(8, 0))
        ttk.Button(
            searchbar,
            text="Clear",
            command=self.clear_search,
        ).grid(row=0, column=5, padx=(8, 0))

        # Custom autocomplete list: unlike a native Combobox dropdown, this does
        # not steal keyboard focus while the user is still typing.
        self.search_suggestion_frame = ttk.Frame(searchbar)
        self.search_suggestion_frame.grid(
            row=1, column=1, sticky="ew", pady=(3, 0)
        )
        self.search_suggestion_frame.columnconfigure(0, weight=1)

        self.search_suggestions = tk.Listbox(
            self.search_suggestion_frame,
            height=5,
            exportselection=False,
            activestyle="dotbox",
        )
        self.search_suggestions.grid(row=0, column=0, sticky="ew")
        self.search_suggestions.bind(
            "<ButtonRelease-1>", self._on_suggestion_click
        )
        self.search_suggestions.bind(
            "<Double-Button-1>", self._on_suggestion_click
        )
        self.search_suggestions.bind(
            "<Return>", self._on_suggestion_activate
        )

        suggestion_scroll = ttk.Scrollbar(
            self.search_suggestion_frame,
            orient="vertical",
            command=self.search_suggestions.yview,
        )
        suggestion_scroll.grid(row=0, column=1, sticky="ns")
        self.search_suggestions.configure(
            yscrollcommand=suggestion_scroll.set
        )
        self.search_suggestion_frame.grid_remove()

        ttk.Label(
            searchbar,
            text=(
                "Search by option name, key, tab, or multiple words. Use the tab filter "
                "to narrow results. Tab/Right Arrow accepts the first suggestion."
            ),
            foreground="#666",
            wraplength=760,
            justify="left",
        ).grid(row=2, column=1, sticky="w", pady=(3, 0))

        presetbar = ttk.LabelFrame(root, text="Presets", padding=(8, 6))
        presetbar.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        presetbar.columnconfigure(1, weight=1)

        ttk.Label(presetbar, text="Preset").grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        self.preset_combo = ttk.Combobox(
            presetbar,
            textvariable=self.preset_var,
            state="readonly",
        )
        self.preset_combo.grid(row=0, column=1, sticky="ew")
        self.preset_combo.bind(
            "<<ComboboxSelected>>",
            lambda _e: self.apply_selected_preset(),
        )

        ttk.Button(
            presetbar,
            text="Save current as…",
            command=self.save_current_preset,
        ).grid(row=0, column=2, padx=(8, 0))

        ttk.Button(
            presetbar,
            text="Apply",
            command=self.apply_selected_preset,
        ).grid(row=0, column=3, padx=(8, 0))

        ttk.Button(
            presetbar,
            text="Delete",
            command=self.delete_selected_preset,
        ).grid(row=0, column=4, padx=(8, 0))

        ttk.Button(
            presetbar,
            text="Import…",
            command=self.import_preset_file,
        ).grid(row=0, column=5, padx=(8, 0))

        ttk.Button(
            presetbar,
            text="Export / Share…",
            command=self.export_selected_preset,
        ).grid(row=0, column=6, padx=(8, 0))

        ttk.Button(
            presetbar,
            text="Open presets",
            command=self.open_preset_folder,
        ).grid(row=0, column=7, padx=(8, 0))

        ttk.Label(
            presetbar,
            text=(
                "Selecting a preset only loads its values into the editor. "
                "Click Save changes when you want to write them to the INI files."
            ),
            foreground="#666",
            wraplength=900,
            justify="left",
        ).grid(row=1, column=1, columnspan=7, sticky="w", pady=(4, 0))

        self.tabs = ttk.Notebook(root)
        self.tabs.grid(row=4, column=0, sticky="nsew")

        self._build_home_tab()
        self._build_favorites_tab()
        self._build_hud_tab()
        self._build_display_tab()
        self._build_general_tab()
        self._build_graphics_tab()
        self._build_sound_tab()
        self._build_items_tab()
        self._build_gameplay_tab()
        self._build_workshop_canvas_tab()
        self._build_condo_tab()
        self._build_privacy_content_tab()
        self._build_profile_tab()
        self._build_backup_tools_tab()
        self._build_advanced_tab()

        self._refresh_search_choices()
        self._refresh_search_filter_values()
        self.refresh_preset_list()
        self.refresh_text_hat_preset_list()
        self._refresh_favorites_ui()
        self._refresh_color_preset_choices()
        self.refresh_backup_history()
        self.update_dashboard()

        bottom = ttk.Frame(root)
        bottom.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        bottom.columnconfigure(0, weight=1)
        status_wrap = ttk.Frame(bottom)
        status_wrap.grid(row=0, column=0, sticky="ew")
        status_wrap.columnconfigure(0, weight=1)
        ttk.Label(status_wrap, textvariable=self.status).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            status_wrap,
            textvariable=self.dirty_status,
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w")

        ttk.Button(
            bottom, text="Undo", command=self.undo_since_load
        ).grid(row=0, column=1, padx=(8, 0))
        ttk.Button(
            bottom, text="Reset tab", command=self.reset_current_tab
        ).grid(row=0, column=2, padx=(8, 0))
        ttk.Button(
            bottom, text="Preview changes", command=self.show_changes_preview
        ).grid(row=0, column=3, padx=(8, 0))
        ttk.Button(
            bottom, text="Create backup", command=self.create_manual_backup
        ).grid(row=0, column=4, padx=(8, 0))
        ttk.Button(
            bottom, text="Save changes", command=self.save_changes,
            style="Accent.TButton",
        ).grid(row=0, column=5, padx=(8, 0))

        # Scroll selected category with the mouse wheel, except inside controls
        # that have their own scrolling behavior.
        self.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.bind_all("<Button-4>", self._on_linux_wheel, add="+")
        self.bind_all("<Button-5>", self._on_linux_wheel, add="+")

    def create_scrollable_tab(self, title):
        outer = ttk.Frame(self.tabs)
        outer.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)
        self.tabs.add(outer, text=title)

        canvas_bg = ttk.Style().lookup("TFrame", "background") or self.cget("background")
        canvas = tk.Canvas(
            outer,
            highlightthickness=0,
            borderwidth=0,
            background=canvas_bg,
        )
        scrollbar = ttk.Scrollbar(
            outer, orient="vertical", command=canvas.yview
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        body = ttk.Frame(canvas)
        body.columnconfigure(0, weight=1)
        window_id = canvas.create_window((0, 0), window=body, anchor="nw")

        def update_scrollregion(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def fit_width(event):
            canvas.itemconfigure(window_id, width=max(1, event.width))

        body.bind("<Configure>", update_scrollregion)
        canvas.bind("<Configure>", fit_width)

        info = {
            "name": title,
            "outer": outer,
            "canvas": canvas,
            "body": body,
        }
        self.tab_infos[title] = info
        self._current_tab_name = title
        return body

    def section(self, parent, title, row):
        box = ttk.LabelFrame(parent, text=title, padding=10)
        box.grid(row=row, column=0, sticky="ew", padx=10, pady=(10, 0))
        box.columnconfigure(1, weight=1)
        self.register_search(title, "", box)
        return box

    def register_search(self, label, key, widget):
        if not self._current_tab_name:
            return
        display = f"{label}  [{self._current_tab_name}]"
        if key:
            display = f"{label} - {key}  [{self._current_tab_name}]"
        self.search_records.append(
            {
                "display": display,
                "label": label,
                "key": key,
                "tab": self._current_tab_name,
                "widget": widget,
            }
        )

    def _refresh_search_choices(self, records=None):
        records = self.search_records if records is None else records

        unique_records = []
        seen = set()
        for rec in records:
            if rec["display"] in seen:
                continue
            seen.add(rec["display"])
            unique_records.append(rec)

        self.filtered_search_records = unique_records

        if not hasattr(self, "search_suggestions"):
            return

        self.search_suggestions.delete(0, tk.END)
        for rec in unique_records:
            self.search_suggestions.insert(tk.END, rec["display"])

        query = self.search_var.get().strip() if hasattr(self, "search_var") else ""
        if query and unique_records:
            visible_rows = min(6, len(unique_records))
            self.search_suggestions.configure(height=max(1, visible_rows))
            self.search_suggestion_frame.grid()
        else:
            self.search_suggestion_frame.grid_remove()

    def _search_prefix_match(self, rec, query):
        """Flexible search: every typed word must occur somewhere in label/key/tab."""
        q = query.strip().lower()
        if not q:
            return True
        haystack = " ".join([
            rec.get("label", ""),
            rec.get("key", ""),
            rec.get("tab", ""),
            rec.get("display", ""),
        ]).lower()
        terms = [t for t in re.split(r"\s+", q) if t]
        return all(term in haystack for term in terms)

    def _on_search_keyrelease(self, event):
        # Navigation/accept keys are handled by their own bindings.
        if event is not None and event.keysym in {
            "Up", "Down", "Return", "Escape", "Tab",
            "Right", "Left", "Home", "End"
        }:
            return

        query = self.search_var.get().strip().lower()

        if not query:
            self.filtered_search_records = []
            self.search_suggestions.delete(0, tk.END)
            self.search_suggestion_frame.grid_remove()
            return

        tab_filter = self.search_tab_filter.get().strip()
        matches = [
            rec for rec in self.search_records
            if self._search_prefix_match(rec, query)
            and (tab_filter == "All tabs" or rec.get("tab") == tab_filter)
        ]
        self._refresh_search_choices(matches)

        # Keep the caret/focus in the text field. The suggestion list is only
        # visual until the user clicks it or accepts a suggestion.
        self.search_box.focus_set()
        self.search_box.icursor(tk.END)

    def _hide_search_suggestions(self, _event=None):
        if hasattr(self, "search_suggestion_frame"):
            self.search_suggestion_frame.grid_remove()
        return "break" if _event is not None else None

    def _accept_first_suggestion(self, event=None):
        records = getattr(self, "filtered_search_records", [])
        if not records:
            return None

        # Do not hijack Right Arrow when the caret is in the middle of the text.
        if event is not None and getattr(event, "keysym", "") == "Right":
            try:
                if self.search_box.index(tk.INSERT) < len(self.search_var.get()):
                    return None
            except Exception:
                pass

        self.search_var.set(records[0]["display"])
        self.search_box.icursor(tk.END)
        self.search_box.focus_set()
        return "break"

    def _on_suggestion_click(self, _event=None):
        selection = self.search_suggestions.curselection()
        if not selection:
            return
        index = selection[0]
        records = getattr(self, "filtered_search_records", [])
        if index >= len(records):
            return
        self.search_var.set(records[index]["display"])
        self.search_box.focus_set()
        self.search_box.icursor(tk.END)

    def _on_suggestion_activate(self, _event=None):
        self._on_suggestion_click()
        self.jump_to_search()
        return "break"

    def jump_to_search(self, _event=None):
        query = self.search_var.get().strip()
        if not query:
            self.status.set("Type an option name or Game.ini key first.")
            return

        q = query.lower()
        exact = [
            rec for rec in self.search_records
            if q == rec["display"].lower()
            or q == rec["label"].lower()
            or q == rec["key"].lower()
        ]
        candidates = exact or [
            rec for rec in self.search_records
            if self._search_prefix_match(rec, q)
        ]
        if not candidates:
            self.status.set(f'No option found for "{query}".')
            return

        rec = candidates[0]
        self.search_suggestion_frame.grid_remove()
        info = self.tab_infos[rec["tab"]]
        self.tabs.select(info["outer"])
        self.update_idletasks()

        body = info["body"]
        canvas = info["canvas"]
        widget = rec["widget"]

        try:
            y = widget.winfo_rooty() - body.winfo_rooty()
            content_h = max(body.winfo_reqheight(), 1)
            viewport_h = max(canvas.winfo_height(), 1)
            scrollable_h = max(content_h - viewport_h, 1)
            target_y = max(0, min(y - 35, scrollable_h))
            canvas.yview_moveto(target_y / scrollable_h)
            self.after(80, lambda: self._focus_search_target(widget))
        except Exception:
            pass

        self.status.set(
            f'Jumped to "{rec["label"]}" in {rec["tab"]}.'
        )

    def _focus_search_target(self, widget):
        try:
            widget.focus_set()
        except Exception:
            pass

    def _selected_scroll_canvas(self):
        selected = self.tabs.select()
        for info in self.tab_infos.values():
            if str(info["outer"]) == selected:
                return info["canvas"]
        return None

    def _on_mousewheel(self, event):
        cls = ""
        try:
            cls = event.widget.winfo_class()
        except Exception:
            pass
        if cls in {"Text", "Listbox", "Spinbox", "TSpinbox"}:
            return
        canvas = self._selected_scroll_canvas()
        if canvas is None:
            return
        delta = getattr(event, "delta", 0)
        if delta:
            steps = -1 if delta > 0 else 1
            canvas.yview_scroll(steps * 3, "units")
            return "break"

    def _on_linux_wheel(self, event):
        cls = ""
        try:
            cls = event.widget.winfo_class()
        except Exception:
            pass
        if cls in {"Text", "Listbox", "Spinbox", "TSpinbox"}:
            return
        canvas = self._selected_scroll_canvas()
        if canvas is None:
            return
        canvas.yview_scroll(-3 if event.num == 4 else 3, "units")
        return "break"

    def bool_control(self, parent, row, label, key):
        var = tk.BooleanVar(value=False)
        self.vars[key] = var
        control = ttk.Checkbutton(parent, text=label, variable=var)
        control.grid(
            row=row, column=0, columnspan=2, sticky="w", pady=3
        )
        self.register_search(label, key, control)
        return control

    def spin_control(
        self, parent, row, label, key, from_, to, inc=1.0, width=10
    ):
        var = tk.StringVar()
        self.vars[key] = var
        ttk.Label(parent, text=label).grid(
            row=row, column=0, sticky="w", pady=4
        )
        control = ttk.Spinbox(
            parent,
            from_=from_,
            to=to,
            increment=inc,
            textvariable=var,
            width=width,
        )
        control.grid(row=row, column=1, sticky="w", pady=4)
        self.register_search(label, key, control)
        return control

    def text_control(self, parent, row, label, key, width=48):
        var = tk.StringVar()
        self.vars[key] = var
        ttk.Label(parent, text=label).grid(
            row=row, column=0, sticky="w", pady=4, padx=(0, 10)
        )
        control = ttk.Entry(parent, textvariable=var, width=width)
        control.grid(row=row, column=1, sticky="ew", pady=4)
        self.register_search(label, key, control)
        return control

    def volume_control(self, parent, row, label, key):
        var = tk.DoubleVar(value=100.0)
        value_label = tk.StringVar(value="100%")
        self.volume_vars[key] = var
        self.volume_value_labels[key] = value_label

        ttk.Label(parent, text=label).grid(
            row=row, column=0, sticky="w", pady=3, padx=(0, 10)
        )
        control = ttk.Scale(
            parent,
            from_=0,
            to=100,
            orient="horizontal",
            variable=var,
        )
        control.grid(row=row, column=1, sticky="ew", pady=3)

        value_entry = ttk.Entry(
            parent,
            textvariable=value_label,
            width=7,
            justify="right",
        )
        value_entry.grid(
            row=row, column=2, sticky="e", padx=(8, 0), pady=3
        )

        def format_pct(value):
            try:
                pct = max(0.0, min(100.0, float(value)))
            except Exception:
                pct = 0.0

            if abs(pct - round(pct)) < 0.0001:
                return f"{int(round(pct))}%"
            return f"{pct:.1f}%"

        def update_entry(_value=None):
            value_label.set(format_pct(var.get()))

        def apply_entry(_event=None):
            raw = value_label.get().strip().replace(",", ".")
            if raw.endswith("%"):
                raw = raw[:-1].strip()

            try:
                pct = float(raw)
            except ValueError:
                value_label.set(format_pct(var.get()))
                self.status.set(
                    f'{label}: enter a percentage from 0 to 100.'
                )
                return "break" if _event is not None else None

            pct = max(0.0, min(100.0, pct))
            var.set(pct)
            value_label.set(format_pct(pct))
            self.status.set(f"{label}: {format_pct(pct)}")
            return "break" if _event is not None and getattr(_event, "keysym", "") == "Return" else None

        # Save the callback so typed values can also be committed if the user
        # clicks Save changes while the cursor is still inside the field.
        if not hasattr(self, "volume_entry_apply"):
            self.volume_entry_apply = {}
        self.volume_entry_apply[key] = apply_entry

        control.configure(command=update_entry)
        value_entry.bind("<Return>", apply_entry)
        value_entry.bind("<FocusOut>", apply_entry)

        update_entry()
        self.register_search(label, key, control)
        self.register_search(label + " percentage", key, value_entry)
        return control


    def gus_bool_control(self, parent, row, label, key):
        var = tk.BooleanVar(value=False)
        self.gus_vars[key] = var
        control = ttk.Checkbutton(parent, text=label, variable=var)
        control.grid(row=row, column=0, columnspan=2, sticky="w", pady=3)
        self.register_search(label, f"GameUserSettings:{key}", control)
        return control

    def gus_spin_control(self, parent, row, label, key, from_, to, inc=1.0, width=10):
        var = tk.StringVar()
        self.gus_vars[key] = var
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4)
        control = ttk.Spinbox(
            parent, from_=from_, to=to, increment=inc, textvariable=var, width=width
        )
        control.grid(row=row, column=1, sticky="w", pady=4)
        self.register_search(label, f"GameUserSettings:{key}", control)
        return control

    def _apply_resolution_preset(self, _event=None):
        raw = self.resolution_preset.get().lower().replace("×", "x")
        m = re.match(r"\\s*(\\d+)\\s*x\\s*(\\d+)\\s*$", raw)
        if not m:
            self.status.set("Resolution preset must look like 2560 x 1440.")
            return
        self.gus_vars["ResolutionSizeX"].set(m.group(1))
        self.gus_vars["ResolutionSizeY"].set(m.group(2))
        self.status.set(f"Resolution set to {m.group(1)} x {m.group(2)}. Save to apply.")

    # ------------------------------------------------------- color presets --
    def _all_color_presets(self):
        result = dict(BUILTIN_COLOR_PRESETS)
        for name, value in self.custom_color_presets.items():
            try:
                result[str(name)] = normalize_hex_color(value)
            except Exception:
                pass
        return result

    def _refresh_color_preset_choices(self):
        if not hasattr(self, "color_preset_combo"):
            return
        presets = self._all_color_presets()
        names = list(presets.keys())
        self.color_preset_combo["values"] = names
        if self.color_preset_var.get() not in presets:
            self.color_preset_var.set(names[0] if names else "")

    def apply_color_preset(self, target="hud_pair"):
        name = self.color_preset_var.get().strip()
        value = self._all_color_presets().get(name)
        if not value:
            self.status.set("Choose a color preset first.")
            return
        rgba = rgba_string(hex_to_rgb01(value), 1.0)
        if target == "hud_pair":
            keys = ["Inventory.Color", "HUD.KeyPrompt.Color"]
        else:
            keys = list(self.color_rows.keys())
        for key in keys:
            row = self.color_rows.get(key)
            if row is not None:
                row.load(rgba)
        self._mark_dirty()
        self.status.set(f'Applied color preset "{name}" to {len(keys)} color setting(s).')

    def save_custom_color_preset(self):
        row = self.color_rows.get("Inventory.Color")
        if row is None or row.use_game_default:
            messagebox.showinfo(APP_NAME, "Choose a custom Inventory Color first.")
            return
        name = simpledialog.askstring(
            APP_NAME,
            "Name for this color preset:",
            parent=self,
        )
        if name is None:
            return
        name = name.strip()
        if not name:
            return
        try:
            value = normalize_hex_color(row.hex_var.get())
        except ValueError as e:
            messagebox.showerror(APP_NAME, str(e))
            return
        self.custom_color_presets[name] = value
        self.color_preset_var.set(name)
        self._save_tool_settings()
        self._refresh_color_preset_choices()
        self.status.set(f'Saved color preset "{name}" ({value}).')

    # --------------------------------------------------------- sound groups --
    def _set_volume_value(self, key, value):
        var = self.volume_vars.get(key)
        if var is None:
            return
        pct = max(0.0, min(100.0, float(value)))
        var.set(pct)
        label = self.volume_value_labels.get(key)
        if label is not None:
            shown = f"{int(pct)}%" if abs(pct - round(pct)) < 0.0001 else f"{pct:.1f}%"
            label.set(shown)

    def apply_sound_group(self, mode):
        if mode == "restore":
            snap = self._loaded_snapshot or {}
            for key, value in snap.get("volumes_percent", {}).items():
                self._set_volume_value(key, value)
            self._refresh_dirty_from_snapshot()
            self.status.set("Sound sliders restored to their loaded values.")
            return

        if mode == "all100":
            updates = {key: 100 for key in self.volume_vars}
        elif mode == "all50":
            updates = {key: 50 for key in self.volume_vars}
        elif mode == "mute":
            updates = {key: 0 for key in self.volume_vars}
        elif mode == "media_off":
            updates = {
                "Volume.MusicVolume": 0,
                "Volume.MediaVolume": 0,
                "Volume.PlazaMusicVolume": 0,
                "Volume.SoundEmitterVolume": 0,
                "Volume.WorkshopSoundVolume": 0,
                "MediaVolume": 0,
            }
        elif mode == "voice_off":
            updates = {
                "Volume.VoiceVolume": 0,
                "Volume.VOVolume": 0,
            }
        else:
            return

        for key, value in updates.items():
            self._set_volume_value(key, value)
        self._mark_dirty()
        self.status.set("Sound group applied. Save changes to write it to Game.ini.")

    # ----------------------------------------------- dirty / undo / preview --
    def _install_change_tracking(self):
        tracked = []
        tracked.extend(self.vars.values())
        tracked.extend(self.gus_vars.values())
        tracked.extend(self.volume_vars.values())
        tracked.extend(self.region_vars.values())
        tracked.extend([
            self.hud_style,
            self.display_mode,
            self.resolution_preset,
        ])
        seen = set()
        for var in tracked:
            if id(var) in seen:
                continue
            seen.add(id(var))
            try:
                var.trace_add("write", lambda *_args: self._mark_dirty())
            except Exception:
                pass
        for row in self.color_rows.values():
            row.set_dirty_callback(self._mark_dirty)

    def _capture_editor_snapshot(self):
        data = self._capture_preset_state()
        data["link_hud_main_colors"] = bool(self.link_hud_main_colors.get())
        return data

    def _snapshot_signature(self, snapshot):
        try:
            return json.dumps(snapshot, sort_keys=True, ensure_ascii=False, default=str)
        except Exception:
            return repr(snapshot)

    def _update_window_title(self):
        star = " *" if self.is_dirty else ""
        self.title(f"{APP_NAME} v{APP_VERSION}{star} - Tower Unite Config Editor")
        self.dirty_status.set(
            "Unsaved changes" if self.is_dirty else "Saved / loaded state"
        )

    def _mark_dirty(self):
        if self._suppress_dirty:
            return
        self.is_dirty = True
        self._update_window_title()
        self.update_dashboard()

    def _refresh_dirty_from_snapshot(self):
        if self._loaded_snapshot is None:
            return
        try:
            current = self._capture_editor_snapshot()
            self.is_dirty = (
                self._snapshot_signature(current)
                != self._snapshot_signature(self._loaded_snapshot)
            )
        except Exception:
            self.is_dirty = True
        self._update_window_title()

    def _set_clean_baseline(self):
        try:
            self._loaded_snapshot = self._capture_editor_snapshot()
        except Exception:
            self._loaded_snapshot = None
        self.is_dirty = False
        self._update_window_title()
        self.update_dashboard()

    def _restore_editor_snapshot(self, snapshot):
        if not snapshot:
            return
        old_suppress = self._suppress_dirty
        self._suppress_dirty = True
        try:
            style = snapshot.get("hud_style")
            if style in HUD_STYLES:
                self.hud_style.set(style)
            if snapshot.get("display_mode"):
                self.display_mode.set(snapshot["display_mode"])
            if snapshot.get("resolution_preset"):
                self.resolution_preset.set(snapshot["resolution_preset"])

            for key, value in snapshot.get("game_vars", {}).items():
                var = self.vars.get(key)
                if var is not None:
                    self._set_tk_var_from_preset(var, value)
            for key, value in snapshot.get("game_user_settings_vars", {}).items():
                var = self.gus_vars.get(key)
                if var is not None:
                    self._set_tk_var_from_preset(var, value)
            for key, value in snapshot.get("volumes_percent", {}).items():
                self._set_volume_value(key, value)
            for key, value in snapshot.get("region_filters", {}).items():
                var = self.region_vars.get(key)
                if var is not None:
                    var.set(bool(value))
            for key, value in snapshot.get("colors", {}).items():
                row = self.color_rows.get(key)
                if row is None:
                    continue
                if value is None:
                    row.load_as_game_default()
                else:
                    row.load(value)
            self.link_hud_main_colors.set(bool(snapshot.get("link_hud_main_colors", False)))
            self._update_hud_preview()
        finally:
            self._suppress_dirty = old_suppress
        self.update_dashboard()

    def undo_since_load(self):
        if not self._loaded_snapshot:
            self.status.set("Nothing has been loaded yet.")
            return
        self._restore_editor_snapshot(self._loaded_snapshot)
        self.is_dirty = False
        self._update_window_title()
        self.status.set("Unsaved editor changes were reverted to the last loaded/saved state.")

    def _selected_tab_name(self):
        selected = self.tabs.select()
        for name, info in self.tab_infos.items():
            if str(info["outer"]) == str(selected):
                return name
        return ""

    def reset_current_tab(self):
        tab_name = self._selected_tab_name()
        if not self._loaded_snapshot:
            self.status.set("Load the config files first.")
            return
        if tab_name in {"Home", "Favorites", "Backups & Health", "Info & Profile"}:
            self.status.set(f"{tab_name} has no editable config section to reset.")
            return

        snapshot = self._loaded_snapshot
        records = [r for r in self.search_records if r.get("tab") == tab_name and r.get("key")]
        keys = {r["key"] for r in records}
        old_suppress = self._suppress_dirty
        self._suppress_dirty = True
        try:
            if "HUD.Mode" in keys:
                style = snapshot.get("hud_style")
                if style in HUD_STYLES:
                    self.hud_style.set(style)

            for raw_key in keys:
                key = raw_key
                if key.startswith("GameUserSettings:"):
                    key = key.split(":", 1)[1]
                    if "/" in key:
                        continue
                    value = snapshot.get("game_user_settings_vars", {}).get(key, None)
                    var = self.gus_vars.get(key)
                    if var is not None and value is not None:
                        self._set_tk_var_from_preset(var, value)
                    continue

                if key == "Chat.RegionFilters":
                    for region, value in snapshot.get("region_filters", {}).items():
                        if region in self.region_vars:
                            self.region_vars[region].set(bool(value))
                    continue

                if key in snapshot.get("colors", {}):
                    row = self.color_rows.get(key)
                    if row is not None:
                        value = snapshot["colors"][key]
                        if value is None:
                            row.load_as_game_default()
                        else:
                            row.load(value)
                    continue

                if key in snapshot.get("volumes_percent", {}):
                    self._set_volume_value(key, snapshot["volumes_percent"][key])
                    continue

                if key in snapshot.get("game_vars", {}):
                    var = self.vars.get(key)
                    if var is not None:
                        self._set_tk_var_from_preset(var, snapshot["game_vars"][key])

            if tab_name == "Display / Resolution":
                self.display_mode.set(snapshot.get("display_mode", self.display_mode.get()))
                self.resolution_preset.set(snapshot.get("resolution_preset", self.resolution_preset.get()))
        finally:
            self._suppress_dirty = old_suppress

        self._refresh_dirty_from_snapshot()
        self._update_hud_preview()
        self.update_dashboard()
        self.status.set(f'Reset "{tab_name}" to the last loaded/saved values.')

    def _changed_editor_keys(self):
        """Return only config keys that differ from the last loaded/saved editor state."""
        if not self._loaded_snapshot:
            return set(), set()
        current = self._capture_editor_snapshot()
        base = self._loaded_snapshot
        game_keys = set()
        gus_keys = set()

        if current.get("hud_style") != base.get("hud_style"):
            game_keys.add("HUD.Mode")

        for section in ["game_vars", "colors", "volumes_percent"]:
            cur = current.get(section, {})
            old = base.get(section, {})
            for key in set(cur) | set(old):
                if cur.get(key) != old.get(key):
                    game_keys.add(key)

        if current.get("region_filters", {}) != base.get("region_filters", {}):
            game_keys.add("Chat.RegionFilters")

        cur_gus = current.get("game_user_settings_vars", {})
        old_gus = base.get("game_user_settings_vars", {})
        for key in set(cur_gus) | set(old_gus):
            if cur_gus.get(key) != old_gus.get(key):
                gus_keys.add(key)

        if current.get("display_mode") != base.get("display_mode"):
            gus_keys.add("FullscreenMode")

        return game_keys, gus_keys

    def _collect_change_rows(self):
        rows = []
        old_suppress = self._suppress_dirty
        self._suppress_dirty = True
        try:
            game_changes = self.collect_changes() if self.loaded_path else {}
            gus_changes = self.collect_user_settings_changes() if self.loaded_user_settings_path else {}
        except ValueError as e:
            self._suppress_dirty = old_suppress
            return [], str(e)
        finally:
            self._suppress_dirty = old_suppress

        changed_game_keys, changed_gus_keys = self._changed_editor_keys()

        for key, new_value in game_changes.items():
            if key not in changed_game_keys:
                continue
            old_present = key in self.values
            old_value = self.values.get(key)
            if new_value is None:
                if not old_present:
                    continue
                shown_new = "<Game default / override removed>"
            else:
                shown_new = str(new_value)
                if old_present and old_value == shown_new:
                    continue
                if not old_present:
                    continue
            rows.append(("Game.ini", key, old_value if old_present else "<missing>", shown_new))

        for key, new_value in gus_changes.items():
            if key not in changed_gus_keys:
                continue
            if key not in self.user_settings_values:
                continue
            old_value = self.user_settings_values.get(key)
            if str(old_value) == str(new_value):
                continue
            rows.append(("GameUserSettings.ini", key, old_value, new_value))
        return rows, None

    def show_changes_preview(self):
        rows, error = self._collect_change_rows()
        if error:
            messagebox.showerror(APP_NAME, error)
            return
        if not rows:
            self.is_dirty = False
            self._update_window_title()
            messagebox.showinfo(APP_NAME, "No config changes are currently pending.")
            return

        lines = [f"Pending changes: {len(rows)}", ""]
        for source, key, old, new in rows:
            lines.append(f"[{source}] {key}")
            lines.append(f"  {old}  ->  {new}")
            lines.append("")
        self._show_text_window("Changes Preview", "\n".join(lines), width=100, height=28)

    def _show_text_window(self, title, text, width=90, height=26):
        win = tk.Toplevel(self)
        win.title(f"{APP_NAME} - {title}")
        win.transient(self)
        win.geometry("900x620")
        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        box = tk.Text(frame, wrap="word", width=width, height=height)
        box.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=box.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        box.configure(yscrollcommand=scroll.set)
        box.insert("1.0", text)
        box.configure(state="disabled")
        ttk.Button(frame, text="Close", command=win.destroy).grid(
            row=1, column=0, columnspan=2, pady=(10, 0)
        )
        self._apply_tk_widget_theme(win, {
            "bg": "#21151D" if self.ui_theme == "angel" else "#F0F0F0",
            "field": "#FFF1F5" if self.ui_theme == "angel" else "#FFFFFF",
            "field_fg": "#3B1E2A" if self.ui_theme == "angel" else "#202020",
            "selection": "#F2A1BE" if self.ui_theme == "angel" else "#0078D7",
            "selection_fg": "#2D1720" if self.ui_theme == "angel" else "#FFFFFF",
        }, self.ui_theme == "angel")

    # ------------------------------------------------------ health / about --
    def run_config_health_check(self):
        issues = []
        checked = []

        def duplicate_keys(text, label):
            seen = {}
            for line_no, raw in enumerate(text.replace("\r\n", "\n").split("\n"), start=1):
                stripped = raw.strip()
                if not stripped or stripped.startswith(("#", ";", "[")) or "=" not in raw:
                    continue
                key = raw.split("=", 1)[0].strip()
                seen.setdefault(key, []).append(line_no)
            for key, lines in seen.items():
                if len(lines) > 1:
                    issues.append(f"{label}: duplicate key {key} on lines {', '.join(map(str, lines))}")

        if self.loaded_path:
            checked.append("Game.ini")
            duplicate_keys(self.original_text, "Game.ini")
            for key in self.color_rows:
                raw = self.values.get(key)
                if raw is not None and not RGBA_RE.fullmatch(raw.strip()):
                    issues.append(f"Game.ini: {key} is not a valid RGBA value")
            for key in self.volume_vars:
                raw = self.values.get(key)
                if raw is None:
                    continue
                try:
                    n = float(raw)
                    if not 0.0 <= n <= 1.0:
                        issues.append(f"Game.ini: {key} is outside 0.0 - 1.0 ({raw})")
                except Exception:
                    issues.append(f"Game.ini: {key} is not numeric ({raw})")
            for key, var in self.vars.items():
                raw = self.values.get(key)
                if raw is None:
                    continue
                if isinstance(var, tk.BooleanVar) and raw.lower() not in {"true", "false"}:
                    issues.append(f"Game.ini: {key} should be True or False ({raw})")
                if key in FLOAT_KEYS:
                    try:
                        float(raw)
                    except Exception:
                        issues.append(f"Game.ini: {key} is not numeric ({raw})")
                if key in INT_KEYS:
                    try:
                        int(float(raw))
                    except Exception:
                        issues.append(f"Game.ini: {key} is not a whole-number setting ({raw})")

        if self.loaded_user_settings_path:
            checked.append("GameUserSettings.ini")
            duplicate_keys(self.user_settings_original_text, "GameUserSettings.ini")
            for key, var in self.gus_vars.items():
                raw = self.user_settings_values.get(key)
                if raw is None:
                    continue
                if isinstance(var, tk.BooleanVar) and raw.lower() not in {"true", "false"}:
                    issues.append(f"GameUserSettings.ini: {key} should be True or False ({raw})")
            for key in ["ResolutionSizeX", "ResolutionSizeY"]:
                raw = self.user_settings_values.get(key)
                if raw is not None:
                    try:
                        if int(float(raw)) <= 0:
                            issues.append(f"GameUserSettings.ini: {key} must be positive ({raw})")
                    except Exception:
                        issues.append(f"GameUserSettings.ini: {key} is not numeric ({raw})")

        if not checked:
            messagebox.showinfo(APP_NAME, "Load the config files before running the health check.")
            return

        if issues:
            summary = f"{len(issues)} potential issue(s) found."
            body = summary + "\n\n" + "\n".join(f"- {x}" for x in issues)
        else:
            summary = "No obvious config problems found."
            body = (
                summary
                + "\n\nChecked for duplicate keys, invalid known RGBA values, "
                  "invalid booleans, volume ranges, and basic numeric formatting.\n\n"
                  "This is a consistency check, not a guarantee that every Tower Unite setting is valid."
            )
        self.health_summary_var.set(summary)
        self.dashboard_health.set("Health: " + summary)
        self._show_text_window("Config Health Check", body)

    def show_about(self):
        text = (
            f"AngelTune v{APP_VERSION} ♡\n\n"
            "The original AngelTune - made by Angel.\n"
            "Cute on the outside, suspiciously organized on the inside. :3\n\n"
            "AngelTune is my unofficial little Tower Unite config gremlin - built "
            "to make tweaking Game.ini and GameUserSettings.ini easier, prettier, "
            "and a lot less annoying.\n\n"
            "It focuses on readable, reversible changes to known config values. "
            "No injection, no executable patching, no game-package modifications - "
            "just configs, backups, and a tiny bit of pink chaos. ♡\n\n"
            "Stuff packed inside:\n"
            "- presets and Share Packs\n"
            "- automatic + manual backups\n"
            "- Text Hat tools and randomizer\n"
            "- colors, sound helpers, and quick actions\n"
            "- favorites and improved search\n"
            "- quest progress tracking\n"
            "- change previews, undo, and config health checks\n\n"
            "Made with love, pink pixels, and probably too many little buttons.\n"
            "If something looks extra cute, that was absolutely intentional. ♡\n\n"
            "Want to say hi or stalk the original little menace behind this thing?\n"
            "Steam custom URL: AngelNeedsSupervision\n"
            "Come say hi if you want - I do not bite... probably. ♡\n\n"
            "Theme: Angel\n"
            "Creator: Angel\n"
            "Status: officially unofficial\n"
            "Original: yep, this is the one ♡\n\n"
            "AngelTune is not affiliated with PixelTail Games, Valve, or Steam."
        )
        self._show_text_window("About AngelTune ♡", text, width=82, height=27)

    def _build_display_tab(self):
        tab = self.create_scrollable_tab("Display")

        res = self.section(tab, "Resolution", 0)
        ttk.Label(res, text="Preset").grid(row=0, column=0, sticky="w", pady=4)
        preset = ttk.Combobox(
            res,
            textvariable=self.resolution_preset,
            values=COMMON_RESOLUTIONS,
            state="normal",
            width=24,
        )
        preset.grid(row=0, column=1, sticky="w", pady=4)
        preset.bind("<<ComboboxSelected>>", self._apply_resolution_preset)
        preset.bind("<Return>", self._apply_resolution_preset)
        ttk.Button(res, text="Apply preset", command=self._apply_resolution_preset).grid(
            row=0, column=2, padx=(8, 0)
        )
        self.register_search("Resolution preset", "GameUserSettings:ResolutionSizeX/Y", preset)

        self.gus_spin_control(res, 1, "Resolution width", "ResolutionSizeX", 640, 7680, 1)
        self.gus_spin_control(res, 2, "Resolution height", "ResolutionSizeY", 480, 4320, 1)
        self.gus_spin_control(res, 3, "Monitor index", "MonitorIndex", 0, 15, 1)

        ttk.Label(res, text="Display mode").grid(row=4, column=0, sticky="w", pady=4)
        mode_combo = ttk.Combobox(
            res,
            textvariable=self.display_mode,
            values=list(DISPLAY_MODE_LABELS),
            state="readonly",
            width=24,
        )
        mode_combo.grid(row=4, column=1, sticky="w", pady=4)
        self.register_search("Display mode", "GameUserSettings:FullscreenMode", mode_combo)

        display = self.section(tab, "Display options", 1)
        self.gus_bool_control(display, 0, "VSync", "bUseVSync")
        self.gus_bool_control(display, 1, "Dynamic resolution", "bUseDynamicResolution")
        self.gus_bool_control(display, 2, "HDR output", "bUseHDRDisplayOutput")
        self.gus_spin_control(display, 3, "HDR output nits", "HDRDisplayOutputNits", 100, 4000, 50)

        quality = self.section(tab, "Scalability", 2)
        self.gus_spin_control(quality, 0, "Resolution quality (%)", "sg.ResolutionQuality", 25, 200, 1)
        self.gus_spin_control(quality, 1, "View distance quality", "sg.ViewDistanceQuality", 0, 4, 1)
        self.gus_spin_control(quality, 2, "Anti-aliasing quality", "sg.AntiAliasingQuality", 0, 4, 1)
        self.gus_spin_control(quality, 3, "Shadow quality", "sg.ShadowQuality", 0, 4, 1)
        self.gus_spin_control(quality, 4, "Post-process quality", "sg.PostProcessQuality", 0, 4, 1)
        self.gus_spin_control(quality, 5, "Texture quality", "sg.TextureQuality", 0, 4, 1)
        self.gus_spin_control(quality, 6, "Effects quality", "sg.EffectsQuality", 0, 4, 1)
        self.gus_spin_control(quality, 7, "Foliage quality", "sg.FoliageQuality", 0, 4, 1)

        info = self.section(tab, "Current saved confirmation values (read-only)", 3)
        self.gus_info_labels = {}
        for i, key in enumerate([
            "LastUserConfirmedResolutionSizeX",
            "LastUserConfirmedResolutionSizeY",
            "LastConfirmedFullscreenMode",
            "PreferredFullscreenMode",
            "DesiredScreenWidth",
            "DesiredScreenHeight",
        ]):
            ttk.Label(info, text=key).grid(row=i, column=0, sticky="w", padx=(0, 10), pady=3)
            var = tk.StringVar(value="—")
            self.gus_info_labels[key] = var
            ent = ttk.Entry(info, textvariable=var, state="readonly")
            ent.grid(row=i, column=1, sticky="ew", pady=3)
            self.register_search(key, f"GameUserSettings:{key}", ent)
        info.columnconfigure(1, weight=1)

    # --------------------------------------------------------------- tabs --
    def _build_home_tab(self):
        tab = self.create_scrollable_tab("Home")

        hero = ttk.Frame(tab, padding=(18, 16))
        hero.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        hero.columnconfigure(1, weight=1)

        try:
            icon_path = resource_path("assets", "angeltune_icon.png")
            if icon_path.exists():
                self.home_logo_image = tk.PhotoImage(file=str(icon_path)).subsample(4, 4)
                ttk.Label(hero, image=self.home_logo_image).grid(
                    row=0, column=0, rowspan=2, padx=(0, 14), sticky="w"
                )
        except Exception:
            pass

        ttk.Label(
            hero,
            text="AngelTune",
            style="Hero.TLabel",
        ).grid(row=0, column=1, sticky="sw")
        ttk.Label(
            hero,
            text="Cute little control panel for your Tower Unite configs ♡",
            style="HeroSub.TLabel",
        ).grid(row=1, column=1, sticky="nw")

        dash = self.section(tab, "Dashboard", 1)
        dash.columnconfigure(0, weight=1)
        dash.columnconfigure(1, weight=1)
        for i, var in enumerate([
            self.dashboard_config,
            self.dashboard_hud,
            self.dashboard_resolution,
            self.dashboard_text_hat,
            self.dashboard_backup,
            self.dashboard_health,
        ]):
            ttk.Label(dash, textvariable=var).grid(
                row=i // 2, column=i % 2, sticky="w", padx=(0, 18), pady=4
            )

        quick = self.section(tab, "Quick actions", 2)
        actions = [
            ("Reload configs", self.load_files),
            ("Preview changes", self.show_changes_preview),
            ("Save changes", self.save_changes),
            ("Undo since load", self.undo_since_load),
            ("Reset current tab", self.reset_current_tab),
            ("Create backup", self.create_manual_backup),
            ("Config health check", self.run_config_health_check),
            ("Randomize Text Hat", self.randomize_text_hat_now),
            ("Open config folder", self.open_folder),
            ("About AngelTune", self.show_about),
        ]
        for i, (label, command) in enumerate(actions):
            ttk.Button(
                quick,
                text=label,
                command=command,
                style="Accent.TButton" if label == "Save changes" else "TButton",
            ).grid(
                row=i // 5,
                column=i % 5,
                padx=(0 if i % 5 == 0 else 8, 0),
                pady=(0 if i < 5 else 8, 0),
                sticky="ew",
            )
            quick.columnconfigure(i % 5, weight=1)

        safety = self.section(tab, "Safe scope", 3)
        ttk.Label(
            safety,
            text=(
                "AngelTune edits known values in Game.ini and GameUserSettings.ini only. "
                "It does not inject into Tower Unite or modify game executables. "
                "Automatic backups are created before writes."
            ),
            wraplength=900,
            justify="left",
        ).grid(row=0, column=0, sticky="w")

    def _build_favorites_tab(self):
        tab = self.create_scrollable_tab("Favs")

        box = self.section(tab, "Favorite settings", 0)
        box.columnconfigure(0, weight=1)
        ttk.Label(
            box,
            text=(
                "Keep shortcuts to settings you use often. Favorites are stored in "
                "AngelTune's own settings file and do not touch Tower Unite."
            ),
            foreground="#666",
            wraplength=850,
            justify="left",
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        self.favorite_option_combo = ttk.Combobox(
            box,
            textvariable=self.favorite_option_var,
            state="readonly",
        )
        self.favorite_option_combo.grid(row=1, column=0, sticky="ew")
        ttk.Button(box, text="Add", command=self.add_favorite_from_combo).grid(
            row=1, column=1, padx=(8, 0)
        )
        ttk.Button(box, text="Remove", command=self.remove_selected_favorite).grid(
            row=1, column=2, padx=(8, 0)
        )
        ttk.Button(box, text="Go", command=self.go_to_selected_favorite).grid(
            row=1, column=3, padx=(8, 0)
        )

        self.favorites_list = tk.Listbox(
            box,
            height=14,
            exportselection=False,
        )
        self.favorites_list.grid(
            row=2, column=0, columnspan=4, sticky="ew", pady=(8, 0)
        )
        self.favorites_list.bind(
            "<Double-Button-1>", lambda _e: self.go_to_selected_favorite()
        )

    def _build_backup_tools_tab(self):
        tab = self.create_scrollable_tab("Backups")

        backup = self.section(tab, "Backup history", 0)
        backup.columnconfigure(0, weight=1)
        ttk.Label(
            backup,
            text=(
                "Select a backup to restore that exact file. AngelTune creates a "
                "before_restore backup first."
            ),
            foreground="#666",
            wraplength=860,
            justify="left",
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))

        columns = ("file", "kind", "time", "size")
        self.backup_tree = ttk.Treeview(
            backup,
            columns=columns,
            show="headings",
            height=12,
            selectmode="browse",
        )
        self.backup_tree.heading("file", text="Backup file")
        self.backup_tree.heading("kind", text="Type")
        self.backup_tree.heading("time", text="Modified")
        self.backup_tree.heading("size", text="Size")
        self.backup_tree.column("file", width=430, anchor="w")
        self.backup_tree.column("kind", width=110, anchor="w")
        self.backup_tree.column("time", width=150, anchor="w")
        self.backup_tree.column("size", width=90, anchor="e")
        self.backup_tree.grid(row=1, column=0, columnspan=4, sticky="ew")

        ttk.Button(
            backup, text="Refresh", command=self.refresh_backup_history
        ).grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Button(
            backup, text="Restore selected", command=self.restore_selected_backup
        ).grid(row=2, column=1, sticky="w", padx=(8, 0), pady=(8, 0))
        ttk.Button(
            backup, text="Create backup now", command=self.create_manual_backup
        ).grid(row=2, column=2, sticky="w", padx=(8, 0), pady=(8, 0))
        ttk.Button(
            backup, text="Open backup folder", command=self.open_backup_folder
        ).grid(row=2, column=3, sticky="w", padx=(8, 0), pady=(8, 0))

        health = self.section(tab, "Config health check", 1)
        self.health_summary_var = tk.StringVar(value="Not checked yet.")
        ttk.Label(
            health,
            textvariable=self.health_summary_var,
            wraplength=820,
            justify="left",
        ).grid(row=0, column=0, sticky="w")
        ttk.Button(
            health,
            text="Run health check",
            command=self.run_config_health_check,
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

    def _save_tool_settings(self):
        data = dict(self.app_settings)
        data["favorites"] = sorted(self.favorite_ids)
        data["color_presets"] = dict(self.custom_color_presets)
        data["text_hat_random_pool"] = sorted(self.text_hat_random_pool)
        self.app_settings = data
        save_app_settings(data)

    def _favorite_id(self, rec):
        return rec.get("display", "")

    def _refresh_favorites_ui(self):
        records = getattr(self, "search_records", [])
        displays = [rec["display"] for rec in records]
        if hasattr(self, "favorite_option_combo"):
            self.favorite_option_combo["values"] = displays
            if self.favorite_option_var.get() not in displays:
                self.favorite_option_var.set(displays[0] if displays else "")

        if hasattr(self, "favorites_list"):
            self.favorites_list.delete(0, tk.END)
            valid = set(displays)
            self.favorite_ids.intersection_update(valid)
            for display in displays:
                if display in self.favorite_ids:
                    self.favorites_list.insert(tk.END, display)

    def add_favorite_from_combo(self):
        display = self.favorite_option_var.get().strip()
        if not display:
            return
        self.favorite_ids.add(display)
        self._save_tool_settings()
        self._refresh_favorites_ui()
        self.status.set(f'Added favorite: {display}')

    def favorite_current_search(self):
        query = self.search_var.get().strip().lower()
        rec = None
        for item in self.search_records:
            if query and query in {
                item["display"].lower(),
                item["label"].lower(),
                item["key"].lower(),
            }:
                rec = item
                break
        if rec is None:
            matches = getattr(self, "filtered_search_records", [])
            if matches:
                rec = matches[0]
        if rec is None:
            self.status.set("Search for a setting first, then add it as a favorite.")
            return
        self.favorite_ids.add(rec["display"])
        self._save_tool_settings()
        self._refresh_favorites_ui()
        self.status.set(f'Added favorite: {rec["label"]}')

    def remove_selected_favorite(self):
        if not hasattr(self, "favorites_list"):
            return
        selection = self.favorites_list.curselection()
        if not selection:
            return
        display = self.favorites_list.get(selection[0])
        self.favorite_ids.discard(display)
        self._save_tool_settings()
        self._refresh_favorites_ui()
        self.status.set(f'Removed favorite: {display}')

    def go_to_selected_favorite(self):
        display = ""
        if hasattr(self, "favorites_list"):
            selection = self.favorites_list.curselection()
            if selection:
                display = self.favorites_list.get(selection[0])
        if not display:
            display = self.favorite_option_var.get().strip()
        if not display:
            return
        self.search_var.set(display)
        self.jump_to_search()

    def clear_search(self):
        self.search_var.set("")
        self.filtered_search_records = []
        if hasattr(self, "search_suggestions"):
            self.search_suggestions.delete(0, tk.END)
        if hasattr(self, "search_suggestion_frame"):
            self.search_suggestion_frame.grid_remove()
        self.search_box.focus_set()

    def _refresh_search_filter_values(self):
        tabs = ["All tabs"] + list(self.tab_infos.keys())
        if hasattr(self, "search_filter_combo"):
            self.search_filter_combo["values"] = tabs
        if self.search_tab_filter.get() not in tabs:
            self.search_tab_filter.set("All tabs")

    def update_dashboard(self):
        loaded = []
        if self.loaded_path:
            loaded.append("Game.ini")
        if self.loaded_user_settings_path:
            loaded.append("GameUserSettings.ini")
        self.dashboard_config.set(
            "Configs: " + (" + ".join(loaded) if loaded else "not loaded")
        )
        self.dashboard_hud.set(f"HUD: {self.hud_style.get()}")
        try:
            x = str(self.gus_vars.get("ResolutionSizeX").get())
            y = str(self.gus_vars.get("ResolutionSizeY").get())
            self.dashboard_resolution.set(f"Resolution: {x} x {y}")
        except Exception:
            self.dashboard_resolution.set("Resolution: -")
        try:
            text = str(self.vars.get("Item.TextHatText").get())
            shown = text if len(text) <= 34 else text[:31] + "..."
            self.dashboard_text_hat.set(f'Text Hat: "{shown}"')
        except Exception:
            self.dashboard_text_hat.set("Text Hat: -")

        backups = self._all_backup_files()
        if backups:
            latest = max(backups, key=lambda x: x.stat().st_mtime)
            stamp = datetime.fromtimestamp(latest.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            self.dashboard_backup.set(f"Latest backup: {stamp}")
        else:
            self.dashboard_backup.set("Latest backup: none")

    def _all_backup_files(self):
        parents = set()
        for candidate in [self.loaded_path, self.loaded_user_settings_path]:
            if candidate:
                try:
                    parents.add(Path(candidate).parent)
                except Exception:
                    pass
        if not parents:
            parents.add(DEFAULT_PATH.parent)

        found = {}
        for parent in parents:
            for folder in [parent / BACKUP_FOLDER_NAME, parent / LEGACY_BACKUP_FOLDER_NAME, parent]:
                if not folder.exists():
                    continue
                for pattern in ["*.angeltune.*.bak", "*.tuctool.*.bak"]:
                    for item in folder.glob(pattern):
                        try:
                            found[str(item.resolve())] = item
                        except Exception:
                            found[str(item)] = item
        return list(found.values())

    def refresh_backup_history(self):
        if not hasattr(self, "backup_tree"):
            return
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)
        self.backup_history_paths = {}

        backups = sorted(
            self._all_backup_files(),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for i, path in enumerate(backups):
            name = path.name
            kind = "backup"
            m = re.search(r"\.(?:angeltune|tuctool)\.([^.]+)\.", name)
            if m:
                kind = m.group(1).replace("_", " ")
            elif ".original.bak" in name:
                kind = "original"
            stamp = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            size = path.stat().st_size
            shown_size = f"{size / 1024:.1f} KB"
            iid = f"backup_{i}"
            self.backup_tree.insert(
                "", "end", iid=iid,
                values=(name, kind, stamp, shown_size),
            )
            self.backup_history_paths[iid] = path
        self.update_dashboard()

    def restore_selected_backup(self):
        if not hasattr(self, "backup_tree"):
            return
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showinfo(APP_NAME, "Select a backup first.")
            return
        backup = self.backup_history_paths.get(selection[0])
        if not backup or not backup.exists():
            messagebox.showerror(APP_NAME, "The selected backup no longer exists.")
            self.refresh_backup_history()
            return
        if is_tower_running():
            messagebox.showwarning(APP_NAME, "Close Tower Unite before restoring a backup.")
            return

        if backup.name.startswith("GameUserSettings.ini"):
            target = self.loaded_user_settings_path or Path(self.user_settings_path.get()).expanduser()
        elif backup.name.startswith("Game.ini"):
            target = self.loaded_path or Path(self.path.get()).expanduser()
        else:
            messagebox.showerror(APP_NAME, "Could not determine which config this backup belongs to.")
            return

        if not messagebox.askyesno(
            APP_NAME,
            f"Restore this backup?\n\n{backup.name}\n\nTarget: {target.name}"
        ):
            return
        try:
            if target.exists():
                self._make_backup_for_path(target, "before_restore")
            shutil.copy2(backup, target)
            self.load_files()
            self.refresh_backup_history()
            self.status.set(f"Restored {backup.name}.")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Restore failed:\n{e}")

    def _build_hud_tab(self):
        tab = self.create_scrollable_tab("HUD")

        box = self.section(tab, "HUD style", 0)
        box.columnconfigure(1, weight=1)
        box.columnconfigure(2, weight=1)

        ttk.Label(box, text="Unit HUD style").grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        self.hud_style = tk.StringVar(value="Cute")
        hud_combo = ttk.Combobox(
            box,
            state="readonly",
            values=list(HUD_STYLES),
            textvariable=self.hud_style,
            width=22,
        )
        hud_combo.grid(row=0, column=1, sticky="w")
        hud_combo.bind("<<ComboboxSelected>>", self._update_hud_preview)
        self.register_search("Unit HUD style", "HUD.Mode", hud_combo)

        ttk.Label(
            box,
            text="Known mappings from your current Tower Unite build.",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

        ttk.Label(
            box,
            text="Preview",
            font=("TkDefaultFont", 9, "bold"),
        ).grid(row=0, column=2, sticky="w", padx=(18, 0))

        self.hud_preview = tk.Canvas(
            box,
            width=320,
            height=180,
            highlightthickness=1,
            highlightbackground="#777",
            bg="#151823",
        )
        self.hud_preview.grid(
            row=1,
            column=2,
            rowspan=3,
            sticky="e",
            padx=(18, 0),
            pady=(5, 0),
        )

        ttk.Label(
            box,
            text="In-game screenshot preview of the selected Unit HUD style.",
            foreground="#666",
            wraplength=320,
            justify="left",
        ).grid(row=4, column=2, sticky="w", padx=(18, 0), pady=(4, 0))

        self._update_hud_preview()

        colors = self.section(tab, "Colors", 1)
        ttk.Button(
            colors,
            text="Use game defaults for all colors",
            command=self.reset_all_colors_to_game_default,
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        ttk.Label(
            colors,
            text="Game default removes the saved override; Tower Unite chooses its built-in color next time it loads.",
            foreground="#666",
            wraplength=760,
            justify="left",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))

        color_preset_frame = ttk.Frame(colors)
        color_preset_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(2, 8))
        ttk.Label(color_preset_frame, text="Color preset").pack(side="left")
        self.color_preset_combo = ttk.Combobox(
            color_preset_frame,
            textvariable=self.color_preset_var,
            state="readonly",
            width=20,
        )
        self.color_preset_combo.pack(side="left", padx=(8, 0))
        ttk.Button(
            color_preset_frame,
            text="Apply to Inventory + Key Prompt",
            command=lambda: self.apply_color_preset("hud_pair"),
        ).pack(side="left", padx=(8, 0))
        ttk.Button(
            color_preset_frame,
            text="Apply to all colors",
            command=lambda: self.apply_color_preset("all"),
        ).pack(side="left", padx=(8, 0))
        ttk.Button(
            color_preset_frame,
            text="Save Inventory color…",
            command=self.save_custom_color_preset,
        ).pack(side="left", padx=(8, 0))

        for i, (label, key) in enumerate(COLOR_KEYS.items(), start=3):
            row = ColorRow(colors, label, key)
            row.grid(
                row=i, column=0, columnspan=2, sticky="ew", pady=4
            )
            self.color_rows[key] = row
            self.register_search(label, key, row.frame)

        inventory_row = self.color_rows.get("Inventory.Color")
        key_prompt_row = self.color_rows.get("HUD.KeyPrompt.Color")
        if inventory_row is not None and key_prompt_row is not None:
            inventory_row.set_on_change(self._hud_main_color_changed)
            key_prompt_row.set_on_change(self._hud_main_color_changed)

        link_row = ttk.Frame(colors)
        link_row.grid(
            row=4 + len(COLOR_KEYS),
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(10, 2),
        )
        ttk.Checkbutton(
            link_row,
            text="Link Inventory + Key Prompt colors",
            variable=self.link_hud_main_colors,
            command=self._toggle_hud_main_color_link,
        ).pack(side="left")

        ttk.Button(
            link_row,
            text="Sync now",
            command=self._sync_inventory_to_key_prompt,
        ).pack(side="left", padx=(10, 0))

        ttk.Label(
            colors,
            text=(
                "When linked, changing either Inventory Color or Key Prompt Color "
                "also changes the other one, including HEX, Alpha and Game Default."
            ),
            foreground="#666",
            wraplength=780,
            justify="left",
        ).grid(
            row=3 + len(COLOR_KEYS),
            column=0,
            columnspan=2,
            sticky="w",
            pady=(2, 0),
        )

        options = self.section(tab, "HUD options", 2)
        self.bool_control(
            options, 0, "Enable HUD", "Gameplay.EnableHUD"
        )
        self.bool_control(
            options, 1, "Always show player names",
            "HUD.PlayerNames.AlwaysShow"
        )
        self.bool_control(
            options, 2, "Show my own name tag",
            "HUD.PlayerNames.ShowNameTagOnSelf"
        )
        self.bool_control(
            options, 3, "Hide player names behind walls",
            "HUD.PlayerNames.HideBehindWalls"
        )
        self.bool_control(
            options, 4, "Floating chat", "HUD.EnableFloatingChat"
        )
        self.bool_control(
            options, 5, "Key prompt flash", "HUD.KeyPrompt.Flash"
        )
        self.spin_control(
            options, 6, "UI scale", "Graphics.UIScale",
            0.50, 2.00, 0.05
        )

    def _toggle_hud_main_color_link(self):
        if self.link_hud_main_colors.get():
            self._sync_inventory_to_key_prompt()
            self.status.set(
                "Inventory Color and Key Prompt Color are linked."
            )
        else:
            self.status.set(
                "Inventory Color and Key Prompt Color are no longer linked."
            )

    def _sync_inventory_to_key_prompt(self):
        source = self.color_rows.get("Inventory.Color")
        target = self.color_rows.get("HUD.KeyPrompt.Color")
        if source is None or target is None:
            return

        self._syncing_hud_main_colors = True
        try:
            target.copy_state_from(source)
        finally:
            self._syncing_hud_main_colors = False

        self.status.set(
            "Key Prompt Color matched to Inventory Color."
        )

    def _hud_main_color_changed(self, source_row):
        if not self.link_hud_main_colors.get():
            return
        if self._syncing_hud_main_colors:
            return

        if source_row.key == "Inventory.Color":
            target = self.color_rows.get("HUD.KeyPrompt.Color")
        elif source_row.key == "HUD.KeyPrompt.Color":
            target = self.color_rows.get("Inventory.Color")
        else:
            return

        if target is None:
            return

        self._syncing_hud_main_colors = True
        try:
            target.copy_state_from(source_row)
        finally:
            self._syncing_hud_main_colors = False

        self.status.set(
            "Linked HUD colors updated together."
        )

    def _update_hud_preview(self, _event=None):
        if not hasattr(self, "hud_preview"):
            return

        c = self.hud_preview
        c.delete("all")
        style = self.hud_style.get()

        filename = HUD_PREVIEW_FILES.get(style)
        if filename:
            image_path = resource_path("assets", filename)
            if image_path.exists():
                try:
                    self.hud_preview_image = tk.PhotoImage(file=str(image_path))
                    c.create_image(0, 0, image=self.hud_preview_image, anchor="nw")
                    return
                except Exception:
                    # Fall through to the local schematic fallback below.
                    self.hud_preview_image = None

        # Fallback if an asset is missing or cannot be loaded.
        w = 320
        h = 180
        c.create_rectangle(0, 0, w, h, fill="#111521", outline="")
        c.create_rectangle(0, 112, w, h, fill="#1A2030", outline="")
        c.create_polygon(
            0, 112, 88, 72, 156, 102, 226, 54, 320, 96, 320, 180, 0, 180,
            fill="#20283A",
            outline="",
        )
        c.create_text(
            160, 78,
            text=f"{style or 'HUD'} preview unavailable",
            fill="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
        )
        c.create_text(
            160, 103,
            text="Screenshot asset not found",
            fill="#AEB5C9",
            font=("Segoe UI", 9),
        )

    def _build_general_tab(self):
        tab = self.create_scrollable_tab("General")

        gameplay = self.section(tab, "Gameplay", 0)
        general_toggles = [
            ("Show first-person legs", "General.FirstPersonLegs"),
            ("Enable Steam Rich Presence", "General.EnableRichPresence"),
            ("Enable player ghosts", "Lobby.EnablePlayerGhosts"),
            ("Enable crosshair", "Gameplay.EnableCrosshair"),
            ("Enable casino history", "Gameplay.EnableCasinoHistory"),
            ("Enable key prompts", "Gameplay.EnableKeyPrompts"),
            ("Enable vomit effects", "Gameplay.EnableVomit"),
            ("Enable weapon scopes", "Gameplay.EnableWeaponScopes"),
            ("Arachnophobia mode", "Gameplay.ArachnophobiaMode"),
            ("Zoom mode toggle", "Gameplay.ZoomModeToggle"),
            ("Leave Me Alone mode", "Lobby.LeaveMeAlone"),
            ("Fishing minigame opaque mode", "Fishing.Minigame.OpaqueMode"),
        ]
        for i, (label, key) in enumerate(general_toggles):
            self.bool_control(gameplay, i, label, key)
        self.spin_control(
            gameplay,
            len(general_toggles),
            "Mouse sensitivity",
            "Gameplay.MouseSensitivity",
            0.001,
            1.0,
            0.001,
        )

        dialogue = self.section(tab, "Dialogue & Voice behavior", 1)
        self.bool_control(
            dialogue, 0, "Nearby NPC greets", "Dialogue.EnableNearbyGreets"
        )
        self.bool_control(
            dialogue, 1, "Event dialogue", "Dialogue.EnableEventDialogue"
        )
        self.bool_control(
            dialogue, 2, "Voice occlusion", "Voice.EnableOcclusion"
        )

        first_person = self.section(tab, "First person & wearables", 2)
        self.bool_control(
            first_person, 0, "Draw wearables in first person", "Wearable.DrawFirstPerson"
        )
        self.bool_control(
            first_person, 1, "Draw pets in first person", "Wearable.DrawPetsFirstPerson"
        )

        menu = self.section(tab, "Menu & Inventory", 3)
        self.bool_control(
            menu, 0, "Quick Access menu", "Menu.QuickAccessEnabled"
        )
        self.bool_control(
            menu, 1, "Toggle Inventory behavior", "Menu.ToggleInventory"
        )
        self.bool_control(
            menu, 2, "Toggle Scoreboard behavior", "Menu.ToggleScoreboard"
        )
        self.bool_control(
            menu, 3, "New Inventory prompt", "Inventory.NewInventoryPrompt"
        )
        self.bool_control(
            menu, 4, "Show Inventory titles", "Inventory.ShowTitles"
        )
        self.bool_control(
            menu, 5, "Show HUD leaderboards", "HUD.ShowLeaderboards"
        )
        self.bool_control(
            menu, 6, "Show HUD awards", "HUD.ShowAwards"
        )

        controls = self.section(tab, "Controller & Vehicle controls", 4)
        self.bool_control(
            controls, 0, "Invert plane Y axis", "Controls.Vehicle.Plane.InvertY"
        )
        self.bool_control(
            controls, 1, "Toggle vehicle acceleration", "Controls.Vehicle.ToggleAcceleration"
        )
        self.bool_control(
            controls, 2, "Invert gamepad aim", "Gamepad.InvertAim"
        )
        self.bool_control(
            controls, 3, "Gamepad rumble", "Gamepad.RumbleEnabled"
        )
        self.spin_control(
            controls, 4, "Gamepad sensitivity", "Gamepad.Sensitivity", 0.0, 1.0, 0.01
        )

        libretro = self.section(tab, "Libretro", 5)
        self.bool_control(
            libretro, 0, "Auto Save State", "Libretro.AutoSaveState"
        )
        self.spin_control(
            libretro,
            1,
            "Resolution scale (raw value)",
            "Libretro.ResolutionScale",
            0,
            8,
            1,
        )
        ttk.Label(
            libretro,
            text="Raw values are shown exactly as stored by Tower Unite; the tool does not invent enum labels.",
            foreground="#666",
            wraplength=760,
            justify="left",
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))

    def _build_graphics_tab(self):
        tab = self.create_scrollable_tab("Graphics")

        gfx = self.section(tab, "Resolution & rendering", 0)
        self.spin_control(gfx, 0, "FOV", "Graphics.FOV", 60, 140, 1)
        self.spin_control(
            gfx, 1, "Gamma", "Graphics.Gamma", 1.0, 4.0, 0.05
        )
        self.spin_control(
            gfx, 2, "Resolution scale (%)",
            "Graphics.ResolutionScale", 25, 200, 1
        )
        self.spin_control(
            gfx, 3, "Media resolution",
            "Graphics.MediaResolution", 240, 4320, 120
        )
        self.spin_control(
            gfx, 4, "Mirror resolution",
            "Graphics.MirrorResolution", 0.10, 2.00, 0.05
        )
        self.spin_control(
            gfx, 5, "Anti-aliasing mode (raw value)",
            "Settings.AAMode", 0, 4, 1
        )
        self.spin_control(
            gfx, 6, "Ocean quality (raw value)",
            "Graphics.OceanQuality", 0, 4, 1
        )
        self.spin_control(
            gfx, 7, "High quality shaders",
            "Graphics.HighQualityShaders", 0, 2, 1
        )
        self.spin_control(
            gfx, 8, "High quality shaders 2 (raw value)",
            "Graphics.HighQualityShaders2", 0, 4, 1
        )
        self.spin_control(
            gfx, 9, "Icon scale (raw value)",
            "Graphics.IconScale", 0, 4, 1
        )
        self.spin_control(
            gfx, 10, "Water simulation (raw value)",
            "Graphics.WaterSimulation", 0, 4, 1
        )

        visual = self.section(tab, "Visual effects", 1)
        self.bool_control(
            visual, 0, "Display FPS", "Graphics.DisplayFPS"
        )
        self.bool_control(
            visual, 1, "Weather particles",
            "Graphics.EnableWeatherParticles"
        )
        self.bool_control(
            visual, 2, "Weather scenery",
            "Graphics.EnableWeatherScenery"
        )
        self.bool_control(
            visual, 3, "Media dynamic lights",
            "Graphics.ShowMediaDynamicLights"
        )
        self.bool_control(
            visual, 4, "Ambient occlusion", "Graphics.AOEnabled"
        )
        self.bool_control(
            visual, 5, "Decals", "Graphics.DecalsEnabled"
        )
        self.bool_control(
            visual, 6, "Gun flash", "Graphics.GunFlashEnabled"
        )
        self.bool_control(
            visual, 7, "Placeable dynamic lights",
            "Graphics.PlaceableDynamicLights"
        )
        self.bool_control(
            visual, 8, "Color-blind mode", "General.ColorBlindMode"
        )
        self.bool_control(
            visual, 9, "Enable player fade", "Lobby.EnablePlayerFade"
        )
        self.spin_control(
            visual, 10, "Player fade amount",
            "Lobby.PlayerFadeAmount", 0.0, 1.0, 0.05
        )
        self.spin_control(
            visual, 11, "Nightclub brightness",
            "Nightclub.Brightness", 0.0, 2.0, 0.05
        )

        cam = self.section(tab, "Camera", 2)
        self.spin_control(
            cam, 0, "View bob", "Camera.ViewBob", 0.0, 2.0, 0.05
        )
        self.bool_control(
            cam, 1, "View bob in Plaza", "Camera.ViewBobPlaza"
        )

    def _build_sound_tab(self):
        tab = self.create_scrollable_tab("Sound")

        volumes = self.section(tab, "Volumes", 0)
        volumes.columnconfigure(1, weight=1)
        for i, (label, key) in enumerate(VOLUME_KEYS):
            self.volume_control(volumes, i, label, key)

        groups = self.section(tab, "Sound groups", 1)
        ttk.Label(
            groups,
            text="Quickly adjust related volume sliders together.",
            foreground="#666",
        ).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 6))
        sound_buttons = [
            ("All 100%", "all100"),
            ("All 50%", "all50"),
            ("Mute all", "mute"),
            ("Mute music + media", "media_off"),
            ("Mute voice", "voice_off"),
            ("Restore loaded", "restore"),
        ]
        for i, (label, mode) in enumerate(sound_buttons):
            ttk.Button(
                groups,
                text=label,
                command=lambda m=mode: self.apply_sound_group(m),
            ).grid(row=1, column=i, padx=(0 if i == 0 else 8, 0), sticky="w")

        toggles = self.section(tab, "Sound & voice options", 2)
        sound_toggles = [
            ("Enable voice chat", "Gameplay.EnableVoiceChat"),
            ("Enable chat sounds", "Gameplay.EnableChatSounds"),
            ("Enable Unit effects", "Gameplay.EnableUnitEffects"),
            ("Enable Unit effect sounds", "Gameplay.EnableUnitEffectSounds"),
            (
                "Enable achievement unlock sound",
                "Gameplay.EnableAchievementUnlockSound",
            ),
            ("Enable Workshop sound packs", "Workshop.EnableSoundPacks"),
            (
                "Workshop sound packs: friends only",
                "Workshop.EnableSoundPacksFriendsOnly",
            ),
            ("Allow media volume toggle", "Media.AllowVolumeToggle"),
        ]
        for i, (label, key) in enumerate(sound_toggles):
            self.bool_control(toggles, i, label, key)

    def _build_items_tab(self):
        tab = self.create_scrollable_tab("Items")

        text_hat = self.section(tab, "Text Hat", 0)

        self.text_hat_entry = self.text_control(
            text_hat, 0, "Text", "Item.TextHatText"
        )

        ttk.Label(text_hat, text="Text preset").grid(
            row=1, column=0, sticky="w", pady=4, padx=(0, 10)
        )

        preset_frame = ttk.Frame(text_hat)
        preset_frame.grid(row=1, column=1, sticky="ew", pady=4)
        preset_frame.columnconfigure(0, weight=1)

        self.text_hat_preset_combo = ttk.Combobox(
            preset_frame,
            textvariable=self.text_hat_preset_var,
            state="readonly",
        )
        self.text_hat_preset_combo.grid(
            row=0, column=0, sticky="ew"
        )
        self.text_hat_preset_combo.bind(
            "<<ComboboxSelected>>",
            lambda _e: self.apply_text_hat_preset(),
        )

        ttk.Button(
            preset_frame,
            text="Save text as…",
            command=self.save_text_hat_preset,
        ).grid(row=0, column=1, padx=(8, 0))

        ttk.Button(
            preset_frame,
            text="Apply",
            command=self.apply_text_hat_preset,
        ).grid(row=0, column=2, padx=(8, 0))

        ttk.Button(
            preset_frame,
            text="Delete",
            command=self.delete_text_hat_preset,
        ).grid(row=0, column=3, padx=(8, 0))
        ttk.Button(
            preset_frame,
            text="Export…",
            command=self.export_selected_text_hat_preset,
        ).grid(row=0, column=4, padx=(8, 0))

        ttk.Label(
            text_hat,
            text=(
                "Text Hat presets store the Text Hat text and Text color "
                "(including Alpha / Game default). Legacy Mode and other settings are not changed."
            ),
            foreground="#666",
            wraplength=780,
            justify="left",
        ).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 5)
        )

        random_frame = ttk.LabelFrame(
            text_hat,
            text="Random Text Hat",
            padding=(8, 6),
        )
        random_frame.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(5, 8),
        )
        random_frame.columnconfigure(2, weight=1)

        ttk.Checkbutton(
            random_frame,
            text="Random preset after each Tower Unite session",
            variable=self.random_text_hat_enabled,
            command=self._toggle_random_text_hat_monitor,
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(
            random_frame,
            text="Randomize now",
            command=self.randomize_text_hat_now,
        ).grid(row=0, column=1, padx=(10, 0))
        ttk.Button(
            random_frame,
            text="Choose pool…",
            command=self.choose_text_hat_random_pool,
        ).grid(row=0, column=2, padx=(10, 0))

        ttk.Label(
            random_frame,
            textvariable=self.random_text_hat_status,
            foreground="#666",
            wraplength=360,
            justify="left",
        ).grid(row=0, column=3, sticky="w", padx=(12, 0))
        ttk.Label(
            random_frame,
            textvariable=self.text_hat_pool_status,
            foreground="#666",
        ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(4, 0))

        ttk.Label(
            random_frame,
            text=(
                "AngelTune only checks the Tower Unite process while this option is enabled "
                "and AngelTune is open. When disabled, no background monitor or polling runs."
            ),
            foreground="#666",
            wraplength=820,
            justify="left",
        ).grid(
            row=2,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(5, 0),
        )

        ttk.Label(text_hat, text="Text symbols / emoticons").grid(
            row=4, column=0, sticky="w", pady=4, padx=(0, 10)
        )

        symbol_frame = ttk.Frame(text_hat)
        symbol_frame.grid(row=4, column=1, sticky="ew", pady=4)
        symbol_frame.columnconfigure(0, weight=1)

        self.text_hat_symbol_choice = tk.StringVar(
            value=TEXT_HAT_SYMBOLS[0][0]
        )
        self.text_hat_symbol_combo = ttk.Combobox(
            symbol_frame,
            textvariable=self.text_hat_symbol_choice,
            values=[label for label, _symbol in TEXT_HAT_SYMBOLS],
            state="readonly",
            width=28,
        )
        self.text_hat_symbol_combo.grid(row=0, column=0, sticky="ew")

        ttk.Button(
            symbol_frame,
            text="Insert",
            command=self.insert_text_hat_symbol,
        ).grid(row=0, column=1, padx=(8, 0))

        quick = ttk.Frame(text_hat)
        quick.grid(row=5, column=1, sticky="w", pady=(0, 5))
        ttk.Label(quick, text="Quick:").pack(side="left", padx=(0, 5))
        for symbol in ["♡", "♥", "★", "✦", "♪", ":3"]:
            ttk.Button(
                quick,
                text=symbol,
                width=3,
                command=lambda s=symbol: self.insert_text_hat_symbol_value(s),
            ).pack(side="left", padx=(0, 4))

        ttk.Label(
            text_hat,
            text=(
                "Symbols are inserted at the current cursor position. "
                "Rendering depends on the font used by Tower Unite; unsupported "
                "characters may appear as a missing-glyph box."
            ),
            foreground="#666",
            wraplength=760,
            justify="left",
        ).grid(row=6, column=0, columnspan=2, sticky="w", pady=(2, 5))

        self.bool_control(
            text_hat, 7, "Legacy mode", "Item.TextHatLegacyMode"
        )

        text_hat_color = ColorRow(
            text_hat, "Text color", "Item.TextHatColor"
        )
        text_hat_color.grid(
            row=8, column=0, columnspan=2, sticky="ew", pady=4
        )
        self.color_rows["Item.TextHatColor"] = text_hat_color
        self.register_search(
            "Text Hat color",
            "Item.TextHatColor",
            text_hat_color.frame,
        )
        self.register_search(
            "Text Hat symbols",
            "Item.TextHatText",
            self.text_hat_symbol_combo,
        )
        self.register_search(
            "Text Hat preset",
            "Item.TextHatText",
            self.text_hat_preset_combo,
        )
        self.register_search(
            "Random Text Hat",
            "Item.TextHatText",
            random_frame,
        )

        self.refresh_text_hat_preset_list()

        colors = self.section(tab, "Item colors", 1)
        ttk.Button(
            colors,
            text="Use game defaults for all colors",
            command=self.reset_all_colors_to_game_default,
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        row_num = 1
        for label, key in ITEM_COLOR_KEYS.items():
            if key == "Item.TextHatColor":
                continue
            row = ColorRow(colors, label, key)
            row.grid(
                row=row_num,
                column=0,
                columnspan=2,
                sticky="ew",
                pady=4,
            )
            self.color_rows[key] = row
            self.register_search(label, key, row.frame)
            row_num += 1

        ttk.Label(
            colors,
            text=(
                "Only color values that already exist in your Game.ini "
                "are written back."
            ),
            wraplength=760,
            justify="left",
        ).grid(
            row=row_num,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(8, 0),
        )

        game_mode_colors = self.section(tab, "Game mode colors", 2)
        ttk.Label(
            game_mode_colors,
            text=(
                "Direct color values used by specific game modes. "
                "These work with the same picker, HEX and preset system as the other colors."
            ),
            foreground="#666",
            wraplength=780,
            justify="left",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        game_mode_color_keys = [
            ("Accelerate cart color", "Accelerate.CartColor"),
            ("Ball Race color", "BallRace.Color"),
        ]
        for i, (label, key) in enumerate(game_mode_color_keys, start=1):
            row = ColorRow(game_mode_colors, label, key)
            row.grid(
                row=i,
                column=0,
                columnspan=2,
                sticky="ew",
                pady=4,
            )
            self.color_rows[key] = row
            self.register_search(label, key, row.frame)

    def insert_text_hat_symbol(self):
        label = self.text_hat_symbol_choice.get()
        symbol = TEXT_HAT_SYMBOL_MAP.get(label)
        if symbol:
            self.insert_text_hat_symbol_value(symbol)

    def insert_text_hat_symbol_value(self, symbol):
        var = self.vars.get("Item.TextHatText")
        if var is None or not hasattr(self, "text_hat_entry"):
            return

        current = var.get()
        try:
            cursor = self.text_hat_entry.index(tk.INSERT)
        except Exception:
            cursor = len(current)

        cursor = max(0, min(len(current), int(cursor)))
        updated = current[:cursor] + symbol + current[cursor:]
        var.set(updated)

        try:
            self.text_hat_entry.focus_set()
            self.text_hat_entry.icursor(cursor + len(symbol))
        except Exception:
            pass

        self.status.set(f'Inserted "{symbol}" into Text Hat text.')

    def _build_gameplay_tab(self):
        tab = self.create_scrollable_tab("Gameplay")

        chat = self.section(tab, "Chat", 0)
        chat_toggles = [
            ("Enable Global Chat", "Chat.EnableGlobalChat"),
            ("Enable Global Chat in games", "Chat.EnableGlobalChatGames"),
            ("Show local messages in Global Chat", "Chat.DisplayLocalMessagesInGlobal"),
            ("Show game messages in Global Chat", "Chat.DisplayGamesInGlobal"),
            ("Show Global messages in Local Chat", "Chat.DisplayGlobalMessagesInLocal"),
            ("Enable direct messages", "Chat.EnableDM"),
            ("Enable emojis", "Chat.EnableEmojis"),
            ("Enable URLs", "Chat.EnableURLs"),
            ("Enable sending awards", "Chat.EnableSendingAwards"),
            ("Enable game-create messages", "Chat.EnableSendingGameCreate"),
            ("Show timestamps", "Chat.EnableTimestamps"),
            ("Show location arrows", "Chat.EnableLocationArrows"),
        ]
        for i, (label, key) in enumerate(chat_toggles):
            self.bool_control(chat, i, label, key)
        self.spin_control(
            chat, len(chat_toggles), "Chat width", "Chat.Width", 250, 1400, 10
        )

        regions = self.section(tab, "Chat region filters", 1)
        ttk.Label(
            regions,
            text=(
                "These four switches edit Chat.RegionFilters exactly "
                "as stored by Tower Unite."
            ),
        ).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )
        region_row = ttk.Frame(regions)
        region_row.grid(
            row=1, column=0, columnspan=2, sticky="w"
        )
        labels = [
            ("US", "REGION_US"),
            ("EU", "REGION_EU"),
            ("APAC", "REGION_APAC"),
            ("AU", "REGION_AU"),
        ]
        for label, key in labels:
            check = ttk.Checkbutton(
                region_row,
                text=label,
                variable=self.region_vars[key],
            )
            check.pack(side="left", padx=(0, 18), pady=3)
            self.register_search(
                f"Chat region: {label}", "Chat.RegionFilters", check
            )

        movement = self.section(tab, "Movement", 2)
        self.bool_control(
            movement, 0, "Toggle sprint", "Controls.ToggleSprint"
        )
        self.bool_control(
            movement, 1, "Toggle walk", "Controls.ToggleWalk"
        )
        self.bool_control(
            movement, 2, "Toggle crouch", "Controls.ToggleCrouch"
        )

        emotes = self.section(tab, "Emote shortcuts", 3)
        ttk.Label(
            emotes, text="Comma-separated emote shortcut IDs"
        ).grid(row=0, column=0, columnspan=3, sticky="w")

        self.emotes = tk.StringVar()
        self.vars["Lobby.EmoteShortcuts"] = self.emotes
        emote_entry = ttk.Entry(emotes, textvariable=self.emotes)
        emote_entry.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(5, 6),
        )
        emotes.columnconfigure(0, weight=1)
        self.register_search(
            "Emote shortcuts", "Lobby.EmoteShortcuts", emote_entry
        )

        ttk.Label(
            emotes,
            textvariable=self.emote_observed_text,
            foreground="#555",
            wraplength=820,
            justify="left",
        ).grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(0, 5)
        )

        ttk.Label(
            emotes, text="Insert a verified / observed shortcut ID:"
        ).grid(row=3, column=0, sticky="w", pady=3)

        self.emote_id_combo = ttk.Combobox(
            emotes,
            textvariable=self.emote_id_choice,
            values=sorted(self.known_emote_ids, key=str.lower),
            state="readonly",
            width=24,
        )
        self.emote_id_combo.grid(row=3, column=1, sticky="w", pady=3)
        if self.emote_id_combo["values"]:
            self.emote_id_combo.current(0)

        ttk.Button(
            emotes,
            text="Add",
            command=self.add_verified_emote_id,
        ).grid(row=3, column=2, sticky="w", padx=(8, 0), pady=3)

        ttk.Label(
            emotes,
            text="Known Tower Unite player-emote names:",
            font=("TkDefaultFont", 9, "bold"),
        ).grid(row=4, column=0, columnspan=3, sticky="w", pady=(10, 4))

        emote_names_frame = ttk.Frame(emotes)
        emote_names_frame.grid(
            row=5, column=0, columnspan=3, sticky="ew"
        )
        emote_names_frame.columnconfigure(0, weight=1)

        self.emote_names_text = tk.Text(
            emote_names_frame,
            height=8,
            wrap="word",
            takefocus=False,
        )
        self.emote_names_text.grid(row=0, column=0, sticky="ew")
        emote_names_scroll = ttk.Scrollbar(
            emote_names_frame,
            orient="vertical",
            command=self.emote_names_text.yview,
        )
        emote_names_scroll.grid(row=0, column=1, sticky="ns")
        self.emote_names_text.configure(
            yscrollcommand=emote_names_scroll.set
        )

        lines = []
        for category, names in EMOTE_DISPLAY_NAMES.items():
            lines.append(f"{category}: " + ", ".join(names))
        self.emote_names_text.insert("1.0", "\n\n".join(lines))
        self.emote_names_text.configure(state="disabled")

        ttk.Label(
            emotes,
            text=(
                "Important: the list above contains valid in-game emote display names. "
                "Tower Unite stores shortcut tokens in Game.ini, and the exact token is "
                "not publicly documented for every emote. The editor therefore only "
                "auto-inserts IDs that were verified or observed in your Game.ini. "
                "Bind another emote in-game and press Reload both to learn its exact ID."
            ),
            foreground="#666",
            wraplength=820,
            justify="left",
        ).grid(
            row=6,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(7, 0),
        )

    def _refresh_emote_id_reference(self):
        current = self.values.get("Lobby.EmoteShortcuts", "")
        observed = [
            item.strip()
            for item in current.split(",")
            if item.strip()
        ]
        self.known_emote_ids.update(observed)

        values = sorted(self.known_emote_ids, key=str.lower)
        if hasattr(self, "emote_id_combo"):
            self.emote_id_combo["values"] = values
            if values and self.emote_id_choice.get() not in values:
                self.emote_id_choice.set(values[0])

        if observed:
            self.emote_observed_text.set(
                "Observed shortcut IDs in loaded Game.ini: "
                + ", ".join(observed)
                + "  |  Known verified IDs: "
                + ", ".join(values)
            )
        else:
            self.emote_observed_text.set(
                "Known verified shortcut IDs: " + ", ".join(values)
            )

    def add_verified_emote_id(self):
        token = self.emote_id_choice.get().strip()
        if not token:
            return

        current = [
            item.strip()
            for item in self.emotes.get().split(",")
            if item.strip()
        ]

        if token in current:
            self.status.set(f'Emote shortcut "{token}" is already in the list.')
            return

        # Tower Unite's emote menu exposes hotkeys 1-9.
        if len(current) >= 9:
            messagebox.showwarning(
                APP_NAME,
                "Tower Unite provides nine emote shortcut slots (1-9).\n\n"
                "Remove one existing shortcut before adding another."
            )
            return

        current.append(token)
        self.emotes.set(",".join(current))
        self.status.set(
            f'Added verified emote shortcut ID "{token}". Save changes to write it.'
        )

    def _build_workshop_canvas_tab(self):
        tab = self.create_scrollable_tab("Workshop")

        workshop = self.section(tab, "Workshop", 0)
        workshop_toggles = [
            ("Enable Workshop", "Workshop.Enabled"),
            ("Enable player models", "Workshop.EnablePlayerModels"),
            ("Enable polygon limits", "Workshop.EnablePolyLimits"),
            ("Enable Workshop in Game Worlds", "Workshop.EnabledForGameWorlds"),
            ("Draw Workshop shadows", "Workshop.DrawShadows"),
            ("Enable Workshop for SDNL", "Workshop.EnabledForSDNL"),
        ]
        for i, (label, key) in enumerate(workshop_toggles):
            self.bool_control(workshop, i, label, key)
        self.spin_control(
            workshop,
            len(workshop_toggles),
            "Workshop cache limit",
            "Workshop.CacheLimit",
            0,
            10000,
            50,
        )

        canvas = self.section(tab, "Canvas / Media cache", 1)
        self.bool_control(
            canvas, 0, "Enable Canvas disk cache", "Canvas.DiskCacheEnabled"
        )
        self.bool_control(
            canvas, 1, "Canvas disk cache: friends only", "Canvas.DiskCacheFriendsOnly"
        )
        self.bool_control(
            canvas, 2, "Allow only listed image hosts", "Canvas.AllowedImageHostOnly"
        )
        self.spin_control(
            canvas, 3, "Canvas disk cache limit", "Canvas.DiskCacheLimit", 0, 10000, 50
        )
        self.spin_control(
            canvas, 4, "Canvas safety level (raw value)", "Canvas.SafetyLevel", 0, 5, 1
        )
        ttk.Label(
            canvas,
            text="Allowed image hosts remain visible under Info & Profile. The safety level is kept as a raw stored value.",
            foreground="#666",
            wraplength=760,
            justify="left",
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(4, 0))

    def _build_condo_tab(self):
        tab = self.create_scrollable_tab("Condo")

        condo = self.section(tab, "Condo permissions", 0)
        controls = [
            ("Connect to Lobby Chat", "Condo.ConnectToLobbyChat"),
            ("Allow doorbell", "Condo.AllowDoorbell"),
            ("Allow consume edibles", "Condo.AllowConsumeEdibles"),
            ("Allow weapons", "Condo.AllowWeapons"),
            ("Allow weapon projectiles", "Condo.AllowWeaponProjectiles"),
            ("Allow melee", "Condo.AllowMelee"),
            ("Allow fall damage", "Condo.AllowFallDamage"),
            ("Allow RC vehicles", "Condo.AllowRCVehicles"),
            ("Allow light switches", "Condo.AllowLightSwitchUse"),
            ("Allow instruments", "Condo.AllowInstrumentUse"),
            ("Allow laser pointer", "Condo.AllowLaserPointerUse"),
            ("Allow Magic Trampoline", "Condo.AllowMagicTrampolineUse"),
            ("Allow jetpack", "Condo.AllowJetpackUse"),
            ("Allow potions", "Condo.AllowPotionUse"),
            ("Allow speed items", "Condo.AllowSpeedUse"),
            ("Allow flashlight", "Condo.AllowFlashlightUse"),
            ("Allow Gravboots", "Condo.AllowGravbootUse"),
            ("Allow Comment Box use", "Condo.AllowCommentBoxUse"),
            ("Allow rocket jump", "Condo.AllowRocketJumpUse"),
            ("Allow milestone item use", "Condo.AllowMilestoneUse"),
            ("Moderation opt-in", "Condo.ModerationOptIn"),
            ("Enable Condo backups", "Condo.EnableBackups"),
        ]
        for i, (label, key) in enumerate(controls):
            self.bool_control(condo, i, label, key)

        self.spin_control(
            condo,
            len(controls),
            "Maximum Condo backups (0 = game-defined/unlimited behavior)",
            "Condo.MaxBackups",
            0,
            500,
            1,
        )

    def _build_privacy_content_tab(self):
        tab = self.create_scrollable_tab("Privacy")

        parental = self.section(tab, "Content controls", 0)
        controls = [
            ("Disable media players", "ParentalControl.DisableMediaPlayer"),
            ("Disable gore", "ParentalControl.DisableGore"),
            ("Disable chat", "ParentalControl.DisableChat"),
            ("Disable profanity filter", "ParentalControl.DisableProfanityFilter"),
            ("Show NSFW Condo content", "ParentalControl.Condo.ShowNSFW"),
        ]
        for i, (label, key) in enumerate(controls):
            self.bool_control(parental, i, label, key)

        ttk.Label(
            parental,
            text=(
                "These are the exact boolean values already present in Game.ini. "
                "The 'Disable profanity filter' checkbox follows the config key literally: "
                "checked means the profanity filter is disabled."
            ),
            foreground="#666",
            wraplength=800,
            justify="left",
        ).grid(
            row=len(controls),
            column=0,
            columnspan=2,
            sticky="w",
            pady=(8, 0),
        )

        canvas = self.section(tab, "Canvas content", 1)
        self.bool_control(
            canvas,
            0,
            "Enable Canvas Quick UI",
            "ParentalControl.Canvas.EnableQuickUI",
        )
        self.bool_control(
            canvas,
            1,
            "Enable animated Canvas content",
            "ParentalControl.Canvas.EnableAnimated",
        )

        ttk.Label(
            canvas,
            text=(
                "These options expose the existing Canvas content-control flags. "
                "They do not change the allowed image-host list."
            ),
            foreground="#666",
            wraplength=800,
            justify="left",
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(8, 0),
        )

    def _build_profile_tab(self):
        tab = self.create_scrollable_tab("Info")

        supporter = self.section(tab, "Supporter tag display", 0)
        self.bool_control(
            supporter,
            0,
            "Hide my supporter tags",
            "Profile.HideMySupporterTags",
        )
        self.bool_control(
            supporter,
            1,
            "Collapse supporter tags",
            "Profile.CollapseSupporterTags",
        )
        ttk.Label(
            supporter,
            text=(
                "These options only control how supporter tags are displayed; "
                "they do not change your supporter status."
            ),
            foreground="#666",
            wraplength=780,
            justify="left",
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(6, 0),
        )

        info = self.section(tab, "Current profile IDs (read-only)", 1)
        self.profile_labels = {}
        profile_keys = [
            "Profile.Background",
            "Profile.Effects",
            "Profile.AvatarFrame",
            "Profile.ChatStyle",
            "Profile.Spray",
            "Profile.Flashlight",
        ]
        for i, key in enumerate(profile_keys):
            ttk.Label(info, text=key).grid(
                row=i, column=0, sticky="nw", pady=3, padx=(0, 10)
            )
            var = tk.StringVar(value="—")
            self.profile_labels[key] = var
            ent = ttk.Entry(info, textvariable=var, state="readonly")
            ent.grid(row=i, column=1, sticky="ew", pady=3)
            self.register_search(key, key, ent)
        info.columnconfigure(1, weight=1)

        quest_box = self.section(
            tab, "Lobby quest progress (read-only)", 2
        )
        self.quest_summary = tk.StringVar(
            value="Load Game.ini to show quest progress."
        )
        ttk.Label(
            quest_box,
            textvariable=self.quest_summary,
            font=("TkDefaultFont", 10, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.quest_progress_vars = {
            "characters": tk.StringVar(value="Characters: 0 / 10"),
            "bones": tk.StringVar(value="Bones: 0 / 10"),
            "puppy": tk.StringVar(value="Puppy: 0 / 1"),
        }
        progress_frame = ttk.Frame(quest_box)
        progress_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        for c in range(3):
            progress_frame.columnconfigure(c, weight=1)

        self.quest_progress_bars = {}
        for col, (key, maximum) in enumerate([
            ("characters", HALLOWEEN_CHARACTER_TOTAL),
            ("bones", HALLOWEEN_BONES_TOTAL),
            ("puppy", HALLOWEEN_PUPPY_TOTAL),
        ]):
            card = ttk.LabelFrame(progress_frame, padding=8)
            card.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 6, 0))
            ttk.Label(
                card,
                textvariable=self.quest_progress_vars[key],
                font=("TkDefaultFont", 9, "bold"),
            ).pack(anchor="w")
            bar = ttk.Progressbar(
                card,
                maximum=maximum,
                value=0,
                style="Angel.Horizontal.TProgressbar",
            )
            bar.pack(fill="x", pady=(6, 0))
            self.quest_progress_bars[key] = bar

        self.quest_text = tk.Text(
            quest_box, height=9, wrap="word"
        )
        self.quest_text.grid(row=2, column=0, sticky="ew")
        self.quest_text.configure(state="disabled")
        quest_box.columnconfigure(0, weight=1)
        self.register_search(
            "Lobby quest progress",
            "Lobby.QuestProgress",
            self.quest_text,
        )

        host_box = self.section(
            tab, "Allowed image hosts (read-only)", 3
        )
        self.image_host_count = tk.StringVar(value="0 hosts")
        ttk.Label(
            host_box, textvariable=self.image_host_count
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        host_frame = ttk.Frame(host_box)
        host_frame.grid(row=1, column=0, sticky="ew")
        host_frame.columnconfigure(0, weight=1)
        self.image_hosts_list = tk.Listbox(host_frame, height=6)
        self.image_hosts_list.grid(row=0, column=0, sticky="ew")
        sb = ttk.Scrollbar(
            host_frame,
            orient="vertical",
            command=self.image_hosts_list.yview,
        )
        sb.grid(row=0, column=1, sticky="ns")
        self.image_hosts_list.configure(yscrollcommand=sb.set)
        host_box.columnconfigure(0, weight=1)
        self.register_search(
            "Allowed image hosts",
            "Canvas.AllowedImageHosts",
            self.image_hosts_list,
        )

        hint = self.section(tab, "Info", 4)
        ttk.Label(
            hint,
            text=(
                "Quest and image-host information is read-only here. "
                "Halloween Character Visit uses the known 10-character set. "
                "Halloween2020.Bones is counted as 10 total bones and its stored "
                "ProgressIDs show exactly which bone pickups were already found. "
                "Halloween2019.Puppy is shown as a 1-item quest and is complete "
                "when its state is COMPLETED."
            ),
            wraplength=760,
            justify="left",
        ).grid(row=0, column=0, sticky="w")


    def _build_advanced_tab(self):
        tab = self.create_scrollable_tab("Advanced")

        editable = self.section(tab, "Additional GameUserSettings (editable)", 0)
        self.gus_bool_control(
            editable, 0, "Use desired screen height", "bUseDesiredScreenHeight"
        )
        self.gus_bool_control(
            editable, 1, "MOTD enabled", "bMotdEnabled"
        )
        self.gus_bool_control(
            editable, 2, "GameUserSettings voice enabled", "bVoiceEnabled"
        )
        self.gus_spin_control(
            editable, 3, "Window position X", "WindowPosX", -1, 10000, 1
        )
        self.gus_spin_control(
            editable, 4, "Window position Y", "WindowPosY", -1, 10000, 1
        )
        self.gus_spin_control(
            editable, 5, "Audio quality level (raw value)", "AudioQualityLevel", 0, 4, 1
        )
        self.gus_spin_control(
            editable, 6, "Desired screen width", "DesiredScreenWidth", 640, 7680, 1
        )
        self.gus_spin_control(
            editable, 7, "Desired screen height", "DesiredScreenHeight", 480, 4320, 1
        )
        ttk.Label(
            editable,
            text=(
                "These values already exist in your GameUserSettings.ini. "
                "Some are Unreal/Tower internal preferences and may be rewritten by the game."
            ),
            foreground="#666",
            wraplength=760,
            justify="left",
        ).grid(row=8, column=0, columnspan=2, sticky="w", pady=(4, 0))

        raw_game = self.section(tab, "Game.ini internals (read-only)", 1)
        self.advanced_game_labels = {}
        advanced_game_keys = [
            "General.News.LastUpdateSeen",
            "Lobby.DayNightMode",
            "Condo.DayNightMode",
            "Condo.JoinPermissions",
            "Dialogue.TextSpeed",
            "HUD.PlayerNames.DrawDistanceMultiplier",
            "Gamepad.ControllerStyle",
            "Gameplay.VomitStyle",
            "Lobby.PVPAllowed",
            "Workshop.PlayerModel",
            "Workshop.Accelerate.VehicleModel",
        ]
        for i, key in enumerate(advanced_game_keys):
            ttk.Label(raw_game, text=key).grid(
                row=i, column=0, sticky="w", padx=(0, 10), pady=3
            )
            var = tk.StringVar(value="—")
            self.advanced_game_labels[key] = var
            ent = ttk.Entry(raw_game, textvariable=var, state="readonly")
            ent.grid(row=i, column=1, sticky="ew", pady=3)
            self.register_search(key, key, ent)
        raw_game.columnconfigure(1, weight=1)

        raw_gus = self.section(tab, "GameUserSettings internals (read-only)", 2)
        self.advanced_gus_labels = {}
        advanced_gus_keys = [
            "TowerVersion",
            "Version",
            "LastUserConfirmedResolutionSizeX",
            "LastUserConfirmedResolutionSizeY",
            "LastConfirmedFullscreenMode",
            "PreferredFullscreenMode",
            "LastConfirmedAudioQualityLevel",
            "LastUserConfirmedDesiredScreenWidth",
            "LastUserConfirmedDesiredScreenHeight",
            "LastRecommendedScreenWidth",
            "LastRecommendedScreenHeight",
            "LastCPUBenchmarkResult",
            "LastGPUBenchmarkResult",
            "LastGPUBenchmarkMultiplier",
            "LastOpened",
        ]
        for i, key in enumerate(advanced_gus_keys):
            ttk.Label(raw_gus, text=key).grid(
                row=i, column=0, sticky="w", padx=(0, 10), pady=3
            )
            var = tk.StringVar(value="—")
            self.advanced_gus_labels[key] = var
            ent = ttk.Entry(raw_gus, textvariable=var, state="readonly")
            ent.grid(row=i, column=1, sticky="ew", pady=3)
            self.register_search(key, f"GameUserSettings:{key}", ent)
        raw_gus.columnconfigure(1, weight=1)

        notes = self.section(tab, "Intentionally not editable", 3)
        ttk.Label(
            notes,
            text=(
                "Quest progress, casino chips, arcade tokens, blocked-player data, "
                "per-player voice volumes, internal save/loadout structures, and similar "
                "progress/account state are intentionally not exposed as editable fields."
            ),
            wraplength=780,
            justify="left",
        ).grid(row=0, column=0, sticky="w")

    def reset_all_colors_to_game_default(self):
        for row in self.color_rows.values():
            row.set_game_default()
        self.status.set(
            "All exposed colors are marked to use Tower Unite's built-in defaults on Save."
        )

    # ------------------------------------------------------------- loading --
    def _refresh_info_views(self):
        for key, var in self.profile_labels.items():
            var.set(self.values.get(key, "—"))

        for key, var in getattr(self, "advanced_game_labels", {}).items():
            var.set(self.values.get(key, "—"))

        hosts = parse_allowed_image_hosts(
            self.values.get("Canvas.AllowedImageHosts", "")
        )
        self.image_hosts_list.delete(0, tk.END)
        for host in hosts:
            self.image_hosts_list.insert(tk.END, host)
        self.image_host_count.set(
            f"{len(hosts)} allowed host"
            f'{"s" if len(hosts) != 1 else ""}'
        )

        quests = parse_quest_progress(
            self.values.get("Lobby.QuestProgress", "")
        )
        character = next(
            (
                q
                for q in quests
                if q["name"] == "Halloween2020.Character"
            ),
            None,
        )
        bones = next(
            (
                q
                for q in quests
                if q["name"] == "Halloween2020.Bones"
            ),
            None,
        )
        puppy = next(
            (
                q
                for q in quests
                if q["name"] == "Halloween2019.Puppy"
            ),
            None,
        )

        character_details = None
        summary_parts = []
        character_found_ui = 0
        bones_found_ui = 0
        puppy_found_ui = 0

        if character:
            ids = list(character["progress_ids"])

            mapped_found = []
            unknown_ids = []
            for progress_id in ids:
                display_name = HALLOWEEN_PROGRESS_ID_TO_NAME.get(progress_id)
                if display_name:
                    mapped_found.append((display_name, progress_id))
                else:
                    unknown_ids.append(progress_id)

            mapped_names = {display_name for display_name, _pid in mapped_found}
            missing_names = [
                display_name
                for display_name in HALLOWEEN_CHARACTER_NAMES
                if display_name not in mapped_names
            ]

            inferred = []
            if len(unknown_ids) == 1 and len(missing_names) == 1:
                inferred_name = missing_names[0]
                inferred.append((inferred_name, unknown_ids[0]))
                mapped_found.append((inferred_name, unknown_ids[0]))
                mapped_names.add(inferred_name)
                missing_names = []

            if character["state"] == "COMPLETED":
                found_count = HALLOWEEN_CHARACTER_TOTAL
                missing_names = []
            else:
                found_count = min(
                    len(mapped_found),
                    HALLOWEEN_CHARACTER_TOTAL,
                )

            character_found_ui = found_count

            if missing_names:
                summary_parts.append(
                    "Halloween characters: "
                    f"{found_count} / {HALLOWEEN_CHARACTER_TOTAL} found - "
                    "Missing: " + ", ".join(missing_names)
                )
            else:
                summary_parts.append(
                    "Halloween characters: "
                    f"{found_count} / {HALLOWEEN_CHARACTER_TOTAL} found - Complete"
                )

            inferred_ids = {pid for _name, pid in inferred}
            character_details = {
                "state": character["state"],
                "found": mapped_found,
                "unknown": [
                    item for item in unknown_ids if item not in inferred_ids
                ],
                "missing": missing_names,
            }
        else:
            summary_parts.append(
                "Halloween character quest not present in this Game.ini."
            )

        if bones:
            bone_ids = list(bones["progress_ids"])
            if bones["state"] == "COMPLETED":
                bones_found = HALLOWEEN_BONES_TOTAL
            else:
                bones_found = min(len(bone_ids), HALLOWEEN_BONES_TOTAL)

            bones_found_ui = bones_found

            if bones_found >= HALLOWEEN_BONES_TOTAL:
                summary_parts.append(
                    f"Halloween bones: {HALLOWEEN_BONES_TOTAL} / "
                    f"{HALLOWEEN_BONES_TOTAL} found - Complete"
                )
            else:
                summary_parts.append(
                    f"Halloween bones: {bones_found} / "
                    f"{HALLOWEEN_BONES_TOTAL} found"
                )
        else:
            summary_parts.append(
                "Halloween bones quest not present in this Game.ini."
            )

        if puppy:
            puppy_found = (
                HALLOWEEN_PUPPY_TOTAL
                if puppy["state"] == "COMPLETED"
                else 0
            )
            puppy_found_ui = puppy_found

            if puppy_found >= HALLOWEEN_PUPPY_TOTAL:
                summary_parts.append(
                    "Halloween puppy: 1 / 1 found - Complete"
                )
            else:
                summary_parts.append(
                    "Halloween puppy: 0 / 1 found"
                )
        else:
            summary_parts.append(
                "Halloween puppy quest not present in this Game.ini."
            )

        if hasattr(self, "quest_progress_vars"):
            self.quest_progress_vars["characters"].set(
                f"Characters: {character_found_ui} / {HALLOWEEN_CHARACTER_TOTAL}"
            )
            self.quest_progress_vars["bones"].set(
                f"Bones: {bones_found_ui} / {HALLOWEEN_BONES_TOTAL}"
            )
            self.quest_progress_vars["puppy"].set(
                f"Puppy: {puppy_found_ui} / {HALLOWEEN_PUPPY_TOTAL}"
            )
            self.quest_progress_bars["characters"].configure(value=character_found_ui)
            self.quest_progress_bars["bones"].configure(value=bones_found_ui)
            self.quest_progress_bars["puppy"].configure(value=puppy_found_ui)

        self.quest_summary.set("\n".join(summary_parts))

        lines = []
        for quest in quests:
            name = quest["name"]
            state = quest["state"]
            ids = quest["progress_ids"]
            if name == "Halloween2020.Character":
                lines.append(f"{name} - {state}")

                if character_details:
                    found_entries = [
                        f"{display_name} [{progress_id}]"
                        for display_name, progress_id in character_details["found"]
                    ]
                    lines.append(
                        "Found characters: "
                        + (", ".join(found_entries) if found_entries else "none")
                    )

                    if character_details["missing"]:
                        lines.append(
                            "Missing character(s): "
                            + ", ".join(character_details["missing"])
                        )
                    else:
                        lines.append("Missing character(s): none")

                    if character_details["unknown"]:
                        lines.append(
                            "Unmapped config ID(s): "
                            + ", ".join(character_details["unknown"])
                        )

            elif name == "Halloween2020.Bones":
                if state == "COMPLETED":
                    found_bones = HALLOWEEN_BONES_TOTAL
                else:
                    found_bones = min(len(ids), HALLOWEEN_BONES_TOTAL)

                lines.append(f"{name} - {state}")
                lines.append(
                    f"Bones found: {found_bones} / {HALLOWEEN_BONES_TOTAL}"
                )
                lines.append(
                    "Found bone IDs: "
                    + (", ".join(ids) if ids else "none")
                )

            elif name == "Halloween2019.Puppy":
                puppy_found = (
                    HALLOWEEN_PUPPY_TOTAL
                    if state == "COMPLETED"
                    else 0
                )
                lines.append(f"{name} - {state}")
                lines.append(
                    f"Puppy found: {puppy_found} / {HALLOWEEN_PUPPY_TOTAL}"
                )

            elif ids:
                lines.append(
                    f"{name} - {state} - Progress IDs: "
                    + ", ".join(ids)
                )
            else:
                lines.append(f"{name} - {state}")

        if not lines:
            lines = ["No parsed Lobby.QuestProgress entries found."]

        self.quest_text.configure(state="normal")
        self.quest_text.delete("1.0", tk.END)
        self.quest_text.insert("1.0", "\n".join(lines))
        self.quest_text.configure(state="disabled")

    def show_startup_disclaimer(self):
        messagebox.showwarning(
            f"{APP_NAME} - Tiny Config Gremlin Warning ♡",
            "Heya, little config gremlin ♡\n\n"
            "AngelTune is an unofficial Tower Unite config editor.\n\n"
            "A few things before you start:\n"
            "- Game updates may overwrite configuration changes.\n"
            "- Some unusual settings can behave unexpectedly.\n"
            "- Modified config values are always used at your own risk.\n\n"
            "AngelTune creates automatic backups before saving, because losing "
            "a cute setup would be criminally un-fun. Keeping your own extra "
            "backup is still a very good idea.\n\n"
            "I cannot take responsibility for data loss, broken settings, game issues, "
            "account actions, or bans resulting from modified configuration values.\n\n"
            "AngelTune is not affiliated with PixelTail Games, Valve, or Steam.\n\n"
            "Before saving:\n"
            "Close Tower Unite first - otherwise the game may overwrite your "
            "changes like a tiny menace. ♡"
        )

    def _set_window_icon(self):
        try:
            icon_path = resource_path("assets", "angeltune_icon.png")
            if icon_path.exists():
                self.window_icon = tk.PhotoImage(file=str(icon_path))
                self.iconphoto(True, self.window_icon)
        except Exception:
            pass

    # --------------------------------------------------------------- theme --
    def toggle_ui_theme(self):
        self.ui_theme = "angel" if self.ui_theme != "angel" else "default"
        self.apply_ui_theme()

    def apply_ui_theme(self):
        style = ttk.Style(self)

        if self.ui_theme == "angel":
            palette = {
                "bg": "#21151D",
                "panel": "#32202A",
                "panel2": "#422837",
                "fg": "#FFEAF1",
                "muted": "#DDAFC0",
                "field": "#FFF1F5",
                "field_fg": "#3B1E2A",
                "accent": "#F07BA7",
                "accent_hover": "#FF95BC",
                "accent_dark": "#9D4268",
                "button": "#6D304C",
                "button_hover": "#88405F",
                "border": "#B95D82",
                "selection": "#F2A1BE",
                "selection_fg": "#2D1720",
            }

            # "clam" reliably accepts custom colors on Windows.
            try:
                style.theme_use("clam")
            except tk.TclError:
                pass

            self.configure(background=palette["bg"])

            style.configure(".", background=palette["bg"], foreground=palette["fg"])
            style.configure("TFrame", background=palette["bg"])
            style.configure(
                "TLabel",
                background=palette["bg"],
                foreground=palette["fg"],
            )
            style.configure(
                "Hero.TLabel",
                background=palette["bg"],
                foreground=palette["accent_hover"],
                font=("TkDefaultFont", 20, "bold"),
            )
            style.configure(
                "HeroSub.TLabel",
                background=palette["bg"],
                foreground=palette["muted"],
                font=("TkDefaultFont", 10),
            )
            style.configure(
                "Muted.TLabel",
                background=palette["bg"],
                foreground=palette["muted"],
            )
            style.configure(
                "Accent.TButton",
                background=palette["accent_dark"],
                foreground=palette["fg"],
                bordercolor=palette["accent"],
                padding=(9, 5),
            )
            style.map(
                "Accent.TButton",
                background=[("active", palette["accent"]), ("pressed", palette["accent_dark"])],
                foreground=[("active", palette["selection_fg"])],
            )
            style.configure(
                "Angel.Horizontal.TProgressbar",
                troughcolor=palette["panel2"],
                background=palette["accent"],
                bordercolor=palette["border"],
                lightcolor=palette["accent_hover"],
                darkcolor=palette["accent_dark"],
            )
            style.configure(
                "TLabelframe",
                background=palette["bg"],
                foreground=palette["fg"],
                bordercolor=palette["border"],
                lightcolor=palette["border"],
                darkcolor=palette["panel"],
            )
            style.configure(
                "TLabelframe.Label",
                background=palette["bg"],
                foreground=palette["accent_hover"],
            )
            style.configure(
                "TButton",
                background=palette["button"],
                foreground=palette["fg"],
                bordercolor=palette["border"],
                focusthickness=1,
                focuscolor=palette["accent"],
                padding=(7, 4),
            )
            style.map(
                "TButton",
                background=[
                    ("active", palette["button_hover"]),
                    ("pressed", palette["accent_dark"]),
                ],
                foreground=[("disabled", palette["muted"])],
            )
            style.configure(
                "TEntry",
                fieldbackground=palette["field"],
                foreground=palette["field_fg"],
                insertcolor=palette["field_fg"],
                bordercolor=palette["border"],
            )
            style.configure(
                "TSpinbox",
                fieldbackground=palette["field"],
                foreground=palette["field_fg"],
                arrowcolor=palette["accent_dark"],
                bordercolor=palette["border"],
            )
            style.configure(
                "TCombobox",
                fieldbackground=palette["field"],
                foreground=palette["field_fg"],
                arrowcolor=palette["accent_dark"],
                bordercolor=palette["border"],
            )
            style.map(
                "TCombobox",
                fieldbackground=[
                    ("readonly", palette["field"]),
                    ("disabled", palette["panel"]),
                ],
                foreground=[
                    ("readonly", palette["field_fg"]),
                    ("disabled", palette["muted"]),
                ],
                selectbackground=[("readonly", palette["field"])],
                selectforeground=[("readonly", palette["field_fg"])],
            )
            style.configure(
                "TCheckbutton",
                background=palette["bg"],
                foreground=palette["fg"],
            )
            style.map(
                "TCheckbutton",
                background=[("active", palette["panel2"])],
                foreground=[("disabled", palette["muted"])],
            )
            style.configure(
                "TNotebook",
                background=palette["panel"],
                bordercolor=palette["border"],
            )
            style.configure(
                "TNotebook.Tab",
                background=palette["panel2"],
                foreground=palette["muted"],
                padding=(6, 5),
            )
            style.map(
                "TNotebook.Tab",
                background=[
                    ("selected", palette["accent_dark"]),
                    ("active", palette["button_hover"]),
                ],
                foreground=[
                    ("selected", palette["fg"]),
                    ("active", palette["fg"]),
                ],
            )
            style.configure(
                "Horizontal.TScale",
                background=palette["bg"],
                troughcolor=palette["panel2"],
                bordercolor=palette["border"],
                lightcolor=palette["accent"],
                darkcolor=palette["accent_dark"],
            )
            style.configure(
                "Vertical.TScrollbar",
                background=palette["button"],
                troughcolor=palette["panel"],
                bordercolor=palette["border"],
                arrowcolor=palette["fg"],
            )
            style.configure(
                "Horizontal.TScrollbar",
                background=palette["button"],
                troughcolor=palette["panel"],
                bordercolor=palette["border"],
                arrowcolor=palette["fg"],
            )
            style.configure(
                "Treeview",
                background=palette["field"],
                fieldbackground=palette["field"],
                foreground=palette["field_fg"],
                bordercolor=palette["border"],
                rowheight=25,
            )
            style.map(
                "Treeview",
                background=[("selected", palette["selection"])],
                foreground=[("selected", palette["selection_fg"])],
            )
            style.configure(
                "Treeview.Heading",
                background=palette["panel2"],
                foreground=palette["fg"],
                bordercolor=palette["border"],
            )

            # Non-ttk widgets do not inherit ttk styles.
            for info in self.tab_infos.values():
                try:
                    info["canvas"].configure(background=palette["bg"])
                except Exception:
                    pass

            for widget in self.winfo_children():
                self._apply_tk_widget_theme(widget, palette, angel=True)

            if hasattr(self, "theme_button"):
                self.theme_button.configure(text="🎨 Default")

        else:
            # Return to the user's normal platform ttk theme.
            try:
                style.theme_use(self.default_ttk_theme)
            except tk.TclError:
                pass

            default_bg = style.lookup("TFrame", "background") or "#F0F0F0"
            self.configure(background=default_bg)

            default_palette = {
                "bg": default_bg,
                "panel": default_bg,
                "panel2": default_bg,
                "fg": "#202020",
                "muted": "#666666",
                "field": "#FFFFFF",
                "field_fg": "#202020",
                "accent": "#0078D7",
                "accent_hover": "#0078D7",
                "accent_dark": "#005A9E",
                "button": default_bg,
                "button_hover": default_bg,
                "border": "#777777",
                "selection": "#0078D7",
                "selection_fg": "#FFFFFF",
            }

            style.configure("Hero.TLabel", font=("TkDefaultFont", 20, "bold"))
            style.configure("HeroSub.TLabel", foreground="#666666")
            style.configure("Muted.TLabel", foreground="#666666")
            style.configure("Accent.TButton", padding=(9, 5))
            style.configure(
                "Angel.Horizontal.TProgressbar",
                troughcolor="#DDDDDD",
                background="#0078D7",
            )

            for info in self.tab_infos.values():
                try:
                    info["canvas"].configure(background=default_bg)
                except Exception:
                    pass

            for widget in self.winfo_children():
                self._apply_tk_widget_theme(widget, default_palette, angel=False)

            if hasattr(self, "theme_button"):
                self.theme_button.configure(text="🎨 Angel")

        # Redraw color swatches after general Canvas styling.
        for row in self.color_rows.values():
            try:
                row.refresh()
            except Exception:
                pass

        # Restore the HUD image/fallback after any theme changes.
        try:
            self._update_hud_preview()
        except Exception:
            pass

    def _apply_tk_widget_theme(self, widget, palette, angel):
        """Theme classic Tk widgets while leaving color-preview canvases alone."""
        try:
            children = widget.winfo_children()
        except Exception:
            children = []

        for child in children:
            cls = child.winfo_class()

            try:
                if isinstance(child, tk.Listbox):
                    child.configure(
                        background=palette["field"],
                        foreground=palette["field_fg"],
                        selectbackground=palette["selection"],
                        selectforeground=palette["selection_fg"],
                    )
                elif isinstance(child, tk.Text):
                    child.configure(
                        background=palette["field"],
                        foreground=palette["field_fg"],
                        insertbackground=palette["field_fg"],
                        selectbackground=palette["selection"],
                        selectforeground=palette["selection_fg"],
                    )
                elif isinstance(child, tk.Canvas):
                    # Large canvases are layout/HUD canvases. Small canvases are
                    # color swatches and should keep showing the actual chosen color.
                    try:
                        width = int(float(child.cget("width")))
                        height = int(float(child.cget("height")))
                    except Exception:
                        width, height = 999, 999

                    if width > 80 or height > 40:
                        # Keep the HUD screenshot canvas dark; scroll canvases are
                        # separately recolored through self.tab_infos.
                        if child is not getattr(self, "hud_preview", None):
                            child.configure(background=palette["bg"])
            except Exception:
                pass

            self._apply_tk_widget_theme(child, palette, angel)

    def browse(self):
        p = filedialog.askopenfilename(
            title="Choose Tower Unite Game.ini",
            filetypes=[
                ("Game.ini", "Game.ini"),
                ("INI files", "*.ini"),
                ("All files", "*.*"),
            ],
        )
        if p:
            self.path.set(p)
            sibling = Path(p).parent / "GameUserSettings.ini"
            if sibling.exists():
                self.user_settings_path.set(str(sibling))
            self.load_files()

    def browse_user_settings(self):
        p = filedialog.askopenfilename(
            title="Choose Tower Unite GameUserSettings.ini",
            filetypes=[
                ("GameUserSettings.ini", "GameUserSettings.ini"),
                ("INI files", "*.ini"),
                ("All files", "*.*"),
            ],
        )
        if p:
            self.user_settings_path.set(p)
            sibling = Path(p).parent / "Game.ini"
            if sibling.exists():
                self.path.set(str(sibling))
            self.load_files()

    def load_files(self):
        old_suppress = self._suppress_dirty
        self._suppress_dirty = True
        try:
            self.load_file()
            self.load_user_settings()
            self.refresh_preset_list()
            self.refresh_text_hat_preset_list()
        finally:
            self._suppress_dirty = old_suppress
        self._set_clean_baseline()
        self.refresh_backup_history()
        self.update_dashboard()

    def open_folder(self):
        p = Path(self.path.get()).expanduser()
        folder = p.parent if p.suffix else p
        if not folder.exists():
            messagebox.showerror(
                APP_NAME, "The folder does not exist."
            )
            return
        try:
            if os.name == "nt":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
        except Exception as e:
            messagebox.showerror(APP_NAME, str(e))

    def load_file(self):
        p = Path(self.path.get()).expanduser()
        if not p.exists():
            self.status.set("Game.ini not found.")
            return
        try:
            text, enc, nl = read_text_preserving(p)
            values = parse_key_values(text)
        except Exception as e:
            messagebox.showerror(
                APP_NAME, f"Could not read file:\n{e}"
            )
            return

        self.loaded_path = p
        self.original_text = text
        self.encoding = enc
        self.newline = nl
        self.values = values

        hud_raw = values.get("HUD.Mode", "")
        self.hud_style.set(
            HUD_STYLES_REV.get(
                hud_raw,
                f"Unknown ({hud_raw})" if hud_raw else "Cute",
            )
        )
        self._update_hud_preview()

        for key, row in self.color_rows.items():
            if key in values:
                row.load(values[key])
            else:
                row.load_as_game_default()

        for key, var in self.vars.items():
            if key not in values:
                continue
            raw = values[key]
            if isinstance(var, tk.BooleanVar):
                var.set(raw.lower() == "true")
            else:
                var.set(raw)

        for key, var in self.volume_vars.items():
            if key not in values:
                continue
            try:
                pct = max(
                    0,
                    min(100, round(float(values[key]) * 100)),
                )
            except Exception:
                pct = 100
            var.set(pct)
            self.volume_value_labels[key].set(f"{pct}%")

        region_values = parse_region_filters(
            values.get("Chat.RegionFilters", "")
        )
        for key, var in self.region_vars.items():
            var.set(region_values.get(key, False))

        self._refresh_info_views()
        self._refresh_emote_id_reference()
        self.status.set(
            f"Loaded {p.name} — {len(values)} settings found."
        )


    def load_user_settings(self):
        p = Path(self.user_settings_path.get()).expanduser()
        if not p.exists():
            self.loaded_user_settings_path = None
            self.status.set("Game.ini loaded; GameUserSettings.ini was not found.")
            return

        try:
            text, enc, nl = read_text_preserving(p)
            values = parse_key_values(text)
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not read GameUserSettings.ini:\n{e}")
            return

        self.loaded_user_settings_path = p
        self.user_settings_original_text = text
        self.user_settings_encoding = enc
        self.user_settings_newline = nl
        self.user_settings_values = values

        for key, var in self.gus_vars.items():
            if key not in values:
                continue
            raw = values[key]
            if isinstance(var, tk.BooleanVar):
                var.set(raw.lower() == "true")
            else:
                var.set(raw)

        x = values.get("ResolutionSizeX")
        y = values.get("ResolutionSizeY")
        if x and y:
            self.resolution_preset.set(f"{x} x {y}")

        mode_raw = values.get("FullscreenMode", "0")
        self.display_mode.set(DISPLAY_MODE_VALUES.get(mode_raw, f"Raw value {mode_raw}"))

        for key, var in getattr(self, "gus_info_labels", {}).items():
            var.set(values.get(key, "—"))

        for key, var in getattr(self, "advanced_gus_labels", {}).items():
            var.set(values.get(key, "—"))

        game_name = self.loaded_path.name if self.loaded_path else "Game.ini"
        self.status.set(
            f"Loaded {game_name} and {p.name} — "
            f"{len(self.values)} + {len(values)} settings found."
        )

    # --------------------------------------------------------------- saving --
    def collect_changes(self):
        changes = {}

        style = self.hud_style.get()
        if style in HUD_STYLES:
            changes["HUD.Mode"] = HUD_STYLES[style]

        for key, row in self.color_rows.items():
            changes[key] = row.value()

        changes["Chat.RegionFilters"] = format_region_filters(
            {key: var.get() for key, var in self.region_vars.items()}
        )

        # Commit manually typed percentage fields before reading slider values.
        for key, apply_entry in getattr(self, "volume_entry_apply", {}).items():
            apply_entry()

        for key, var in self.volume_vars.items():
            try:
                pct = max(0.0, min(100.0, float(var.get())))
            except Exception:
                pct = 100.0
            changes[key] = f"{pct / 100.0:.6f}"

        for key, var in self.vars.items():
            if isinstance(var, tk.BooleanVar):
                changes[key] = "True" if var.get() else "False"
                continue

            raw = str(var.get()).strip()
            if key in FLOAT_KEYS:
                try:
                    n = float(raw)
                except ValueError:
                    raise ValueError(f"{key}: expected a number")
                if key == "Graphics.UIScale":
                    n = min(2.0, max(0.50, n))
                elif key == "Graphics.FOV":
                    n = min(140.0, max(60.0, n))
                elif key == "Graphics.Gamma":
                    n = min(4.0, max(1.0, n))
                elif key == "Camera.ViewBob":
                    n = min(2.0, max(0.0, n))
                elif key == "Graphics.MirrorResolution":
                    n = min(2.0, max(0.10, n))
                elif key == "Lobby.PlayerFadeAmount":
                    n = min(1.0, max(0.0, n))
                elif key == "Nightclub.Brightness":
                    n = min(2.0, max(0.0, n))
                elif key == "Gameplay.MouseSensitivity":
                    n = min(1.0, max(0.001, n))
                elif key == "Gamepad.Sensitivity":
                    n = min(1.0, max(0.0, n))
                changes[key] = f"{n:.6f}"
            elif key in INT_KEYS:
                try:
                    n = int(float(raw))
                except ValueError:
                    raise ValueError(
                        f"{key}: expected a whole number"
                    )

                if key in {"Workshop.CacheLimit", "Canvas.DiskCacheLimit"}:
                    n = max(0, min(10000, n))
                elif key == "Canvas.SafetyLevel":
                    n = max(0, min(5, n))
                elif key == "Condo.MaxBackups":
                    n = max(0, min(500, n))
                elif key == "Libretro.ResolutionScale":
                    n = max(0, min(8, n))

                changes[key] = str(n)
            else:
                changes[key] = raw

        return changes

    def collect_user_settings_changes(self):
        changes = {}

        # Resolution / monitor / scalar values.
        for key, var in self.gus_vars.items():
            if isinstance(var, tk.BooleanVar):
                changes[key] = "True" if var.get() else "False"
                continue

            raw = str(var.get()).strip()
            if key in {
                "ResolutionSizeX",
                "ResolutionSizeY",
                "MonitorIndex",
                "HDRDisplayOutputNits",
                "WindowPosX",
                "WindowPosY",
                "AudioQualityLevel",
                "DesiredScreenWidth",
                "DesiredScreenHeight",
            }:
                try:
                    value = int(float(raw))
                except ValueError:
                    raise ValueError(f"GameUserSettings {key}: expected a whole number")

                if key == "ResolutionSizeX":
                    value = max(640, min(7680, value))
                elif key == "ResolutionSizeY":
                    value = max(480, min(4320, value))
                elif key == "MonitorIndex":
                    value = max(0, min(15, value))
                elif key == "HDRDisplayOutputNits":
                    value = max(100, min(4000, value))
                elif key in {"WindowPosX", "WindowPosY"}:
                    value = max(-1, min(10000, value))
                elif key == "AudioQualityLevel":
                    value = max(0, min(4, value))
                elif key == "DesiredScreenWidth":
                    value = max(640, min(7680, value))
                elif key == "DesiredScreenHeight":
                    value = max(480, min(4320, value))

                changes[key] = str(value)
            elif key == "sg.ResolutionQuality":
                try:
                    value = max(25.0, min(200.0, float(raw)))
                except ValueError:
                    raise ValueError("Resolution quality must be a number")
                changes[key] = f"{value:.6f}"
            elif key.startswith("sg."):
                try:
                    value = max(0, min(4, int(float(raw))))
                except ValueError:
                    raise ValueError(f"{key}: expected 0 to 4")
                changes[key] = str(value)
            else:
                changes[key] = raw

        mode = self.display_mode.get()
        if mode in DISPLAY_MODE_LABELS:
            changes["FullscreenMode"] = DISPLAY_MODE_LABELS[mode]

        return changes

    # -------------------------------------------- Random Text Hat monitor --
    def _update_text_hat_pool_status(self):
        if not hasattr(self, "text_hat_pool_status"):
            return
        total = len(getattr(self, "text_hat_preset_paths", {}))
        if not self.text_hat_random_pool:
            self.text_hat_pool_status.set(f"Pool: all saved presets ({total})")
            return
        eligible = sum(
            1 for path in self.text_hat_preset_paths.values()
            if Path(path).name in self.text_hat_random_pool
        )
        self.text_hat_pool_status.set(f"Pool: {eligible} selected preset(s)")

    def _eligible_text_hat_presets(self):
        self.refresh_text_hat_preset_list()
        candidates = []
        use_all = not self.text_hat_random_pool
        for display_name, path in self.text_hat_preset_paths.items():
            if not use_all and Path(path).name not in self.text_hat_random_pool:
                continue
            data = self._read_text_hat_preset_data(path)
            if data is not None:
                candidates.append((display_name, path, data))
        return candidates

    def choose_text_hat_random_pool(self):
        self.refresh_text_hat_preset_list()
        items = list(self.text_hat_preset_paths.items())
        if not items:
            messagebox.showinfo(APP_NAME, "Save or import Text Hat presets first.")
            return

        win = tk.Toplevel(self)
        win.title(f"{APP_NAME} - Text Hat Random Pool")
        win.transient(self)
        win.geometry("560x470")
        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        ttk.Label(
            frame,
            text=(
                "Choose which saved Text Hat presets may be selected at random. "
                "At least two are recommended for session randomizing."
            ),
            wraplength=500,
            justify="left",
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        lb = tk.Listbox(frame, selectmode="multiple", exportselection=False)
        lb.grid(row=1, column=0, columnspan=3, sticky="nsew")
        for display_name, path in items:
            lb.insert(tk.END, display_name)
        if not self.text_hat_random_pool:
            lb.selection_set(0, tk.END)
        else:
            for idx, (_name, path) in enumerate(items):
                if Path(path).name in self.text_hat_random_pool:
                    lb.selection_set(idx)

        def select_all():
            lb.selection_set(0, tk.END)

        def save_pool():
            selected = list(lb.curselection())
            if not selected:
                messagebox.showwarning(APP_NAME, "Select at least one preset for the pool.", parent=win)
                return
            if len(selected) == len(items):
                self.text_hat_random_pool = set()  # empty means all
            else:
                self.text_hat_random_pool = {
                    Path(items[i][1]).name for i in selected
                }
            self._save_tool_settings()
            self._update_text_hat_pool_status()
            win.destroy()
            self.status.set("Text Hat random pool updated.")

        ttk.Button(frame, text="Select all", command=select_all).grid(row=2, column=0, sticky="w", pady=(10, 0))
        ttk.Button(frame, text="Use selection", command=save_pool).grid(row=2, column=1, padx=(8, 0), pady=(10, 0))
        ttk.Button(frame, text="Cancel", command=win.destroy).grid(row=2, column=2, padx=(8, 0), pady=(10, 0))
        self._apply_tk_widget_theme(win, {
            "bg": "#21151D" if self.ui_theme == "angel" else "#F0F0F0",
            "field": "#FFF1F5" if self.ui_theme == "angel" else "#FFFFFF",
            "field_fg": "#3B1E2A" if self.ui_theme == "angel" else "#202020",
            "selection": "#F2A1BE" if self.ui_theme == "angel" else "#0078D7",
            "selection_fg": "#2D1720" if self.ui_theme == "angel" else "#FFFFFF",
        }, self.ui_theme == "angel")

    def _toggle_random_text_hat_monitor(self):
        if self.random_text_hat_enabled.get():
            self.refresh_text_hat_preset_list()

            eligible = self._eligible_text_hat_presets()
            if len(eligible) < 2:
                self.random_text_hat_enabled.set(False)
                self.random_text_hat_status.set(
                    "Off - at least 2 presets are required in the random pool"
                )
                messagebox.showwarning(
                    APP_NAME,
                    "Random Text Hat needs at least two eligible presets in its random pool."
                )
                return

            # Start monitoring only now. Nothing is scheduled while the option is off.
            self._random_text_hat_saw_game = is_tower_running()
            if self._random_text_hat_saw_game:
                self.random_text_hat_status.set(
                    "On - Tower Unite detected; waiting for it to close"
                )
            else:
                self.random_text_hat_status.set(
                    "On - waiting for Tower Unite to start"
                )

            self._schedule_random_text_hat_monitor()
        else:
            self._stop_random_text_hat_monitor()
            self.random_text_hat_status.set(
                "Off - no background monitoring"
            )
            self.status.set(
                "Random Text Hat disabled. No background monitoring is running."
            )

    def _schedule_random_text_hat_monitor(self):
        if not self.random_text_hat_enabled.get():
            return
        if self._random_text_hat_monitor_job is not None:
            return

        self._random_text_hat_monitor_job = self.after(
            3000,
            self._poll_random_text_hat_monitor,
        )

    def _stop_random_text_hat_monitor(self):
        job = self._random_text_hat_monitor_job
        self._random_text_hat_monitor_job = None
        self._random_text_hat_saw_game = False

        if job is not None:
            try:
                self.after_cancel(job)
            except Exception:
                pass

    def _poll_random_text_hat_monitor(self):
        # This callback exists only while the option is enabled.
        self._random_text_hat_monitor_job = None

        if not self.random_text_hat_enabled.get():
            return

        running = is_tower_running()

        if running:
            if not self._random_text_hat_saw_game:
                self._random_text_hat_saw_game = True
                self.random_text_hat_status.set(
                    "On - Tower Unite is running"
                )

        elif self._random_text_hat_saw_game:
            # A running -> stopped transition means one game session just ended.
            self._random_text_hat_saw_game = False
            self.random_text_hat_status.set(
                "On - game closed; choosing next Text Hat..."
            )
            self._randomize_text_hat_after_session()

        else:
            self.random_text_hat_status.set(
                "On - waiting for Tower Unite to start"
            )

        self._schedule_random_text_hat_monitor()

    def _read_text_hat_preset_data(self, path):
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:
            return None

        if not isinstance(data, dict) or "text" not in data:
            return None
        return data

    def _choose_random_text_hat_preset(self):
        self.refresh_text_hat_preset_list()

        candidates = self._eligible_text_hat_presets()

        if not candidates:
            return None

        # Prefer a preset that differs from what Game.ini currently contains.
        current_text = self.values.get("Item.TextHatText", "")
        current_color = self.values.get("Item.TextHatColor")

        different = []
        for item in candidates:
            _name, path, data = item
            preset_text = str(data.get("text", ""))

            if "text_color" in data:
                preset_color = data.get("text_color")
                same_color = (
                    (preset_color is None and current_color is None)
                    or preset_color == current_color
                )
                same = preset_text == current_text and same_color
            else:
                same = preset_text == current_text

            if not same:
                different.append(item)

        pool = different or candidates

        # Also avoid selecting the exact same preset twice in a row when possible.
        if self._random_text_hat_last_path is not None and len(pool) > 1:
            filtered = [
                item
                for item in pool
                if Path(item[1]) != Path(self._random_text_hat_last_path)
            ]
            if filtered:
                pool = filtered

        return random.choice(pool)

    def randomize_text_hat_now(self):
        if is_tower_running():
            messagebox.showwarning(
                APP_NAME,
                "Close Tower Unite before randomizing the Text Hat preset."
            )
            return

        result = self._apply_random_text_hat_preset()
        if result:
            name = result
            self.status.set(
                f'Random Text Hat preset "{name}" applied to Game.ini.'
            )
        else:
            self.status.set("No eligible Text Hat preset could be randomized.")

    def _randomize_text_hat_after_session(self):
        # Never write while the game is still running.
        if is_tower_running():
            self.random_text_hat_status.set(
                "On - game is still running; waiting"
            )
            self._random_text_hat_saw_game = True
            return

        result = self._apply_random_text_hat_preset()
        if result:
            self.random_text_hat_status.set(
                f'On - next Text Hat: {result}'
            )
        else:
            self.random_text_hat_status.set(
                "On - could not choose/apply a Text Hat preset"
            )

    def _apply_random_text_hat_preset(self):
        choice = self._choose_random_text_hat_preset()
        if choice is None:
            return None

        display_name, preset_path, data = choice

        p = self.loaded_path
        if not p or not p.exists():
            try:
                p = Path(self.path.get()).expanduser()
            except Exception:
                p = None

        if not p or not p.exists():
            self.status.set(
                "Random Text Hat could not find Game.ini."
            )
            return None

        try:
            text, enc, nl = read_text_preserving(p)
            values = parse_key_values(text)
        except Exception as e:
            self.status.set(f"Random Text Hat could not read Game.ini: {e}")
            return None

        if "Item.TextHatText" not in values:
            self.status.set(
                "Random Text Hat skipped: Item.TextHatText is not in Game.ini."
            )
            return None

        updated = text
        changed = False

        new_text = str(data.get("text", ""))
        next_text, did = replace_key(
            updated,
            "Item.TextHatText",
            new_text,
        )
        if did and next_text != updated:
            changed = True
        updated = next_text

        if "text_color" in data:
            color_value = data.get("text_color")

            if color_value is None:
                if "Item.TextHatColor" in parse_key_values(updated):
                    next_text, did = delete_key(
                        updated,
                        "Item.TextHatColor",
                    )
                    if did and next_text != updated:
                        changed = True
                    updated = next_text

            elif "Item.TextHatColor" in parse_key_values(updated):
                next_text, did = replace_key(
                    updated,
                    "Item.TextHatColor",
                    str(color_value),
                )
                if did and next_text != updated:
                    changed = True
                updated = next_text

        if not changed:
            # The chosen preset already matches the file; still remember it.
            self._random_text_hat_last_path = Path(preset_path)
            self.text_hat_preset_var.set(display_name)
            return display_name

        try:
            self._ensure_original_backup(p)
            self._make_backup_for_path(p, "random_text_hat")
            write_text_preserving(p, updated, enc, nl)
        except Exception as e:
            self.status.set(
                f"Random Text Hat could not save Game.ini: {e}"
            )
            return None

        self._random_text_hat_last_path = Path(preset_path)
        self.text_hat_preset_var.set(display_name)

        # Refresh AngelTune from the just-written file and make that the new baseline.
        self.load_files()
        self.text_hat_preset_var.set(display_name)
        self.update_dashboard()
        return display_name

    def _on_close(self):
        if self.is_dirty:
            leave = messagebox.askyesno(
                APP_NAME,
                "You have unsaved config changes.\n\nExit AngelTune and discard those changes?"
            )
            if not leave:
                return
        self.random_text_hat_enabled.set(False)
        self._stop_random_text_hat_monitor()
        self._save_tool_settings()
        self.destroy()

    # ---------------------------------------------------- Text Hat presets --
    def _text_hat_preset_dir(self, create=False):
        folder = self._preset_dir(create=create) / "TextHat"
        if create:
            folder.mkdir(parents=True, exist_ok=True)
        return folder

    def refresh_text_hat_preset_list(self):
        if not hasattr(self, "text_hat_preset_combo"):
            return

        folders = [self._text_hat_preset_dir(create=False)]
        legacy_folder = self._preset_base_dir() / LEGACY_PRESET_FOLDER_NAME / "TextHat"
        if legacy_folder not in folders:
            folders.append(legacy_folder)

        entries = []
        paths = {}

        for folder in folders:
            if not folder.exists():
                continue

            for path in sorted(folder.glob("*.json"), key=lambda p: p.name.lower()):
                display_name = path.stem
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(data, dict) and data.get("name"):
                        display_name = str(data["name"])
                except Exception:
                    pass

                unique_name = display_name
                n = 2
                while unique_name in paths:
                    unique_name = f"{display_name} ({n})"
                    n += 1

                paths[unique_name] = path
                entries.append(unique_name)

        self.text_hat_preset_paths = paths
        self.text_hat_preset_combo["values"] = entries

        current = self.text_hat_preset_var.get()
        if current not in paths:
            self.text_hat_preset_var.set(entries[0] if entries else "")
        self._update_text_hat_pool_status()

    def save_text_hat_preset(self):
        var = self.vars.get("Item.TextHatText")
        if var is None:
            return

        current_text = str(var.get())

        name = simpledialog.askstring(
            APP_NAME,
            "Text Hat preset name:",
            parent=self,
        )
        if name is None:
            return

        name = name.strip()
        if not name:
            messagebox.showwarning(APP_NAME, "Please enter a preset name.")
            return

        folder = self._text_hat_preset_dir(create=True)
        path = folder / self._safe_preset_filename(name)

        if path.exists():
            if not messagebox.askyesno(
                APP_NAME,
                f'A Text Hat preset named "{name}" already exists.\\n\\nOverwrite it?'
            ):
                return

        color_row = self.color_rows.get("Item.TextHatColor")
        current_color = color_row.value() if color_row is not None else None

        data = {
            "schema_version": 2,
            "type": "text_hat_text_color",
            "name": name,
            "text": current_text,
            "text_color": current_color,
            "saved_at": datetime.now().isoformat(timespec="seconds"),
            "created_with": APP_VERSION,
        }

        try:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            messagebox.showerror(
                APP_NAME,
                f"Could not save Text Hat preset:\\n{e}"
            )
            return

        self.refresh_text_hat_preset_list()

        for display_name, preset_path in self.text_hat_preset_paths.items():
            try:
                if preset_path.resolve() == path.resolve():
                    self.text_hat_preset_var.set(display_name)
                    break
            except Exception:
                pass

        self.status.set(f'Text Hat preset "{name}" saved.')

    def apply_text_hat_preset(self):
        name = self.text_hat_preset_var.get().strip()
        path = self.text_hat_preset_paths.get(name)

        if not path:
            self.status.set("No Text Hat preset selected.")
            return

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            messagebox.showerror(
                APP_NAME,
                f"Could not read Text Hat preset:\\n{e}"
            )
            return

        if not isinstance(data, dict) or "text" not in data:
            messagebox.showerror(
                APP_NAME,
                "The selected Text Hat preset is invalid."
            )
            return

        var = self.vars.get("Item.TextHatText")
        if var is None:
            return

        var.set(str(data.get("text", "")))

        # v1.16+ presets can also carry the Text Hat color. Older v1.15
        # text-only presets deliberately leave the current color untouched.
        if "text_color" in data:
            color_row = self.color_rows.get("Item.TextHatColor")
            if color_row is not None:
                color_value = data.get("text_color")
                if color_value is None:
                    color_row.load_as_game_default()
                elif isinstance(color_value, str):
                    color_row.load(color_value)

        try:
            self.text_hat_entry.focus_set()
            self.text_hat_entry.icursor(tk.END)
        except Exception:
            pass

        self._mark_dirty()
        self.status.set(
            f'Text Hat preset "{data.get("name", name)}" loaded '
            "(text + color when stored). Click Save changes to write it to Game.ini."
        )

    def delete_text_hat_preset(self):
        name = self.text_hat_preset_var.get().strip()
        path = self.text_hat_preset_paths.get(name)

        if not path:
            self.status.set("No Text Hat preset selected.")
            return

        if not messagebox.askyesno(
            APP_NAME,
            f'Delete Text Hat preset "{name}"?'
        ):
            return

        try:
            path.unlink()
        except Exception as e:
            messagebox.showerror(
                APP_NAME,
                f"Could not delete Text Hat preset:\\n{e}"
            )
            return

        self.refresh_text_hat_preset_list()
        self.status.set(f'Text Hat preset "{name}" deleted.')

    # -------------------------------------------------------------- presets --
    def _preset_base_dir(self):
        if self.loaded_path and self.loaded_path.exists():
            return self.loaded_path.parent
        if self.loaded_user_settings_path and self.loaded_user_settings_path.exists():
            return self.loaded_user_settings_path.parent

        for raw in (self.path.get(), self.user_settings_path.get()):
            try:
                candidate = Path(raw).expanduser()
                if candidate.parent.exists():
                    return candidate.parent
            except Exception:
                pass

        return DEFAULT_PATH.parent

    def _preset_dir(self, create=False):
        folder = self._preset_base_dir() / PRESET_FOLDER_NAME
        if create:
            folder.mkdir(parents=True, exist_ok=True)
        return folder

    def _safe_preset_filename(self, name):
        cleaned = re.sub(r'[<>:"/\\\\|?*]+', "_", str(name)).strip().rstrip(". ")
        cleaned = re.sub(r"\\s+", " ", cleaned)
        if not cleaned:
            cleaned = "Preset"
        return cleaned[:80] + ".json"

    def refresh_preset_list(self):
        if not hasattr(self, "preset_combo"):
            return

        folders = [self._preset_dir(create=False)]
        legacy_folder = self._preset_base_dir() / LEGACY_PRESET_FOLDER_NAME
        if legacy_folder not in folders:
            folders.append(legacy_folder)

        entries = []
        paths = {}

        for folder in folders:
            if not folder.exists():
                continue

            for path in sorted(folder.glob("*.json"), key=lambda p: p.name.lower()):
                display_name = path.stem
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(data, dict) and data.get("name"):
                        display_name = str(data["name"])
                except Exception:
                    pass

                # Keep duplicate display names distinguishable.
                unique_name = display_name
                n = 2
                while unique_name in paths:
                    unique_name = f"{display_name} ({n})"
                    n += 1

                paths[unique_name] = path
                entries.append(unique_name)

        self.preset_paths = paths
        self.preset_combo["values"] = entries

        current = self.preset_var.get()
        if current not in paths:
            self.preset_var.set(entries[0] if entries else "")

    def _capture_preset_state(self):
        colors = {}
        for key, row in self.color_rows.items():
            colors[key] = row.value()

        normal_vars = {}
        for key, var in self.vars.items():
            try:
                normal_vars[key] = var.get()
            except Exception:
                pass

        gus_vars = {}
        for key, var in self.gus_vars.items():
            try:
                gus_vars[key] = var.get()
            except Exception:
                pass

        volumes = {}
        for key, var in self.volume_vars.items():
            try:
                volumes[key] = float(var.get())
            except Exception:
                pass

        regions = {
            key: bool(var.get())
            for key, var in self.region_vars.items()
        }

        return {
            "schema_version": PRESET_SCHEMA_VERSION,
            "created_with": APP_VERSION,
            "hud_style": self.hud_style.get(),
            "display_mode": self.display_mode.get(),
            "resolution_preset": self.resolution_preset.get(),
            "colors": colors,
            "game_vars": normal_vars,
            "game_user_settings_vars": gus_vars,
            "volumes_percent": volumes,
            "region_filters": regions,
        }

    def save_current_preset(self):
        if not self.loaded_path and not self.loaded_user_settings_path:
            messagebox.showwarning(
                APP_NAME,
                "Load Game.ini and/or GameUserSettings.ini before creating a preset."
            )
            return

        name = simpledialog.askstring(
            APP_NAME,
            "Preset name:",
            parent=self,
        )
        if name is None:
            return

        name = name.strip()
        if not name:
            messagebox.showwarning(APP_NAME, "Please enter a preset name.")
            return

        folder = self._preset_dir(create=True)
        filename = self._safe_preset_filename(name)
        path = folder / filename

        if path.exists():
            if not messagebox.askyesno(
                APP_NAME,
                f'A preset named "{name}" already exists.\\n\\nOverwrite it?'
            ):
                return

        data = self._capture_preset_state()
        data["name"] = name
        data["saved_at"] = datetime.now().isoformat(timespec="seconds")

        try:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not save preset:\\n{e}")
            return

        self.refresh_preset_list()

        # Select the just-saved preset even if its sanitized filename differs.
        for display_name, preset_path in self.preset_paths.items():
            try:
                if preset_path.resolve() == path.resolve():
                    self.preset_var.set(display_name)
                    break
            except Exception:
                pass

        self.status.set(f'Preset "{name}" saved.')
        messagebox.showinfo(
            APP_NAME,
            f'Preset "{name}" saved.\\n\\n'
            "It stores the editable values currently shown in the tool."
        )

    def _set_tk_var_from_preset(self, var, value):
        try:
            if isinstance(var, tk.BooleanVar):
                if isinstance(value, str):
                    var.set(value.strip().lower() == "true")
                else:
                    var.set(bool(value))
            else:
                var.set(value)
        except Exception:
            pass

    def apply_selected_preset(self):
        name = self.preset_var.get().strip()
        path = self.preset_paths.get(name)

        if not path:
            if name:
                self.refresh_preset_list()
                path = self.preset_paths.get(self.preset_var.get())
            if not path:
                self.status.set("No preset selected.")
                return

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not read preset:\\n{e}")
            return

        if not isinstance(data, dict):
            messagebox.showerror(APP_NAME, "The selected preset is invalid.")
            return

        style = data.get("hud_style")
        if style in HUD_STYLES:
            self.hud_style.set(style)
            self._update_hud_preview()

        display_mode = data.get("display_mode")
        if isinstance(display_mode, str) and display_mode:
            self.display_mode.set(display_mode)

        resolution_preset = data.get("resolution_preset")
        if isinstance(resolution_preset, str) and resolution_preset:
            self.resolution_preset.set(resolution_preset)

        for key, value in data.get("game_vars", {}).items():
            var = self.vars.get(key)
            if var is not None:
                self._set_tk_var_from_preset(var, value)

        for key, value in data.get("game_user_settings_vars", {}).items():
            var = self.gus_vars.get(key)
            if var is not None:
                self._set_tk_var_from_preset(var, value)

        for key, value in data.get("volumes_percent", {}).items():
            var = self.volume_vars.get(key)
            if var is None:
                continue
            try:
                pct = max(0.0, min(100.0, float(value)))
                var.set(pct)
                if key in self.volume_value_labels:
                    if abs(pct - round(pct)) < 0.0001:
                        shown = f"{int(round(pct))}%"
                    else:
                        shown = f"{pct:.1f}%"
                    self.volume_value_labels[key].set(shown)
            except Exception:
                pass

        for key, value in data.get("region_filters", {}).items():
            var = self.region_vars.get(key)
            if var is not None:
                var.set(bool(value))

        for key, value in data.get("colors", {}).items():
            row = self.color_rows.get(key)
            if row is None:
                continue
            if value is None:
                row.load_as_game_default()
            elif isinstance(value, str):
                row.load(value)

        # Keep dependent UI elements synced.
        try:
            x = str(self.gus_vars["ResolutionSizeX"].get()).strip()
            y = str(self.gus_vars["ResolutionSizeY"].get()).strip()
            if x and y:
                self.resolution_preset.set(f"{x} x {y}")
        except Exception:
            pass

        self._mark_dirty()
        self.status.set(
            f'Preset "{data.get("name", name)}" loaded into the editor. '
            "Click Save changes to write it to the INI files."
        )

    def delete_selected_preset(self):
        name = self.preset_var.get().strip()
        path = self.preset_paths.get(name)
        if not path:
            self.status.set("No preset selected.")
            return

        if not messagebox.askyesno(
            APP_NAME,
            f'Delete preset "{name}"?'
        ):
            return

        try:
            path.unlink()
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not delete preset:\\n{e}")
            return

        self.refresh_preset_list()
        self.status.set(f'Preset "{name}" deleted.')

    def _preset_import_summary(self, data, fallback_name="Preset"):
        preset_type = str(data.get("type", "")).strip()
        name = str(data.get("name") or fallback_name)
        created_with = str(data.get("created_with", "unknown"))
        share = data.get("share_pack", {}) if isinstance(data.get("share_pack"), dict) else {}

        lines = [f"Name: {name}"]
        if preset_type in {"text_hat_text", "text_hat_text_color"}:
            lines.append("Type: Text Hat preset")
            lines.append(f"Text: {str(data.get('text', ''))[:120]}")
            lines.append("Stored color: yes" if "text_color" in data else "Stored color: no")
        else:
            lines.append("Type: Full AngelTune preset")
            counts = [
                ("Game settings", len(data.get("game_vars", {}))),
                ("GameUserSettings", len(data.get("game_user_settings_vars", {}))),
                ("Colors", len(data.get("colors", {}))),
                ("Volumes", len(data.get("volumes_percent", {}))),
                ("Regions", len(data.get("region_filters", {}))),
            ]
            lines.extend(f"{label}: {count}" for label, count in counts if count)
            if data.get("hud_style"):
                lines.append(f"HUD style: {data.get('hud_style')}")
            if data.get("display_mode"):
                lines.append(f"Display mode: {data.get('display_mode')}")
        lines.append(f"Created with: {created_with}")
        if share:
            if share.get("author"):
                lines.append(f"Shared by: {share.get('author')}")
            if share.get("description"):
                lines.append(f"Description: {share.get('description')}")
            if share.get("exported_with"):
                lines.append(f"Exported with AngelTune {share.get('exported_with')}")
        return "\n".join(lines)

    def _export_preset_path(self, source_path, display_name):
        if not source_path or not Path(source_path).exists():
            messagebox.showinfo(APP_NAME, "Select a preset to export first.")
            return
        try:
            data = json.loads(Path(source_path).read_text(encoding="utf-8"))
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not read preset:\n{e}")
            return
        if not isinstance(data, dict):
            messagebox.showerror(APP_NAME, "The selected preset is not valid JSON.")
            return

        author = simpledialog.askstring(
            APP_NAME,
            "Optional name/author for the Share Pack (Cancel = blank):",
            parent=self,
        )
        if author is None:
            author = ""
        description = simpledialog.askstring(
            APP_NAME,
            "Optional short description (Cancel = blank):",
            parent=self,
        )
        if description is None:
            description = ""

        export_data = dict(data)
        export_data["share_pack"] = {
            "format": "AngelTune Share Pack",
            "exported_with": APP_VERSION,
            "exported_at": datetime.now().isoformat(timespec="seconds"),
            "author": author.strip(),
            "description": description.strip(),
        }

        suggested = self._safe_preset_filename(display_name).replace(".json", "_AngelTune.json")
        destination = filedialog.asksaveasfilename(
            title="Export AngelTune Share Pack",
            defaultextension=".json",
            initialfile=suggested,
            filetypes=[("AngelTune preset", "*.json"), ("All files", "*.*")],
        )
        if not destination:
            return
        try:
            Path(destination).write_text(
                json.dumps(export_data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not export preset:\n{e}")
            return
        self.status.set(f'Exported Share Pack "{display_name}".')
        messagebox.showinfo(APP_NAME, "AngelTune Share Pack exported successfully.")

    def export_selected_preset(self):
        name = self.preset_var.get().strip()
        path = self.preset_paths.get(name)
        self._export_preset_path(path, name or "Preset")

    def export_selected_text_hat_preset(self):
        name = self.text_hat_preset_var.get().strip()
        path = self.text_hat_preset_paths.get(name)
        self._export_preset_path(path, name or "TextHat")

    def import_preset_file(self):
        selected = filedialog.askopenfilename(
            title="Import AngelTune preset",
            filetypes=[
                ("AngelTune / JSON preset", "*.json"),
                ("All files", "*.*"),
            ],
        )
        if not selected:
            return
        source = Path(selected)
        try:
            data = json.loads(source.read_text(encoding="utf-8"))
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not read preset JSON:\n{e}")
            return
        if not isinstance(data, dict):
            messagebox.showerror(APP_NAME, "This file is not a valid AngelTune preset.")
            return

        preset_type = str(data.get("type", "")).strip()
        if preset_type in {"text_hat_text", "text_hat_text_color"}:
            if "text" not in data:
                messagebox.showerror(APP_NAME, "This Text Hat preset is missing its text value.")
                return
            destination_dir = self._text_hat_preset_dir(create=True)
            is_text_hat = True
        else:
            known_sections = {
                "hud_style",
                "display_mode",
                "resolution_preset",
                "colors",
                "game_vars",
                "game_user_settings_vars",
                "volumes_percent",
                "region_filters",
            }
            if not any(key in data for key in known_sections):
                messagebox.showerror(
                    APP_NAME,
                    "This JSON file does not look like a compatible AngelTune preset."
                )
                return
            destination_dir = self._preset_dir(create=True)
            is_text_hat = False

        preview = self._preset_import_summary(data, source.stem)
        if not messagebox.askyesno(
            APP_NAME,
            "Preset preview\n\n" + preview + "\n\nImport this preset?"
        ):
            return

        display_name = str(data.get("name") or source.stem).strip() or source.stem
        filename = self._safe_preset_filename(display_name)
        destination = destination_dir / filename
        if destination.exists():
            if not messagebox.askyesno(
                APP_NAME,
                f'A preset named "{display_name}" already exists.\n\nOverwrite it?'
            ):
                return
        try:
            destination.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not import preset:\n{e}")
            return

        if is_text_hat:
            self.refresh_text_hat_preset_list()
            for name, path in self.text_hat_preset_paths.items():
                try:
                    if path.resolve() == destination.resolve():
                        self.text_hat_preset_var.set(name)
                        break
                except Exception:
                    pass
            self.status.set(f'Imported Text Hat preset "{display_name}".')
        else:
            self.refresh_preset_list()
            for name, path in self.preset_paths.items():
                try:
                    if path.resolve() == destination.resolve():
                        self.preset_var.set(name)
                        break
                except Exception:
                    pass
            self.status.set(f'Imported preset "{display_name}". Select Apply to load it.')
        messagebox.showinfo(APP_NAME, f'Preset "{display_name}" imported successfully.')

    def open_preset_folder(self):
        folder = self._preset_dir(create=True)
        try:
            if os.name == "nt":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not open preset folder:\\n{e}")

    def _backup_dir_for_path(self, path: Path):
        backup_dir = path.parent / BACKUP_FOLDER_NAME
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir

    def _original_backup_path(self, path: Path):
        return self._backup_dir_for_path(path) / (path.name + ".angeltune.original.bak")

    def _legacy_original_backup_candidates(self, path: Path):
        return [
            path.parent / LEGACY_BACKUP_FOLDER_NAME / (path.name + ".tuctool.original.bak"),
            path.with_name(path.name + ".tuctool.original.bak"),
        ]

    def _ensure_original_backup(self, path: Path):
        target = self._original_backup_path(path)
        if target.exists():
            return target

        # Preserve the earliest known original backup from pre-AngelTune builds.
        for legacy in self._legacy_original_backup_candidates(path):
            if legacy.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(legacy, target)
                return target

        shutil.copy2(path, target)
        return target

    def _make_backup_for_path(self, path: Path, kind="manual"):
        if not path or not path.exists():
            raise FileNotFoundError("Config file does not exist.")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self._backup_dir_for_path(path)
        backup = backup_dir / (path.name + f".angeltune.{kind}.{ts}.bak")
        shutil.copy2(path, backup)
        return backup

    def open_backup_folder(self):
        source = self.loaded_path or self.loaded_user_settings_path

        if source and source.exists():
            folder = self._backup_dir_for_path(source)
        else:
            folder = DEFAULT_PATH.parent / BACKUP_FOLDER_NAME
            folder.mkdir(parents=True, exist_ok=True)

        try:
            if os.name == "nt":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not open backup folder:\\n{e}")

    def _make_backup(self, kind="manual"):
        if not self.loaded_path:
            raise FileNotFoundError("Load a Game.ini first.")
        return self._make_backup_for_path(self.loaded_path, kind)

    def create_manual_backup(self):
        paths = [p for p in [self.loaded_path, self.loaded_user_settings_path] if p and p.exists()]
        if not paths:
            messagebox.showwarning(APP_NAME, "Load a config file first.")
            return

        if is_tower_running():
            proceed = messagebox.askyesno(
                APP_NAME,
                "Tower Unite appears to be running.\n\n"
                "For the cleanest backup it is better to close the game first.\n\n"
                "Create the backup anyway?"
            )
            if not proceed:
                return

        backups = []
        try:
            for p in paths:
                backups.append(self._make_backup_for_path(p, "manual"))
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not create backup:\n{e}")
            return

        self.status.set("Manual backup created for: " + ", ".join(p.name for p in paths))
        self.refresh_backup_history()
        self.update_dashboard()
        messagebox.showinfo(
            APP_NAME,
            "Backup created successfully:\n\n" + "\n".join(b.name for b in backups)
        )

    def save_changes(self):
        if not self.loaded_path and not self.loaded_user_settings_path:
            messagebox.showwarning(APP_NAME, "Load Game.ini and/or GameUserSettings.ini first.")
            return

        if is_tower_running():
            proceed = messagebox.askyesno(
                APP_NAME,
                "Tower Unite appears to be running.\n\n"
                "The game may overwrite its config files while it is open.\n"
                "It is safer to close Tower Unite first.\n\n"
                "Save anyway?"
            )
            if not proceed:
                return

        try:
            game_changes = self.collect_changes() if self.loaded_path else {}
            gus_changes = self.collect_user_settings_changes() if self.loaded_user_settings_path else {}
        except ValueError as e:
            messagebox.showerror(APP_NAME, str(e))
            return

        summaries = []
        backups = []
        changed_game_keys, changed_gus_keys = self._changed_editor_keys()

        # ---- Game.ini ----
        if self.loaded_path:
            text = self.original_text
            changed_count = 0
            missing = []
            for key, value in game_changes.items():
                if key not in changed_game_keys:
                    continue
                if value is None:
                    if key not in self.values:
                        continue
                    new_text, did = delete_key(text, key)
                else:
                    if key not in self.values:
                        missing.append(key)
                        continue
                    new_text, did = replace_key(text, key, value)

                if did:
                    if new_text != text:
                        changed_count += 1
                    text = new_text

            if changed_count:
                p = self.loaded_path
                try:
                    self._ensure_original_backup(p)
                    auto_backup = self._make_backup_for_path(p, "auto")
                    write_text_preserving(p, text, self.encoding, self.newline)
                except Exception as e:
                    messagebox.showerror(APP_NAME, f"Could not save Game.ini:\n{e}")
                    return
                backups.append(auto_backup.name)
                self.original_text = text
                self.values = parse_key_values(text)
                self._refresh_info_views()
                self._refresh_emote_id_reference()
                summaries.append(f"Game.ini: {changed_count} change(s)")
                if missing:
                    summaries.append(f"Game.ini skipped {len(missing)} absent key(s)")

        # ---- GameUserSettings.ini ----
        if self.loaded_user_settings_path:
            text = self.user_settings_original_text
            changed_count = 0
            missing = []
            for key, value in gus_changes.items():
                if key not in changed_gus_keys:
                    continue
                if key not in self.user_settings_values:
                    missing.append(key)
                    continue
                new_text, did = replace_key(text, key, value)
                if did:
                    if new_text != text:
                        changed_count += 1
                    text = new_text

            if changed_count:
                p = self.loaded_user_settings_path
                try:
                    self._ensure_original_backup(p)
                    auto_backup = self._make_backup_for_path(p, "auto")
                    write_text_preserving(
                        p,
                        text,
                        self.user_settings_encoding,
                        self.user_settings_newline,
                    )
                except Exception as e:
                    messagebox.showerror(APP_NAME, f"Could not save GameUserSettings.ini:\n{e}")
                    return
                backups.append(auto_backup.name)
                self.user_settings_original_text = text
                self.user_settings_values = parse_key_values(text)
                for key, var in getattr(self, "gus_info_labels", {}).items():
                    var.set(self.user_settings_values.get(key, "—"))
                for key, var in getattr(self, "advanced_gus_labels", {}).items():
                    var.set(self.user_settings_values.get(key, "—"))
                summaries.append(f"GameUserSettings.ini: {changed_count} change(s)")
                if missing:
                    summaries.append(f"GameUserSettings.ini skipped {len(missing)} absent key(s)")

        if not summaries:
            self.status.set("No changes to save.")
            self._set_clean_baseline()
            return

        self.status.set(" | ".join(summaries))
        self._set_clean_baseline()
        self.refresh_backup_history()
        self.update_dashboard()
        messagebox.showinfo(
            APP_NAME,
            "Changes saved.\n\nAutomatic backups created before writing:\n"
            + ("\n".join(backups) if backups else "No file required a backup.")
        )

    def restore_backup(self):
        paths = [p for p in [self.loaded_path, self.loaded_user_settings_path] if p and p.exists()]
        if not paths:
            messagebox.showwarning(APP_NAME, "Load a config file first.")
            return

        if is_tower_running():
            messagebox.showwarning(APP_NAME, "Close Tower Unite before restoring backups.")
            return

        restore_pairs = []
        for p in paths:
            backup_dir = self._backup_dir_for_path(p)

            # AngelTune backups use .angeltune.* in AngelTune_Backups.
            # Older .tuctool.* backups remain restorable from both the legacy
            # backup folder and the config directory.
            candidates = list(backup_dir.glob(p.name + ".angeltune.*.bak"))
            candidates.extend(backup_dir.glob(p.name + ".tuctool.*.bak"))

            legacy_dir = p.parent / LEGACY_BACKUP_FOLDER_NAME
            if legacy_dir.exists():
                candidates.extend(legacy_dir.glob(p.name + ".tuctool.*.bak"))

            candidates.extend(p.parent.glob(p.name + ".tuctool.*.bak"))

            # De-duplicate in case paths ever overlap.
            unique = {str(item.resolve()): item for item in candidates}
            backups = sorted(
                unique.values(),
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            )
            if backups:
                restore_pairs.append((p, backups[0]))

        if not restore_pairs:
            messagebox.showinfo(APP_NAME, "No AngelTune backups were found.")
            return

        detail = "\n".join(f"{p.name}  ←  {b.name}" for p, b in restore_pairs)
        if not messagebox.askyesno(APP_NAME, "Restore the latest backup(s)?\n\n" + detail):
            return

        try:
            for p, backup in restore_pairs:
                if p.exists():
                    self._make_backup_for_path(p, "before_restore")
                shutil.copy2(backup, p)
            self.load_files()
            self.status.set("Restored latest backup(s).")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Restore failed:\n{e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
