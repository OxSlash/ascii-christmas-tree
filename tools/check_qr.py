import io
import sys

import zxingcpp
from PIL import Image


def attempt(label, image):
    results = zxingcpp.read_barcodes(image)
    if results:
        for r in results:
            print(f"{label:24s} OK {r.text}")
        return True
    print(f"{label:24s} FAIL")
    return False


for path in sys.argv[1:]:
    base = Image.open(path).convert("RGB")
    print(f"--- {path} {base.size}")
    attempt("original", base)
    for quality in (85, 70, 55, 40):
        buffer = io.BytesIO()
        base.save(buffer, "JPEG", quality=quality)
        buffer.seek(0)
        attempt(f"jpeg q{quality}", Image.open(buffer).convert("RGB"))
    for scale in (0.6, 0.4, 0.3):
        small = base.resize((int(base.width * scale), int(base.height * scale)), Image.LANCZOS)
        attempt(f"scale {scale}", small)
