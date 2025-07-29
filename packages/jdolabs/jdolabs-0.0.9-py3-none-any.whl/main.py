import typer
from cli.cli import app as cli_app  # if your CLI app is in cli/cli.py

def main():
    cli_app()

if __name__ == "__main__":
    main()
