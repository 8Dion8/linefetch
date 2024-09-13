import os
import re
import subprocess
from datetime import datetime

ZSHPATTERN = re.compile(r'(?P<timestamp>\d+):\d+;(?P<command>.*)')
USERHOME = os.path.expanduser("~")


def load_aliases():
    # Load user-defined aliases from the .zshrc file
    aliases = {}
    zshrc_path = f"{USERHOME}/.zshrc"

    try:
        with open(zshrc_path, 'r') as zshrc_file:
            for line in zshrc_file:
                if line[0] == "#": continue
                alias_match = re.search(r'alias\s+(\w+)=["\']?(.*?)(["\']?)$', line)
                if alias_match:
                    alias_name = alias_match.group(1)
                    alias_value = alias_match.group(2)
                    aliases[alias_name] = alias_value

    except FileNotFoundError:
        print(f"{zshrc_path} not found.")
    except Exception as e:
        print(f"Error reading {zshrc_path}: {e}")

    return aliases


USERALIASES = load_aliases()



def parse_command(command):
    pattern = re.compile(r'^(sudo\s+)?(\w+)(\s+.*)?$')
    match = pattern.match(command)

    if match:
        modifier = match.group(1).strip() if match.group(1) else ""
        cmd = match.group(2)
        args = match.group(3).strip() if match.group(3) else ""
        alias = USERALIASES[cmd] if cmd in USERALIASES else ""

        return (
            modifier,
            cmd,
            alias,
            args.split() if args else []
        )
    return None


def parse_zsh_history(filepath: str = f"{USERHOME}/.zsh_history"):
    entries = []

    with open(filepath, 'r') as file:
        for line in file:
            match = ZSHPATTERN.search(line)
            if match:
                timestamp = int(match.group("timestamp"))
                parsed_timestamp = datetime.fromtimestamp(timestamp)

                command = match.group("command").strip()
                parsed_command = parse_command(command)

                entries.append((parsed_timestamp, parsed_command))

    return entries


