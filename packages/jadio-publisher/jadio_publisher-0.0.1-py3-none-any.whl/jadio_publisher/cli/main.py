import sys
import json
import importlib
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("⚠️  No command provided. Try 'jpub help' for usage.")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    # Load commands
    current_dir = Path(__file__).parent
    commands_file = current_dir / "clicommands.json"

    if not commands_file.exists():
        print("❌ Missing clicommands.json. Cannot route commands.")
        sys.exit(1)

    with commands_file.open("r") as f:
        command_map = json.load(f)

    if command not in command_map:
        print(f"❌ Unknown command: '{command}'. Try 'jpub help'.")
        sys.exit(1)

    # ✅ Guard: Only allow init and help without jpubconfig
    if command not in ["init", "help"]:
        config_dir = Path.cwd() / "jadio_config"
        config_file = config_dir / "jpubconfig.json"

        if not config_file.exists():
            print("❓ jpubconfig.json not found in jadio_config/.")
            choice = input("➡️  Would you like to run 'jpub init' now? (y/n): ").strip().lower()
            if choice == "y":
                # Dynamically call init command
                try:
                    init_module = importlib.import_module("jadio_publisher.cli.init")
                    init_func = getattr(init_module, "init_project")
                    init_func([])
                    print("✅ Now ready! Please re-run your command.")
                except Exception as e:
                    print(f"❌ Error running init: {e}")
                sys.exit(0)
            else:
                print("❌ Cannot continue without jpubconfig. Please run 'jpub init' first.")
                sys.exit(1)

    # ✅ Dynamic import and run
    module_name = command_map[command]["module"]
    function_name = command_map[command]["function"]

    try:
        module = importlib.import_module(f"jadio_publisher.cli.{module_name}")
        func = getattr(module, function_name)
        func(args)
    except Exception as e:
        print(f"❌ Error running command '{command}': {e}")
        sys.exit(1)
