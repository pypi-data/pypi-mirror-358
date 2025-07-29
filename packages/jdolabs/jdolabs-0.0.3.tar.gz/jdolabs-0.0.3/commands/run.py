import subprocess
import sys
import os

def run(args):
    if len(args) < 1:
        print("Incorrect Usage - Try: jdolabs run <tool> [args...]")
        return

    tool = args[0]
    tool_path = f".jdolabs_modules/{tool}"

    if not os.path.exists(tool_path):
        print(f"❌ Tool '{tool}' not found in .jdolabs_modules/")
        return

    command_args = [sys.executable, "-m", tool] + args[1:]
    subprocess.run(command_args)
