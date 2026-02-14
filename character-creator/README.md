# Python GUI Character Creator

A beginner-friendly desktop GUI (Python 3.8+) that matches a modern dark portfolio theme.

## Features

- Two-panel layout
  - Left: live avatar preview
  - Right: generated export code (Python dict)
- Dark theme with teal/cyan accent
- Layered avatar parts (face, hair, eyes, body, accessory)
- Export
  - Save PNG
  - Save JSON

## Setup

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

## Assets

This app loads PNG layers from `assets/`:

- `assets/faces/*.png`
- `assets/hair/*.png`
- `assets/eyes/*.png`
- `assets/bodies/*.png`
- `assets/accessories/*.png` (optional)

### Asset format

- Use **transparent PNGs** (RGBA).
- Keep all layers the **same canvas size** (recommended: `512x512`).
- Layers should be aligned to the same origin so they stack correctly.

### Where to get assets

- Create your own layers in:
  - Krita / Photoshop / GIMP
  - Aseprite (pixel art)
  - Blender renders exported with alpha
- Or use free-to-use sprite bases and ensure licensing allows portfolio/demo use.

## Notes

If no assets are present, the app still runs and uses simple placeholder shapes so you can verify layout/theme.
