"""Turn the original certificate uploads into clean, web-ready WebP images.

Run from the repo root:  python3 resume/tools/process_certs.py
Needs: pip install pymupdf pillow opencv-python-headless numpy

- PDFs are rendered at 200 dpi (pages that embed a large photo are rendered
  at their native resolution instead, so we don't upscale).
- Photos are straightened/cropped to the certificate edges and white-balanced.
- Personal identifiers (certificate/member/credential numbers, QR codes) are blurred.
- Output: assets/certs/<slug>.webp (long side <= 1600px) and <slug>-thumb.webp (640px wide).
"""
import os
import cv2
import numpy as np
import pymupdf
from PIL import Image, ImageFilter

ROOT = os.path.join(os.path.dirname(__file__), "..", "assets", "certs")
SRC = os.path.join(ROOT, "originals")

# slug: (source file, options)
# blur boxes are (x0, y0, x1, y1) in the rendered page's pixel coordinates.
# quad = 4 corners (TL, TR, BR, BL) of the certificate in a photo, after `pre_crop`.
CERTS = {
    "chartered-tax-professional": ("CTP.pdf", dict(dpi=72, quad=[(22, 22), (2283, 24), (2283, 1640), (22, 1638)],
                                    photo=True, blur=[(1550, 1180, 1815, 1250)])),
    "niat-member": ("CB_JORGE VINCENT C. CORAL.pdf", dict(blur=[(355, 2025, 525, 2085)])),
    "certified-credit-professional": ("CeCP.pdf", dict(dpi=72, pre_crop=(1300, 0, 2674, 1863),
                                       quad=[(50, 18), (1320, 22), (1322, 1842), (72, 1843)], photo=True,
                                       blur=[(1935, 1034, 2250, 1070), (1425, 1460, 1690, 1725)])),
    "xero-advisor": ("Xero Advisor.pdf", {}),
    "xero-payroll": ("Xero Payroll.pdf", {}),
    "quickbooks-online-level-1": ("QBO lvl 1.pdf", {}),
    "quickbooks-online-level-2": ("QBO lvl 2.pdf", {}),
    "quickbooks-online-payroll": ("QBO Payroll.pdf", {}),
    "philippine-taxation": ("Cerificate of Completion - Philippine Taxation for individuals and business.jpg",
                            dict(blur=[(1500, 1280, 1875, 1330)])),
    "financial-statements-audit": ("basic of financial statement audit (EV).jpg",
                                   dict(pre_crop=(0, 10, 776, 559), photo=True)),
    "basic-advanced-excel": ("Basic and Advance Excel (EV).jpg", dict(pre_crop=(2, 2, 1278, 975), photo=True)),
    "datacamp-associate-data-analyst": ("Data Camp_DataAnalystAssociate.pdf", dict(blur=[(1000, 285, 1295, 340)])),
    "data-analytics-learning-challenge": ("DataSense - Data Analytic Challenge.pdf", dict(blur=[(1835, 158, 2115, 207)])),
    "power-bi-crash-course": ("DataSense - PowerBI.pdf", dict(blur=[(1835, 158, 2135, 207)])),
    "power-bi-desktop": ("PowerBi Training (DataSense).pdf", dict(blur=[(1835, 158, 2120, 207)])),
    "python-fundamentals": ("DataSense-Python.pdf", dict(blur=[(1870, 156, 2155, 207)])),
    "mos-excel-associate-training": ("Microsoft excel Associate Training (DataSense).pdf", dict(blur=[(1870, 156, 2155, 207)])),
    "emerson-national-data-challenge": ("Jorge Vincent C. Coral.pdf", dict(blur=[(1232, 1150, 1430, 1203)])),
    "lean-six-sigma-white-belt": ("CLSSWB.pdf", dict(blur=[(1388, 176, 1577, 364), (1243, 830, 1480, 874), (1246, 873, 1484, 917)])),
}


def load(name, dpi):
    path = os.path.join(SRC, name)
    if name.lower().endswith(".pdf"):
        doc = pymupdf.open(path)
        page = doc[0]  # every upload is a single certificate page
        pix = page.get_pixmap(dpi=dpi, alpha=False)
        return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return Image.open(path).convert("RGB")


def blur_boxes(im, boxes):
    for box in boxes:
        region = im.crop(box)
        # pixelate then blur: unreadable but still looks tidy
        w, h = region.size
        small = region.resize((max(1, w // 14), max(1, h // 14)), Image.BILINEAR)
        region = small.resize((w, h), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6))
        im.paste(region, box)
    return im


def straighten(im, quad):
    src = np.float32(quad)
    w = int(max(np.linalg.norm(src[1] - src[0]), np.linalg.norm(src[2] - src[3])))
    h = int(max(np.linalg.norm(src[3] - src[0]), np.linalg.norm(src[2] - src[1])))
    dst = np.float32([(0, 0), (w, 0), (w, h), (0, h)])
    m = cv2.getPerspectiveTransform(src, dst)
    out = cv2.warpPerspective(np.asarray(im), m, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(out)


def clean_scan(im):
    """White-balance the paper to white and stretch contrast so a photo reads like a scan."""
    a = np.asarray(im).astype(np.float32)
    lum = a.mean(axis=2)
    paper = a[lum >= np.percentile(lum, 70)]
    white = np.percentile(paper, 60, axis=0)  # per-channel paper colour
    a = a * (247.0 / np.maximum(white, 1))
    lo = np.percentile(a, 0.8)
    a = (a - lo) * (255.0 / (255.0 - lo))
    a = 255.0 * np.power(np.clip(a, 0, 255) / 255.0, 1.05)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def main():
    for slug, (name, opt) in CERTS.items():
        im = load(name, opt.get("dpi", 200))
        im = blur_boxes(im, opt.get("blur", []))
        if "pre_crop" in opt:
            im = im.crop(opt["pre_crop"])
        if "quad" in opt:
            im = straighten(im, opt["quad"])
        if opt.get("photo"):
            im = clean_scan(im)
        full = im.copy()
        full.thumbnail((1600, 1600), Image.LANCZOS)
        full.save(os.path.join(ROOT, f"{slug}.webp"), "WEBP", quality=84, method=6)
        thumb = im.copy()
        thumb.thumbnail((640, 640 * 3), Image.LANCZOS)
        if thumb.width > 640:
            thumb = thumb.resize((640, round(thumb.height * 640 / thumb.width)), Image.LANCZOS)
        thumb.save(os.path.join(ROOT, f"{slug}-thumb.webp"), "WEBP", quality=80, method=6)
        print(f"{slug:36s} {full.size} thumb {thumb.size}")


if __name__ == "__main__":
    main()
