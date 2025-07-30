"""
Используйте команду:
python -m bot.core.commands.create_dialog --name {name} --folder {folder} --use_dto {(true/false или 1/0)}
"""


import argparse

from .script import create_structure

parser = argparse.ArgumentParser(description="Создание структуры директорий и файлов.")
parser.add_argument("--name", type=str, required=True, help="Имя диалога.")
parser.add_argument(
    "--folder",
    type=str,
    help=(
        "Папка, в которую надо поместить сущность. Например: bot/dialogs/common. По"
        " умолчанию: bot/dialogs"
    ),
    default="bot/dialogs",
)
parser.add_argument(
    "--use_dto",
    type=str,
    choices=["true", "false", "1", "0"],
    help=(
        "Построить ли структуру, основанную на использовании DTO в хендлерах (true/false"
        " или 1/0). По умолчанию false"
    ),
    default="false",
)

args = parser.parse_args()
args.use_dto = args.use_dto.lower() in ("true", "1")  # type: ignore

# Вызов функции с переданным именем
if '-' in args.name:
    raise ValueError('Do not use "-" in name')

create_structure(args.name, args.folder, args.use_dto)
