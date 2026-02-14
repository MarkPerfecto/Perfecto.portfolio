import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox

from PIL import Image, ImageDraw, ImageTk


ACCENT = "#00ff9d"
BG = "#1a1a1a"
PANEL = "#111111"
PANEL_2 = "#141414"
TEXT = "#e6e6e6"
MUTED = "#a3a3a3"
BORDER = "#262626"

CANVAS_SIZE = 512
PREVIEW_SIZE = 420

ASSET_ROOT = Path(__file__).resolve().parent / "assets"


@dataclass
class CharacterConfig:
    face: str
    hair: str
    eyes: str
    body: str
    accessory: str
    hair_color: str
    created_at: str


def _list_pngs(folder: Path) -> List[str]:
    if not folder.exists():
        return []
    names = [p.name for p in folder.glob("*.png") if p.is_file()]
    names.sort(key=lambda s: s.lower())
    return names


def _safe_open_rgba(path: Path) -> Optional[Image.Image]:
    try:
        img = Image.open(path)
        return img.convert("RGBA")
    except Exception:
        return None


def _tint_alpha_layer(layer: Image.Image, color_hex: str) -> Image.Image:
    r = int(color_hex[1:3], 16)
    g = int(color_hex[3:5], 16)
    b = int(color_hex[5:7], 16)

    base = Image.new("RGBA", layer.size, (r, g, b, 255))
    alpha = layer.split()[-1]
    base.putalpha(alpha)
    return base


