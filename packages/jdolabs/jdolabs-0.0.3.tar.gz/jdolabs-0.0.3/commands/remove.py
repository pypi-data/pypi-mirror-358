import os
import json
import shutil

def run(args):
    if len(args) < 1:
        print("Usage: jdolabs remove <tool>")
        return

    tool = args[0]
    tool_path = f".jdolabs_modules/{tool}"
    config_path = ".jdolabs_modules/jdolabs_config.json"

    if os.path.exists(tool_path):
        shutil.rmtree(tool_path)
        print(f"🗑️ Removed {tool} from .jdolabs_modules/")
    else:
        print(f"⚠️ Tool '{tool}' not found in .jdolabs_modules/")

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
        if tool in config.get("tools", {}):
            del config["tools"][tool]
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            print(f"✅ Removed {tool} from jdolabs_config.json")
