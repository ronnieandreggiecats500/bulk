#!/usr/bin/env python3
"""
bulk_timestamp_crop.py

Keeps each photo at full width (capped to 1054px) minus the bottom 76px,
then stamps a timestamp in the bottom-right corner.
"""

import os
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

# ── CONFIG ────────────────────────────────────────────────────────────────────
INPUT_DIR  = 'input_photos'
OUTPUT_DIR = 'output_photos'

# First photo’s timestamp: 14th February 2024 at your chosen time
START_TIME = datetime(2024, 2, 14, 10, 24, 59)

# Use a real TTF font so it’s bigger—you can swap to any .ttf on your PC
FONT_PATH  = r'C:\Windows\Fonts\arialbd.ttf'
FONT_SIZE  = 48

# Color of the timestamp text:
TEXT_COLOR = 'white'
# ──────────────────────────────────────────────────────────────────────────────

def load_font():
    if FONT_PATH:
        return ImageFont.truetype(FONT_PATH, FONT_SIZE)
    return ImageFont.load_default()

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    files = sorted(f for f in os.listdir(INPUT_DIR)
                   if f.lower().endswith(('.jpg','jpeg','png')))
    n = len(files)
    if n == 0:
        print("❌ No images found in", INPUT_DIR)
        return

    # Spread timestamps evenly over one hour
    interval = timedelta(hours=1) / max(n - 1, 1)
    font = load_font()

    for i, fname in enumerate(files):
        # 1) Open and measure
        img = Image.open(os.path.join(INPUT_DIR, fname))
        w, h = img.size

        # 2) Crop: keep full width up to 1054px, cut bottom 76px
        new_w = min(1054, w)
        new_h = h - 76
        cropped = img.crop((0, 0, new_w, new_h))

        # 3) Compute timestamp for this frame
        ts = START_TIME + interval * i
        text = ts.strftime('%d %b %Y, %H:%M:%S')

        # 4) Draw timestamp in bottom-right (10px margin)
        draw = ImageDraw.Draw(cropped)
        mask = font.getmask(text)
        text_w, text_h = mask.size
        x = new_w - text_w - 10
        y = new_h - text_h - 10
        draw.text((x, y), text, font=font, fill=TEXT_COLOR)

        # 5) Save output
        out_path = os.path.join(OUTPUT_DIR, fname)
        cropped.save(out_path)
        print("✅", fname, "→", out_path)

    print(f"\n🎉 Done! {n} images in '{OUTPUT_DIR}'.")

if __name__ == '__main__':
    main()