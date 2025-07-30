GETTERS_WITH_DTO = """from .handlers import {name}Handler

DialogManager = {name}Handler.DialogManager

async def get_data(dialog_manager: DialogManager, **kwargs) -> dict:
    return {{'dto_id': dialog_manager.dto.id}}"""

HANDLERS_WITH_DTO = '''from typing import Optional
from pydantic import BaseModel


class {name}DialogDTO(BaseModel):
    """DTO будет установленно в dialog_data по аттрибуту 'dto'
    и использоваться в пространстве данного диалога и хендлеров"""

    id: Optional[int] = None


class {name}Handler(TypedHandler):
    DialogManager = DialogManagerWithDTO[{name}DialogDTO]

    @staticmethod
    async def on_start(_, manager: DialogManager) -> None:
        await manager.set_dialog_dto({name}DialogDTO())
'''


DIALOG_WITH_DTO = """from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const

from . import getters
from .state import {name}SG
from .handlers import {name}Handler


dialog = Dialog(
    Window(
        Const("🏠 Главное меню"),
        getter=getters.get_data,
        state={name}SG.start,
    ),
    on_start={name}Handler.on_start
)
"""
