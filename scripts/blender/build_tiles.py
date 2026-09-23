"""Rebuild the four GLBs, fallback posters, preview renders and editable scenes."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CITIES = ("jaipur", "jaisalmer", "udaipur", "jawai")


def find_blender():
    configured = os.environ.get("BLENDER_PATH") or shutil.which("blender")
    if configured:
        return configured
    candidates = list(Path("C:/Program Files/Blender Foundation").glob("Blender */blender.exe"))
    candidates += [Path("/Applications/Blender.app/Contents/MacOS/Blender")]
    return next((str(p) for p in sorted(candidates, reverse=True) if p.is_file()), None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cities", nargs="*", help="Default: all four destinations")
    parser.add_argument("--blender", default=find_blender(), help="Blender executable; or set BLENDER_PATH")
    args = parser.parse_args()
    if not args.blender:
        parser.error("Blender was not found. Set BLENDER_PATH or pass --blender.")
    cities = args.cities or CITIES
    if any(city not in CITIES for city in cities):
        parser.error("Choose from: " + ", ".join(CITIES))
    output = ROOT / "blender-output"
    output.mkdir(exist_ok=True)
    for city in cities:
        log_path = output / f"{city}-build.log"
        print(f"Building {city}...", flush=True)
        with log_path.open("w", encoding="utf-8") as log:
            result = subprocess.run([
                args.blender, "--background", "--threads", "6", "--python-exit-code", "1",
                "--python", str(Path(__file__).parent / f"{city}_tile.py"),
            ], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            raise SystemExit(f"{city} failed; see {log_path}")
        size = (ROOT / "public/models" / f"{city}_tile.glb").stat().st_size / 1024 ** 2
        print(f"  {city}: {size:.2f} MiB; models, posters and .blend saved", flush=True)


if __name__ == "__main__":
    main()
