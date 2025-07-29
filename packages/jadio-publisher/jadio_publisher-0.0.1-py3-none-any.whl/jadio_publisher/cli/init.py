import sys
import json
from pathlib import Path

def init_project(args):
    root = Path.cwd()
    config_dir = root / "jadio_config"
    config_file = config_dir / "jpubconfig.json"

    if not config_dir.exists():
        config_dir.mkdir()
        print("✅ Created jadio_config/ folder.")

    if config_file.exists():
        print("⚠️  jpubconfig.json already exists. Skipping.")
        return

    default_config = {
        "last_built_version": None
    }

    with config_file.open("w") as f:
        json.dump(default_config, f, indent=2)

    print("✅ Created jpubconfig.json with defaults.")
