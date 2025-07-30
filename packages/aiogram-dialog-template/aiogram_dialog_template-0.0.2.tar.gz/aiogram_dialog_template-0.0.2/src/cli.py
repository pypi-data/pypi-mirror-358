# cli.py
import click
from .commands.create_dialog.script import create_structure

@click.group()
def cli():
    """Main CLI for aiogram-dialog-template"""
    pass

@cli.command()
@click.option("--name", required=True, help="Dialog name (no hyphens allowed)")
@click.option("--path", required=True, help="Target directory")
@click.option("--use-dto", is_flag=True, help="Use DTO-based structure")
def create(name, path, use_dto):
    """Create a new aiogram-dialog structure"""
    if "-" in name:
        raise ValueError('Do not use "-" in name')
    create_structure(name, path, use_dto)

if __name__ == "__main__":
    cli()
