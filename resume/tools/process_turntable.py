"""Slice the 360° turntable sheet into aligned, transparent frames and pack a sprite atlas.

Run from the repo root:  python3 resume/tools/process_turntable.py
Needs: pip install "rembg[cpu]" pillow numpy

Output: assets/turntable/atlas.webp (frames in a 10x2 grid) + assets/turntable/frames.json
"""
import json
import os
import numpy as np
from PIL import Image
from rembg import new_session, remove

HERE = os.path.join(os.path.dirname(__file__), "..", "assets", "turntable")
SHEET = os.path.join(HERE, "turntable.png")

# Figure columns found by scanning the white background (x0, x1) per row, rows are (y0, y1).
ROWS = [(0, 520), (520, 1024)]
COLS = [
    [(28, 158), (192, 319), (354, 469), (506, 613), (654, 756), (803, 902), (952, 1047), (1104, 1187), (1250, 1332), (1399, 1479)],
    [(42, 136), (205, 306), (373, 480), (543, 655), (710, 825), (881, 992), (1044, 1153), (1204, 1327), (1370, 1496)],
]

# Real viewing angle of each frame (0 = facing camera, 180 = back), estimated from the pose.
# The sheet's spacing is uneven (1-2 nearly identical, 14-17 change only a little),
# so playback is timed by these angles, not by frame index.
# The bottom row on the sheet is shot from the other side (face peeks out on the left),
# so those frames are flipped here: every atlas frame then shows the same turn direction,
# and the page builds 180-360 by mirroring.
ANGLES = [0, 5, 24, 42, 56, 67, 77, 86, 94, 101,
          110, 120, 130, 139, 145, 151, 157, 170, 180]

FW, FH = 192, 512          # frame cell in the atlas
FIG_H = 470                # head-to-feet height inside the cell
BASE_Y = 500               # feet baseline inside the cell
GRID = 10


def main():
    sheet = Image.open(SHEET).convert("RGB")
    session = new_session("isnet-general-use")
    frames = []
    for r, (y0, y1) in enumerate(ROWS):
        for (x0, x1) in COLS[r]:
            pad = 24
            crop = sheet.crop((max(0, x0 - pad), y0, min(sheet.width, x1 + pad), y1))
            cut = np.asarray(remove(crop, session=session)).astype(np.float32)
            a = cut[..., 3] / 255.0
            a[a < 0.06] = 0
            # remove the white fringe: un-mix colour from the white background
            rgb = cut[..., :3]
            safe = np.maximum(a, 0.25)[..., None]
            rgb = np.clip((rgb - (1 - safe) * 255) / safe, 0, 255)
            ys, xs = np.nonzero(a > 0.5)
            top, bottom = ys.min(), ys.max()
            # horizontal centre = mass centre of the legs + torso (stable rotation axis)
            band = (ys > top + (bottom - top) * 0.25)
            cx = xs[band].mean()
            frames.append((rgb, a, top, bottom, cx))

    atlas = Image.new("RGBA", (FW * GRID, FH * 2), (0, 0, 0, 0))
    for i, (rgb, a, top, bottom, cx) in enumerate(frames):
        img = Image.fromarray(np.dstack([rgb, a * 255]).astype(np.uint8), "RGBA")
        s = FIG_H / (bottom - top)
        img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
        ox = round(FW / 2 - cx * s)
        oy = round(BASE_Y - bottom * s)
        cell = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
        cell.alpha_composite(img, (max(ox, 0), max(oy, 0)), (max(-ox, 0), max(-oy, 0)))
        if i >= len(COLS[0]):
            cell = cell.transpose(Image.FLIP_LEFT_RIGHT)
        atlas.paste(cell, ((i % GRID) * FW, (i // GRID) * FH))

    atlas.save(os.path.join(HERE, "atlas.webp"), "WEBP", quality=88, method=6)
    # still front view for reduced motion / no-WebGL
    atlas.crop((0, 0, FW, FH)).save(os.path.join(HERE, "front.webp"), "WEBP", quality=90, method=6)
    meta = {"cols": GRID, "rows": 2, "frameWidth": FW, "frameHeight": FH,
            "baseline": BASE_Y, "figureHeight": FIG_H, "angles": ANGLES,
            "avatar": False}  # set "avatar": true here only for a local preview with assets/avatar.glb
    with open(os.path.join(HERE, "frames.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print("frames:", len(frames), "atlas:", atlas.size)


if __name__ == "__main__":
    main()
