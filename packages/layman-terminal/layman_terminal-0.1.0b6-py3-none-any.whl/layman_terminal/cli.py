import sys
from layman_terminal.agent import TerminalAgent
# from dotenv import load_dotenv
import os
import subprocess
import argparse
from configparser import ConfigParser
from pathlib import Path


CONFIG_DIR = Path.home() / ".layman_terminal"
CONFIG_FILE = CONFIG_DIR / "config"



def load_config(profile="default"):
    """Load config and credentials for a given profile."""
    config = ConfigParser()

    if not CONFIG_FILE.exists():
        raise Exception('Please configure llm api key uisng command - lt-init')
    else:
        config.read(CONFIG_FILE)

    settings = {}
    if profile in config:
        settings.update(config[profile])

    return settings


def main():

    settings = load_config('DEFAULT')

    # load_dotenv()
    api_key = settings.get("api_key")
    terminal_agent = TerminalAgent(api_key)

    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        user_query = input("Enter your request: ")

    response = terminal_agent.process(user_query)
    print(f"COMMAND - {response}")

    exec_cmd = input("Do you want to execute this command? (Y/N): ")
    if exec_cmd.lower() == "y":
        print("\n")
        result = subprocess.run(response, shell=True, capture_output=True, text=True)
        print(result.stdout)

if __name__ == "__main__":
    main()