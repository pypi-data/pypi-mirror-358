import sys
import json
import importlib

def main():
    if len(sys.argv) < 2:
        print("Usage: jdolabs <command> [args...]")
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    try:
        with open("commands.json") as f:
            cmd_map = json.load(f)
    except FileNotFoundError:
        print("❌ commands.json not found.")
        return

    if cmd not in cmd_map:
        print(f"❌ Unknown command: {cmd}")
        return

    try:
        module_name = f"commands.{cmd_map[cmd]}"
        module = importlib.import_module(module_name)
        module.run(args)
    except Exception as e:
        print(f"❌ Failed to run command '{cmd}': {e}")
