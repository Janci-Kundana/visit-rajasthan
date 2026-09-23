"""Build the homepage facade, then pack it for delivery to the browser."""
import argparse
from pathlib import Path
import shutil
import subprocess

from build_tiles import ROOT, find_blender


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", default=find_blender())
    parser.add_argument("--pack-only", action="store_true", help="Pack an existing raw Blender export")
    args = parser.parse_args()
    if not args.pack_only and not args.blender:
        parser.error("Blender was not found. Set BLENDER_PATH or pass --blender.")
    npx = shutil.which("npx.cmd") or shutil.which("npx")
    if not npx:
        parser.error("Node.js/npm is required for gltfpack.")
    output = ROOT / "blender-output"
    output.mkdir(exist_ok=True)
    if not args.pack_only:
        log_path = output / "hawa-mahal-home.log"
        print(f"Building Hawa Mahal; see {log_path}", flush=True)
        with log_path.open("w", encoding="utf-8") as log:
            subprocess.run([
                args.blender, "--background", "--threads", "6", "--python-exit-code", "1",
                "--python", str(Path(__file__).parent / "hawa_mahal_home.py"),
            ], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    raw = output / "hawa_mahal_home.raw.glb"
    packed = output / "hawa_mahal_home.packed.glb"
    # 16-bit positions preserve 0.7mm detail across the 43m facade. Indexed,
    # quantized attributes reduce both download size and GPU memory use.
    subprocess.run([
        npx, "--yes", "gltfpack@1.2.0", "-i", str(raw), "-o", str(packed),
        "-cc", "-ce", "ext", "-vp", "16", "-vt", "14", "-vn", "12", "-v",
    ], cwd=ROOT, check=True)
    destination = ROOT / "public/models/hawa_mahal_home.glb"
    shutil.copyfile(packed, destination)
    print(f"Homepage model: {destination.stat().st_size / 1024**2:.2f} MiB", flush=True)


if __name__ == "__main__":
    main()
