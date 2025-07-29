import sys
import shutil
import subprocess
import json
import re
from pathlib import Path
import datetime

def build_package(args):
    root = Path.cwd()

    # 1️⃣ Locate src/package
    src_path = root / "src"
    packages = [p for p in src_path.iterdir() if p.is_dir()]
    if not packages:
        print("❌ No package folder found in src/")
        sys.exit(1)

    package = packages[0]
    init_file = package / "__init__.py"
    if not init_file.exists():
        print(f"❌ {init_file} does not exist")
        sys.exit(1)

    # 2️⃣ Read current version from __init__.py
    content = init_file.read_text()
    version_match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
    if not version_match:
        print("❌ Could not find __version__ in __init__.py")
        sys.exit(1)

    current_version = version_match.group(1)
    print(f"📦 Current version: {current_version}")

    # 3️⃣ Load jpubconfig.json
    config_dir = root / "jadio_config"
    config_file = config_dir / "jpubconfig.json"

    if not config_file.exists():
        print("⚠️  jpubconfig.json not found. Run 'jpub init' first.")
        sys.exit(1)

    with config_file.open("r") as f:
        config = json.load(f)

    last_built_version = config.get("last_built_version")

    # 4️⃣ Compare versions
    if last_built_version == current_version:
        print(f"❌ Version {current_version} was already built. Please bump the version first.")
        sys.exit(1)

    # 5️⃣ Clean old build artifacts
    print("🛠️  Cleaning old builds...")
    for folder in ["dist", "build"]:
        target = root / folder
        if target.exists():
            shutil.rmtree(target)
            print(f"🗑️  Removed {target}")

    for egg_info in root.glob("*.egg-info"):
        shutil.rmtree(egg_info)
        print(f"🗑️  Removed {egg_info}")

    # 6️⃣ Run build
    try:
        print("🚀 Running: python -m build")
        subprocess.run([sys.executable, "-m", "build"], check=True)
        print("✅ Build complete!")
    except subprocess.CalledProcessError:
        print("❌ Build failed. Make sure you have 'build' installed.")
        sys.exit(1)

    # 7️⃣ Update jpubconfig.json
    config["last_built_version"] = current_version
    config["last_updated"] = datetime.datetime.now().isoformat()

    with config_file.open("w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Updated jpubconfig.json with new last_built_version: {current_version}")
