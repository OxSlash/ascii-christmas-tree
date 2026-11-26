import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "web" / "build" / "web"
PUBLIC = ROOT / "public"
STYLE = (
    "html,body{background:#070a12 !important;margin:0;}"
    "canvas{image-rendering:pixelated;}"
)


def patch_page():
    page = PUBLIC / "index.html"
    html = page.read_text(encoding="utf-8")
    if "ascii-tree-style" in html:
        return
    html = html.replace("</head>", f"<style id=ascii-tree-style>{STYLE}</style>\n</head>", 1)
    page.write_text(html, encoding="utf-8")


def main():
    subprocess.run([sys.executable, "-m", "pygbag", "--build", "web"], cwd=ROOT, check=True)
    if not BUILD.is_dir():
        raise SystemExit(f"pygbag output not found: {BUILD}")
    PUBLIC.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in BUILD.iterdir():
        target = PUBLIC / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)
        count += 1
    patch_page()
    print(f"copied {count} items to {PUBLIC}")


if __name__ == "__main__":
    main()
