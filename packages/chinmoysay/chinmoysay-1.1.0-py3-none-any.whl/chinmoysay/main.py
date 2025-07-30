"""
chinmoysay - A simple CLI greeting application
"""

import typer

app = typer.Typer(help="A friendly CLI app for greetings!")


@app.command()
def greet(name: str = typer.Argument(..., help="Name of the person to greet")):
    """Greet someone with a friendly hello."""
    typer.echo(f"Hi {name}")


@app.command()
def goodbye(name: str = typer.Argument(..., help="Name of the person to say goodbye to")):
    """Say goodbye to someone."""
    typer.echo(f"Bye {name}")


@app.command()
def goodnight(name: str = typer.Argument(..., help="Name of the person say good night")):
    """Say goodnight to someone"""
    typer.echo(f"Good Night {name}")


@app.command()
def version():
    """Show the version of chinmoysay."""
    typer.echo("chinmoysay version 1.1.0")


def main():
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
