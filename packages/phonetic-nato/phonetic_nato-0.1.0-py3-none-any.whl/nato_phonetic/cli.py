"""Command-line interface for the NATO phonetic alphabet."""

import click
from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED
from rich.panel import Panel
from rich.prompt import Prompt

from .core import spell_word, get_full_alphabet

console = Console()

PROJECT_NAME = "phonetic"
PROJECT_VERSION = "0.1.0"
PROJECT_DESC = (
    "A beautiful CLI for the NATO phonetic alphabet built with "
    "Python, Click, and Rich."
)
PROJECT_AUTHOR = "trtmn <trtmn@trtmn.io>"


class PhoneticGroup(click.Group):
    def format_help(self, ctx: click.Context,
                   formatter: click.HelpFormatter) -> None:
        # Usage section
        console.print(Panel.fit(
            f"{ctx.command_path} [OPTIONS] COMMAND [ARGS]...\n\n"
            "NATO Phonetic Alphabet CLI - Beautiful terminal interface.\n\n"
            "If a word is provided without a command, it will be spelled out using "
            "the NATO phonetic alphabet.",
            border_style="cyan",
            title="Usage"
        ))
        console.print()
        
        # Options section
        console.print(Panel.fit(
            "--version  Show the version and exit.\n"
            "--help     Show this message and exit.",
            border_style="green",
            title="Options"
        ))
        console.print()
        
        # Commands section
        console.print(Panel.fit(
            "interactive  Enter interactive mode\n"
            "list         Show full alphabet",
            border_style="yellow",
            title="Commands"
        ))
        console.print()
        
        # Examples section
        console.print(Panel.fit(
            "[cyan]phonetic 'HELLO'[/cyan]     # Spell out HELLO\n"
            "[cyan]phonetic interactive[/cyan] # Interactive mode\n"
            "[cyan]phonetic list[/cyan]        # Show full alphabet",
            border_style="magenta",
            title="Examples"
        ))


@click.group(cls=PhoneticGroup, invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show the version and exit.')
@click.pass_context
def main(ctx: click.Context, version: bool = False) -> None:
    """NATO Phonetic Alphabet CLI - Beautiful terminal interface.
    
    If a word is provided without a command, it will be spelled out using 
    the NATO phonetic alphabet.
    """
    if version:
        console.print(Panel.fit(
            f"[bold cyan]{PROJECT_NAME}[/bold cyan] [green]v{PROJECT_VERSION}[/green]",
            border_style="cyan",
            title="Version"
        ))
        ctx.exit()
    if ctx.invoked_subcommand is None:
        # Check if there are any arguments that aren't options
        args = [arg for arg in ctx.args if not arg.startswith('-')]
        if args:
            # Treat the first non-option argument as a word to spell
            word = args[0]
            spell_word_command(word)
        else:
            # Show help if no arguments provided
            click.echo(ctx.get_help())


@main.command('interactive', short_help="Enter interactive mode", help="Enter interactive mode for spelling words.")
def interactive_cmd() -> None:
    """Enter interactive mode for spelling words."""
    interactive_command()


@main.command('list', short_help="Show full alphabet", help="Display the complete NATO phonetic alphabet.")
def list_cmd() -> None:
    """Display the complete NATO phonetic alphabet."""
    print_alphabet_command()


# Internal functions
def interactive_command() -> None:
    """Internal function for interactive mode."""
    console.print(
        Panel.fit(
            "[bold blue]NATO Phonetic Alphabet - Interactive Mode[/bold blue]\n"
            "Enter words to spell them out. Type 'quit' or 'exit' to leave.",
            border_style="blue",
        )
    )

    while True:
        try:
            word = Prompt.ask("\n[cyan]Enter a word to spell[/cyan]")

            if word.lower() in ["quit", "exit", "q"]:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if not word.strip():
                continue

            spell_word_command(word)

        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break


def spell_word_command(word: str) -> None:
    """Internal function to spell a word."""
    result = spell_word(word)

    # Create a table for beautiful output with rounded corners
    table = Table(
        title=f"NATO Phonetic Spelling: {word.upper()}", 
        box=ROUNDED
    )
    table.add_column("Letter", style="cyan", justify="center")
    table.add_column("Phonetic", style="green", justify="left")

    for letter, phonetic in result:
        if letter.isspace():
            table.add_row(letter, "[dim]Space[/dim]")
        elif not letter.isalnum():
            table.add_row(letter, "[dim]Special Character[/dim]")
        else:
            table.add_row(letter, phonetic)

    console.print(table)


def print_alphabet_command() -> None:
    """Internal function to print the alphabet."""
    alphabet = get_full_alphabet()

    # Create a table for beautiful output with rounded corners
    table = Table(
        title="NATO Phonetic Alphabet", 
        box=ROUNDED
    )
    table.add_column("Letter", style="cyan", justify="center")
    table.add_column("Phonetic", style="green", justify="left")

    # Sort alphabetically
    for letter in sorted(alphabet.keys()):
        table.add_row(letter, alphabet[letter])

    console.print(table)


if __name__ == "__main__":
    main()
