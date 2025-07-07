import io, zipfile
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# ── CONFIG ────────────────────────────────────────────────────────────────────
DEFAULT_WIDTH    = 1054
DEFAULT_CROP_PX  = 76
DEFAULT_FONT     = r"C:\Windows\Fonts\arialbd.ttf"
DEFAULT_FONT_SZ  = 48
# ──────────────────────────────────────────────────────────────────────────────

st.title("Bulk Photo Crop & Timestamp")

# 1) Upload photos
uploads = st.file_uploader(
    "Upload JPG/PNG photos",
    type=["jpg","jpeg","png"],
    accept_multiple_files=True
)
if not uploads:
    st.info("Please upload at least one image.")
    st.stop()

# 2) Parameters
col1, col2 = st.columns(2)
with col1:
    w = st.number_input("Max width", value=DEFAULT_WIDTH, min_value=1)
    crop_px = st.number_input(
        "Crop pixels from bottom",
        value=DEFAULT_CROP_PX,
        min_value=0
    )
with col2:
    date_sel = st.date_input(
        "Start date",
        value=datetime.now().date()
    )
    time_sel = st.time_input(
        "Start time",
        value=datetime.now().time().replace(microsecond=0)
    )
    start_dt = datetime.combine(date_sel, time_sel)

    font_path = st.text_input("Font path (.ttf)", value=DEFAULT_FONT)
    font_sz   = st.number_input("Font size", value=DEFAULT_FONT_SZ, min_value=1)

if st.button("Process and Download ZIP"):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        interval = timedelta(hours=1) / max(len(uploads)-1, 1)
        font = ImageFont.truetype(font_path, font_sz)

        for i, upload in enumerate(uploads):
            img = Image.open(upload)
            orig_w, orig_h = img.size

            # Crop
            new_w = min(int(w), orig_w)
            new_h = orig_h - int(crop_px)
            cropped = img.crop((0, 0, new_w, new_h))

            # Timestamp
            ts = start_dt + interval * i
            txt = ts.strftime("%d %b %Y, %H:%M:%S")

            draw = ImageDraw.Draw(cropped)
            mask = font.getmask(txt)
            tw, th = mask.size
            x = new_w - tw - 10
            y = new_h - th - 10
            draw.text((x, y), txt, font=font, fill="white")

            # Save to ZIP
            buf = io.BytesIO()
            cropped.save(buf, format="JPEG")
            zf.writestr(Path(upload.name).name, buf.getvalue())

    zip_buffer.seek(0)
    st.download_button(
        "Download ZIP of Edited Photos",
        data=zip_buffer,
        file_name="edited_photos.zip"
    )
