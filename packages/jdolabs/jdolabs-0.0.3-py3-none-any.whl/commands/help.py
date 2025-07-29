def run(args):
    print("""
🧪 jdolabs — Universal Tool Installer

Usage:
  jdolabs init
      Initializes jdolabs with .jadiolabs_modules/ and config

  jdolabs install <tool>
      Installs a PyPI tool into the local toolspace

  jdolabs run <tool> [args...]
      Runs the tool with optional arguments

  jdolabs remove <tool>
      Uninstalls a tool and removes from config

  jdolabs list
      Lists all installed tools

  jdolabs help
      Displays this help message
""")
