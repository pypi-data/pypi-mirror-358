import json
import os

def run(args):
    path = "programs.json"
    if not os.path.exists(path):
        print("❌ programs.json not found.")
        return

    with open(path, "r") as f:
        programs = json.load(f)

    if not programs:
        print("📦 No programs registered in the JDO Labs suite yet.")
        return

    print("📦 JDO Labs Suite — Available Tools\n")
    for name, desc in programs.items():
        print(f"• {name.ljust(14)} – {desc}")
