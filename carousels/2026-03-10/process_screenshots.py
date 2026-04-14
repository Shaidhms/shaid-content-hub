#!/usr/bin/env python3
"""Resize and crop screenshots for carousel embedding."""

import subprocess
import sys

try:
    from PIL import Image
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import Image

import os

SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "reference_screenshots")

def process():
    for fname in os.listdir(SCREENSHOTS_DIR):
        if not fname.endswith(".png"):
            continue
        path = os.path.join(SCREENSHOTS_DIR, fname)
        img = Image.open(path)
        w, h = img.size
        print(f"{fname}: {w}x{h}")

        # Crop to top portion (article header + key content)
        # and resize to max 1080 wide for carousel
        crop_h = min(h, int(w * 0.7))  # roughly 4:3 aspect from top
        img = img.crop((0, 0, w, crop_h))

        # Resize to 1080 wide
        new_w = 1080
        new_h = int(crop_h * (new_w / w))
        img = img.resize((new_w, new_h), Image.LANCZOS)

        out_path = os.path.join(SCREENSHOTS_DIR, f"cropped-{fname}")
        img.save(out_path, quality=90)
        print(f"  -> cropped-{fname}: {new_w}x{new_h}")

if __name__ == "__main__":
    process()
