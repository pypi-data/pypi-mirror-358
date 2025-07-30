import sys
from .cli import main, spell_word_command

def entrypoint() -> None:
    """Entry point that handles direct word input or passes to CLI."""
    argv = sys.argv[1:]
    
    # If no args, show help
    if not argv:
        main()
        return
    
    # Check if first arg is a flag/option
    if argv[0].startswith('-'):
        main()
        return
    
    # Check if it's a known command
    known_commands = {"interactive", "list"}
    if argv[0] in known_commands:
        main()
        return
    
    # Otherwise, treat as word to spell
    spell_word_command(argv[0])

if __name__ == "__main__":
    entrypoint() 