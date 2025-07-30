#!/usr/bin/env python3
"""Main entry point for the phonetic CLI."""

import sys
from .cli import spell_word_command, main as cli_main

def main() -> None:
    """Main entry point that handles direct word input."""
    argv = sys.argv[1:]
    
    # If no args, show help
    if not argv:
        cli_main()
        return
    
    # Known subcommands and options
    known_commands = {"interactive", "list"}
    known_options = {"--help", "--version", "-h", "-V"}
    if argv[0] in known_commands or argv[0] in known_options or argv[0].startswith('-'):
        cli_main()
        return
    
    # Otherwise, treat as word to spell
    spell_word_command(argv[0])

if __name__ == "__main__":
    main() 