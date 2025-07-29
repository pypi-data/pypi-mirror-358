import subprocess
import sys
import json
import os

def run(args):
    if len(args) < 1:
        print("Incorrect Usage - Try: jdolabs install <tool> |or| jdolabs install <tool> --list")
        return

    if args[0] == "--list":
        if not os.path.exists("programs.json"):
            print("❌ programs.json not found.")
            return

        with open("programs.json", "r") as f:
            programs = json.load(f)

        if not programs:
            print("📦 No tools currently available.")
            return

        print("📦 Available tools:\n")
        for name, desc in programs.items():
            print(f"• {name.ljust(14)} – {desc}")
        return

    tool = args[0]
    target_dir = f".jdolabs_modules/{tool}"

    # Ensure required folders exist
    os.makedirs(".jdolabs_modules", exist_ok=True)
    os.makedirs(target_dir, exist_ok=True)

    # Run pip install into the tool's folder
    subprocess.run([
        sys.executable, "-m", "pip", "install", tool,
        "--target", target_dir
    ])

    # Track installed tool
    config_path = ".jdolabs_modules/jdolabs_config.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    config["tools"][tool] = {"installed": True}
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Installed {tool} into .jdolabs_modules/")
