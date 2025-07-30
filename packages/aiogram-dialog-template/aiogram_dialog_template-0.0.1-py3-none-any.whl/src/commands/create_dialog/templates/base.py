GETTERS = """async def get_data(**kwargs) -> dict:
    pass
"""

HANDLERS = """from aiogram_dialog import DialogManager


async def on_start(_, manager: DialogManager) -> None:
    pass
"""

DIALOG = """from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const

from . import getters, handlers
from .state import {name}SG


dialog = Dialog(
    Window(
        Const("🏠 Главное меню"),
        getter=getters.get_data,
        state={name}SG.start,
    ),
    on_start=handlers.on_start
)
"""

STATE = """from aiogram.fsm.state import State, StatesGroup


class {name}SG(StatesGroup):
    start = State()
"""
