import importlib
from fastapi import APIRouter

from chariot_scaffold import log
from chariot_scaffold.core.config import PluginSpecYaml
from chariot_scaffold.schema.base import ActionOutputModel, ActionOutputBodyModel, StdinModel


editor_router = APIRouter()
plugin_spec = PluginSpecYaml()
plugin_spec.deserializer()


@editor_router.post("/editor/plugin", response_model=ActionOutputModel, name="在线编辑代码")
async def receive_plugin(plugin_construction: dict):
    """
    接收在线编辑的代码并热更新
    """
    # module = importlib.import_module(plugin_spec.entrypoint)
    # pack = module.__getattribute__(plugin_spec.module)()

    editor = plugin_construction["editor"]
    codes = editor["plugin_code"]
    actions = codes["actions"]



    """
    数据格式: 
    {
        "type": "action",
        "editor": {...},
        "parameters": {...},
        "plugin_edit_type": "code"
    }
    """




    ...


