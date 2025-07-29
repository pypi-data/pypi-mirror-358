import sys
import re
import json
from pathlib import Path
import datetime

def show_version(args):
    root = Path.cwd()

    # Step 1: Read from __init__.py
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

    content = init_file.read_text()
    version_match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
    if not version_match:
        print("❌ Could not find __version__ in __init__.py")
        sys.exit(1)

    current_version = version_match.group(1)

    # Step 2: Read jpubconfig.json
    config_dir = root / "jadio_config"
    config_file = config_dir / "jpubconfig.json"

    if not config_file.exists():
        print("⚠️  jpubconfig.json not found in jadio_config/. Run 'jpub init' first.")
        sys.exit(1)

    with config_file.open("r") as f:
        config = json.load(f)

    last_built_version = config.get("last_built_version", "N/A")
    last_updated_raw = config.get("last_updated", None)

    if last_updated_raw:
        try:
            last_updated = datetime.datetime.fromisoformat(last_updated_raw)
            formatted_time = last_updated.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            formatted_time = last_updated_raw
    else:
        formatted_time = "N/A"

    # Step 3: Print nicely
    print("\n📦 Jadio Package Info")
    print(f"✔️ Current version in __init__.py: {current_version}")
    print(f"🗂️ Last built version (jpubconfig.json): {last_built_version}")
    print(f"🕑 Last bump/update: {formatted_time}\n")
