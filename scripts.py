import subprocess
import sys
import json5

def load_commands(file_path="commands.json5"):
    try:
        with open(file_path, "r") as f:
            return json5.load(f)
    except Exception as e:
        print(f"Error loading commands file: {e}")
        sys.exit(1)

def run_command(command):
    try:
        print(f"Running: {command}")
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}")
        sys.exit(e.returncode)

def main():
    commands = load_commands()
    if len(sys.argv) < 2:
        print("Usage: python scripts.py <command>")
        print("Available commands:")
        for cmd in commands:
            print(f"  - {cmd}")
        sys.exit(1)

    script = sys.argv[1]
    if script in commands:
        run_command(commands[script])
    else:
        print(f"Unknown command: {script}")
        print("Use one of the available commands.")
        sys.exit(1)

if __name__ == "__main__":
    main()
