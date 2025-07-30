from pathlib import Path
from configparser import ConfigParser
import sys


def create_config():
    """Function to create config file that works in both develop and install modes"""
    config_dir = Path.home() / ".layman_terminal"
    config_file = config_dir / "config"
    
    try:
        config_dir.mkdir(mode=0o700, exist_ok=True)
        
        if not config_file.exists():
            default_config = ConfigParser()
            api_key = input("provide your llm api key (For now layman-terminal just support gemini) - ")
            default_config["DEFAULT"] = {
                "api_key": api_key,
                "llm": "gemini"
            }
            with open(config_file, "w") as f:
                default_config.write(f)
            config_file.chmod(0o600)
            print(f"Created config file: {config_file}", file=sys.stderr)
    except Exception as e:
        print(f"Error creating config: {e}", file=sys.stderr)