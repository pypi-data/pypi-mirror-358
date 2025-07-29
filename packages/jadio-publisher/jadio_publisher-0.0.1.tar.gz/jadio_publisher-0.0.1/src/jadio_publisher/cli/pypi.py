import sys
import subprocess
from pathlib import Path

def upload_package(args):
    root = Path.cwd()
    dist_dir = root / "dist"

    if not dist_dir.exists() or not any(dist_dir.iterdir()):
        print("❌ No built distributions found in dist/. Please run 'jpub build' first.")
        sys.exit(1)

    print("🚀 Uploading to PyPI with twine...")
    try:
        subprocess.run([sys.executable, "-m", "twine", "upload", "dist/*"], check=True)
        print("✅ Published to PyPI successfully!")
    except subprocess.CalledProcessError:
        print("❌ Twine upload failed. Make sure you have 'twine' installed and set up.")
        sys.exit(1)
