import sys
import re
import json
from pathlib import Path
import datetime

def bump_version(args):
    # Locate src/package
    root = Path.cwd()
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

    # Read __init__.py version
    content = init_file.read_text()
    version_match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
    if not version_match:
        print("❌ Could not find __version__ in __init__.py")
        sys.exit(1)

    old_version = version_match.group(1)
    print(f"📦 Current version: {old_version}")

    # Prompt for new version
    new_version = input("✏️  Enter new version: ").strip()
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print("❌ Invalid version format. Use MAJOR.MINOR.PATCH (e.g. 0.0.2)")
        sys.exit(1)

    # Write new version to __init__.py
    new_content = re.sub(
        r'__version__\s*=\s*[\'"][^\'"]+[\'"]',
        f'__version__ = \"{new_version}\"',
        content
    )
    init_file.write_text(new_content)
    print(f"✅ Updated __init__.py to {new_version}")

    # Now update jpubconfig.json
    config_dir = root / "jadio_config"
    config_file = config_dir / "jpubconfig.json"

    if not config_file.exists():
        print("⚠️  No jpubconfig.json found in jadio_config/. Run 'jpub init' first.")
        sys.exit(1)

    with config_file.open("r") as f:
        config = json.load(f)

    config["last_built_version"] = new_version
    config["last_updated"] = datetime.datetime.now().isoformat()

    with config_file.open("w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Updated jpubconfig.json with new version {new_version}")
