"""
Используйте команду:
python -m bot.core.commands.create_dialog --name {name} --folder {folder} --use_dto {(true/false или 1/0)}
"""

from pathlib import Path

from loguru import logger


from .templates.base import *
from .templates.with_dto import *

MODULES = ['dialog', 'getters', 'handlers', 'state']

MODULE_TEMPLATE_MAP = {
    'dialog': DIALOG,
    'getters': GETTERS,
    'handlers': HANDLERS,
    'state': STATE,
}

MODULE_TEMPLATE_WITH_DTO_MAP = {
    'dialog': DIALOG_WITH_DTO,
    'getters': GETTERS_WITH_DTO,
    'handlers': HANDLERS_WITH_DTO,
    'state': STATE,
}


def format_name(name: str) -> str:
    words = name.split('_')
    words = [word.title() for word in words]
    return ''.join(words)


def test_format_name():
    names = ['hello', 'World', 'hello_word', 'bey__', '213', '_ok', 'SuperName', 'to-do']
    for name_ in names:
        print(format_name(name_))


def create_files(base_dir: Path, file_names: list[str]):
    for file_name in file_names:
        (base_dir / f'{file_name}.py').touch()


def fill_file_template(
    base_dir: Path, file_names: list[str], name: str, mapper: dict[str, str]
):
    for file_name in file_names:
        with open((base_dir / f'{file_name}.py'), 'a', encoding='utf-8') as file:
            file.write(mapper[file_name].format(name=format_name(name)))


def create_structure(name: str, path: str, use_dto: bool):
    # Создаем базовую директорию с именем %name%
    pars_folder = path.split('/')
    
    base_dir = Path(*pars_folder, name)
    
    if base_dir.exists():
        logger.warning(f"Структура для '{path}/{name}' уже существует.")
        return
    
    base_dir.mkdir(parents=True, exist_ok=True)
    base_dir.mkdir(exist_ok=True)
    
    # Создаем поддиректории и файлы
    create_files(base_dir, file_names=MODULES)

    mapper = MODULE_TEMPLATE_WITH_DTO_MAP if use_dto else MODULE_TEMPLATE_MAP
    fill_file_template(
        base_dir,
        file_names=MODULES,
        name=name,
        mapper=mapper,
    )

    logger.success(f"Структура для '{name}' успешно создана.")


