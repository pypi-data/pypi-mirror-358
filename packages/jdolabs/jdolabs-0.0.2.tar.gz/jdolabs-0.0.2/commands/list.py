import json
import os

def run(args):
    config_path = ".jdolabs_modules/jdolabs_config.json"
    if not os.path.exists(config_path):
        print("No tools installed.")
        return

    with open(config_path, "r") as f:
        config = json.load(f)

    tools = config.get("tools", {})
    if not tools:
        print("No tools installed.")
    else:
        print("📦 Installed tools:")
        for tool in tools:
            print(f" - {tool}")
