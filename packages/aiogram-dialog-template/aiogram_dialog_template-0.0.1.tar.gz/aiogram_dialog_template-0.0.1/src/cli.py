# cli.py
import click
from src.commands import create_structure

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
    import sys
    from pathlib import Path
    
    def get_project_base_path() -> Path:
        # Исключаем пути из venv и системные пути Python
        print(sys.path)
        for path in sys.path:
            if "site-packages" not in path and "dist-packages" not in path:
                candidate = Path(path).resolve()
                if (candidate / "pyproject.toml").exists() or (candidate / "setup.py").exists():
                    return candidate
        # Если не нашли, возвращаем текущую рабочую директорию
        return Path.cwd()
    
    
    BASE_PATH = get_project_base_path()
    print(f"Project BASE_PATH: {BASE_PATH}")