def _placeholder_avatar(config: CharacterConfig) -> Image.Image:
    img = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    cx = CANVAS_SIZE // 2
    cy = CANVAS_SIZE // 2 - 10

    body_w = 260
    body_h = 240
    body_top = cy + 80
    body_left = cx - body_w // 2

    body_style = config.body
    if body_style == "Athletic":
        body_w = 300
        body_h = 250
    elif body_style == "Slim":
        body_w = 240
        body_h = 230

    body_box = [cx - body_w // 2, body_top, cx + body_w // 2, body_top + body_h]
    d.rounded_rectangle(body_box, radius=48, fill="#2b2b2b", outline="#3a3a3a", width=4)

    face_style = config.face
    if face_style == "Square":
        face_box = [cx - 120, cy - 130, cx + 120, cy + 110]
        face_radius = 24
    elif face_style == "Heart":
        face_box = [cx - 115, cy - 135, cx + 115, cy + 105]
        face_radius = 64
    else:
        face_box = [cx - 120, cy - 140, cx + 120, cy + 110]
        face_radius = 80

    d.rounded_rectangle(face_box, radius=face_radius, fill="#3a3a3a", outline="#525252", width=4)

    hair_style = config.hair
    hair_color = config.hair_color
    if hair_style == "Long":
        hair_box = [cx - 140, cy - 170, cx + 140, cy + 30]
        d.rounded_rectangle(hair_box, radius=90, fill=hair_color, outline="#0b0b0b", width=2)
    elif hair_style == "Spiky":
        points = [
            (cx - 150, cy - 35),
            (cx - 110, cy - 175),
            (cx - 60, cy - 65),
            (cx - 10, cy - 190),
            (cx + 40, cy - 60),
            (cx + 90, cy - 175),
            (cx + 150, cy - 35),
        ]
        d.polygon(points, fill=hair_color, outline="#0b0b0b")
        d.rounded_rectangle([cx - 150, cy - 35, cx + 150, cy + 10], radius=40, fill=hair_color)
    else:
        hair_box = [cx - 145, cy - 170, cx + 145, cy - 20]
        d.rounded_rectangle(hair_box, radius=90, fill=hair_color, outline="#0b0b0b", width=2)

    eye_style = config.eyes
    if eye_style == "Sharp":
        d.polygon([(cx - 85, cy - 10), (cx - 25, cy - 25), (cx - 25, cy + 5)], fill=ACCENT)
        d.polygon([(cx + 25, cy - 25), (cx + 85, cy - 10), (cx + 25, cy + 5)], fill=ACCENT)
    elif eye_style == "Round":
        d.ellipse([cx - 85, cy - 20, cx - 35, cy + 30], fill=ACCENT)
        d.ellipse([cx + 35, cy - 20, cx + 85, cy + 30], fill=ACCENT)
    else:
        d.rounded_rectangle([cx - 90, cy - 10, cx - 30, cy + 20], radius=12, fill=ACCENT)
        d.rounded_rectangle([cx + 30, cy - 10, cx + 90, cy + 20], radius=12, fill=ACCENT)

    if config.accessory != "None":
        if config.accessory == "Glasses":
            d.rounded_rectangle([cx - 115, cy - 25, cx - 10, cy + 40], radius=16, outline="#d4d4d4", width=4)
            d.rounded_rectangle([cx + 10, cy - 25, cx + 115, cy + 40], radius=16, outline="#d4d4d4", width=4)
            d.line([cx - 10, cy + 5, cx + 10, cy + 5], fill="#d4d4d4", width=4)
        elif config.accessory == "Earring":
            d.ellipse([cx - 140, cy + 20, cx - 110, cy + 50], outline=ACCENT, width=5)
        else:
            d.rounded_rectangle([cx - 70, cy + 70, cx + 70, cy + 95], radius=10, fill="#2b2b2b", outline=ACCENT, width=2)

    return img


class CharacterCreatorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Python GUI Character Creator")
        self.root.configure(bg=BG)
        self.root.minsize(1020, 620)

        self.asset_index = {
            "faces": _list_pngs(ASSET_ROOT / "faces"),
            "hair": _list_pngs(ASSET_ROOT / "hair"),
            "eyes": _list_pngs(ASSET_ROOT / "eyes"),
            "bodies": _list_pngs(ASSET_ROOT / "bodies"),
            "accessories": _list_pngs(ASSET_ROOT / "accessories"),
        }

        self.face_options = self._options_or_fallback(self.asset_index["faces"], ["Oval", "Square", "Heart"])
        self.hair_options = self._options_or_fallback(self.asset_index["hair"], ["Short", "Long", "Spiky"])
        self.eye_options = self._options_or_fallback(self.asset_index["eyes"], ["Round", "Sharp", "Calm"])
        self.body_options = self._options_or_fallback(self.asset_index["bodies"], ["Classic", "Slim", "Athletic"])
        self.acc_options = ["None"] + self._options_or_fallback(self.asset_index["accessories"], ["Glasses", "Earring", "Badge"])

        self.var_face = tk.StringVar(value=self.face_options[0])
        self.var_hair = tk.StringVar(value=self.hair_options[0])
        self.var_eyes = tk.StringVar(value=self.eye_options[0])
        self.var_body = tk.StringVar(value=self.body_options[0])
        self.var_acc = tk.StringVar(value=self.acc_options[0])
        self.var_hair_color = tk.StringVar(value="#6b7280")

        self._preview_img_tk = None  # type: Optional[ImageTk.PhotoImage]
        self._last_composited = None  # type: Optional[Image.Image]

        self._build_layout()
        self._wire_events()
        self.render()

    def _options_or_fallback(self, assets: List[str], fallback: List[str]) -> List[str]:
        return assets if assets else fallback

    def _build_layout(self) -> None:
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True, padx=18, pady=18)

        header = tk.Frame(outer, bg=BG)
        header.pack(fill="x", pady=(0, 14))

        title = tk.Label(
            header,
            text="Python GUI Character Creator",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 18, "bold"),
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text="A beginner-friendly GUI for creating custom characters",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 11),
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        content = tk.Frame(outer, bg=BG)
        content.pack(fill="both", expand=True)

        content.grid_columnconfigure(0, weight=3, uniform="cols")
        content.grid_columnconfigure(1, weight=2, uniform="cols")
        content.grid_rowconfigure(0, weight=1)

        self.left = tk.Frame(content, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        self.left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.right = tk.Frame(content, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        self.right.grid(row=0, column=1, sticky="nsew")

        left_top = tk.Frame(self.left, bg=PANEL)
        left_top.pack(fill="both", expand=True, padx=16, pady=16)

        preview_label = tk.Label(left_top, text="Preview", bg=PANEL, fg=TEXT, font=("Segoe UI", 12, "bold"))
        preview_label.pack(anchor="w")

        preview_box = tk.Frame(left_top, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        preview_box.pack(fill="both", expand=True, pady=(10, 14))

        self.preview = tk.Label(preview_box, bg=PANEL_2)
        self.preview.pack(expand=True, pady=16)

        controls = tk.Frame(left_top, bg=PANEL)
        controls.pack(fill="x")

        self._row_select(controls, 0, "Face", self.var_face, self.face_options)
        self._row_select(controls, 1, "Hair", self.var_hair, self.hair_options)
        self._row_select(controls, 2, "Eyes", self.var_eyes, self.eye_options)
        self._row_select(controls, 3, "Body", self.var_body, self.body_options)
        self._row_select(controls, 4, "Accessory", self.var_acc, self.acc_options)

        color_row = tk.Frame(controls, bg=PANEL)
        color_row.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        color_row.grid_columnconfigure(1, weight=1)

        tk.Label(color_row, text="Hair color", bg=PANEL, fg=MUTED, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")

        self.hair_color_chip = tk.Canvas(color_row, width=26, height=26, bg=PANEL, highlightthickness=0)
        self.hair_color_chip.grid(row=0, column=1, sticky="w", padx=(10, 0))

        self.btn_pick_hair = tk.Button(
            color_row,
            text="Pick",
            bg=PANEL_2,
            fg=TEXT,
            activebackground=PANEL_2,
            activeforeground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            padx=12,
            pady=6,
            command=self.pick_hair_color,
        )
        self.btn_pick_hair.grid(row=0, column=2, sticky="e")

        right_top = tk.Frame(self.right, bg=PANEL)
        right_top.pack(fill="both", expand=True, padx=16, pady=16)

        right_header = tk.Frame(right_top, bg=PANEL)
        right_header.pack(fill="x")

        code_title = tk.Label(right_header, text="Export Code", bg=PANEL, fg=TEXT, font=("Segoe UI", 12, "bold"))
        code_title.pack(side="left")

        btns = tk.Frame(right_header, bg=PANEL)
        btns.pack(side="right")

        self.btn_save_png = tk.Button(
            btns,
            text="Save PNG",
            bg=ACCENT,
            fg="#001b12",
            activebackground=ACCENT,
            activeforeground="#001b12",
            relief="flat",
            padx=12,
            pady=6,
            command=self.export_png,
        )
        self.btn_save_png.pack(side="left", padx=(0, 8))

        self.btn_save_json = tk.Button(
            btns,
            text="Save JSON",
            bg=PANEL_2,
            fg=TEXT,
            activebackground=PANEL_2,
            activeforeground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            padx=12,
            pady=6,
            command=self.export_json,
        )
        self.btn_save_json.pack(side="left")

        self.code = tk.Text(
            right_top,
            bg=PANEL_2,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            font=("Consolas", 10),
            wrap="none",
        )
        self.code.pack(fill="both", expand=True, pady=(12, 0))

        self.code.configure(state="disabled")

        self._draw_color_chip()

    def _row_select(self, parent: tk.Widget, row: int, label: str, var: tk.StringVar, options: List[str]) -> None:
        parent.grid_columnconfigure(1, weight=1)

        tk.Label(parent, text=label, bg=PANEL, fg=MUTED, font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky="w", pady=4
        )

        om = tk.OptionMenu(parent, var, *options)
        om.configure(
            bg=PANEL_2,
            fg=TEXT,
            activebackground=PANEL_2,
            activeforeground=TEXT,
            highlightthickness=1,
            highlightbackground=BORDER,
            relief="flat",
            padx=6,
        )
        om["menu"].configure(bg=PANEL_2, fg=TEXT, activebackground=ACCENT, activeforeground="#001b12")
        om.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=4)

    def _wire_events(self) -> None:
        for v in (self.var_face, self.var_hair, self.var_eyes, self.var_body, self.var_acc):
            v.trace_add("write", lambda *_: self.render())

        self.var_hair_color.trace_add("write", lambda *_: self._draw_color_chip())
        self.var_hair_color.trace_add("write", lambda *_: self.render())

    def _draw_color_chip(self) -> None:
        self.hair_color_chip.delete("all")
        self.hair_color_chip.create_rectangle(2, 2, 24, 24, fill=self.var_hair_color.get(), outline=BORDER, width=2)

    def pick_hair_color(self) -> None:
        color = colorchooser.askcolor(title="Pick hair color", initialcolor=self.var_hair_color.get())
        if not color or not color[1]:
            return
        self.var_hair_color.set(color[1])

    def _build_config(self) -> CharacterConfig:
        return CharacterConfig(
            face=self.var_face.get(),
            hair=self.var_hair.get(),
            eyes=self.var_eyes.get(),
            body=self.var_body.get(),
            accessory=self.var_acc.get(),
            hair_color=self.var_hair_color.get(),
            created_at=datetime.now().isoformat(timespec="seconds"),
        )

    def _load_layer(self, category: str, name: str) -> Optional[Image.Image]:
        folder = ASSET_ROOT / category
        if not folder.exists():
            return None
        path = folder / name
        if not path.exists():
            return None
        return _safe_open_rgba(path)

    def _compose_from_assets(self, config: CharacterConfig) -> Optional[Image.Image]:
        has_any_assets = any(self.asset_index.values())
        if not has_any_assets:
            return None

        base = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))

        face_layer = self._load_layer("faces", config.face)
        body_layer = self._load_layer("bodies", config.body)
        eyes_layer = self._load_layer("eyes", config.eyes)
        hair_layer = self._load_layer("hair", config.hair)

        acc_layer = None
        if config.accessory != "None":
            acc_layer = self._load_layer("accessories", config.accessory)

        layers = [body_layer, face_layer, eyes_layer]

        if hair_layer is not None:
            hair_layer = _tint_alpha_layer(hair_layer, config.hair_color)

        layers.append(hair_layer)
        layers.append(acc_layer)

        for layer in layers:
            if layer is None:
                continue
            if layer.size != base.size:
                layer = layer.resize(base.size, Image.Resampling.LANCZOS)
            base = Image.alpha_composite(base, layer)

        return base

    def render(self) -> None:
        config = self._build_config()

        img = self._compose_from_assets(config)
        if img is None:
            img = _placeholder_avatar(config)

        self._last_composited = img

        preview = img.copy()
        preview.thumbnail((PREVIEW_SIZE, PREVIEW_SIZE), Image.Resampling.LANCZOS)
        self._preview_img_tk = ImageTk.PhotoImage(preview)
        self.preview.configure(image=self._preview_img_tk)

        self._update_code_panel(config)

    def _update_code_panel(self, config: CharacterConfig) -> None:
        cfg = asdict(config)
        cfg.pop("created_at", None)

        py = "character = " + json.dumps(cfg, indent=2)
        py = py.replace("true", "True").replace("false", "False").replace("null", "None")

        self.code.configure(state="normal")
        self.code.delete("1.0", "end")
        self.code.insert("1.0", py)
        self.code.configure(state="disabled")

    def export_png(self) -> None:
        if self._last_composited is None:
            messagebox.showerror("Export failed", "Nothing to export yet.")
            return

        path = filedialog.asksaveasfilename(
            title="Save character PNG",
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            initialfile="character.png",
        )
        if not path:
            return

        try:
            self._last_composited.save(path, format="PNG")
            messagebox.showinfo("Saved", f"Saved PNG to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def export_json(self) -> None:
        config = self._build_config()

        path = filedialog.asksaveasfilename(
            title="Save character JSON",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialfile="character.json",
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(asdict(config), f, indent=2)
            messagebox.showinfo("Saved", f"Saved JSON to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))


def main() -> None:
    root = tk.Tk()
    app = CharacterCreatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
