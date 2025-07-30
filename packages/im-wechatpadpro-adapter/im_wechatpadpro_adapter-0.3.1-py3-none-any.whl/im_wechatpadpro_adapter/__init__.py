import asyncio
import os

from im_wechatpadpro_adapter.adapter import WeChatAdapter, WeChatConfig

from kirara_ai.logger import get_logger
from kirara_ai.plugin_manager.plugin import Plugin
from kirara_ai.web.app import WebServer
from kirara_ai.workflow.core.workflow.builder import WorkflowBuilder

logger = get_logger("WeChat-Adapter")


class WeChatAdapterPlugin(Plugin):
    web_server: WebServer
    
    def __init__(self):
        pass

    def on_load(self):
        self.im_registry.register(
            "wechat", 
            WeChatAdapter, 
            WeChatConfig, 
            "微信机器人", 
            "微信机器人，通过 WeChatPadPro 与微信交互，支持基本的聊天功能。",
            """
微信机器人，通过 WeChatPadPro 与微信交互，支持基本的聊天功能，WeChatPadPro的部署和注意事项可参考 [WeChatPadPro 文档](https://github.com/WeChatPadPro/WeChatPadPro),以下配置默认为docker部署WeChatPadPro的配置,初次登录将会在控制台打印登录二维码网址，请打开网址后扫码登录。
            """
        )
        local_logo_path = os.path.join(os.path.dirname(__file__), "assets", "wechat.png")
        self.web_server.add_static_assets("/assets/icons/im/wechat.png", local_logo_path)

    def on_start(self):
        try:
            # Get current file's absolute path
            with importlib.resources.path('im_wechat_adapter', '__init__.py') as p:
                package_path = p.parent
                example_dir = package_path / 'example'

                if not example_dir.exists():
                    raise FileNotFoundError(f"Example directory not found at {example_dir}")

                yaml_files = list(example_dir.glob('*.yaml')) + list(example_dir.glob('*.yml'))

                for yaml in yaml_files:
                    logger.info(yaml)
                    self.workflow_registry.register_preset_workflow("chat", yaml.stem, WorkflowBuilder.load_from_yaml(os.path.join(example_dir, yaml), self.container))
        except Exception as e:
            logger.warning(f"workflow_registry failed: {e}")
            try:
                current_file = os.path.abspath(__file__)
                parent_dir = os.path.dirname(current_file)
                example_dir = os.path.join(parent_dir, 'example')
                yaml_files = [f for f in os.listdir(example_dir) if f.endswith('.yaml') or f.endswith('.yml')]

                for yaml in yaml_files:
                    logger.info(os.path.join(example_dir, yaml))
                    self.workflow_registry.register_preset_workflow("chat", yaml.stem, WorkflowBuilder.load_from_yaml(os.path.join(example_dir, yaml), self.container))
            except Exception as e:
                logger.warning(f"workflow_registry failed: {e}")

    def on_stop(self):
        try:
            tasks = []
            loop = asyncio.get_event_loop()
            for key, adapter in self.im_manager.get_adapters().items():
                if isinstance(adapter, WeChatAdapter) and adapter.is_running:
                    tasks.append(self.im_manager.stop_adapter(key, loop))
            for key in list(self.im_manager.get_adapters().keys()):
                self.im_manager.delete_adapter(key)
            loop.run_until_complete(asyncio.gather(*tasks))
        except Exception as e:
            logger.error(f"Error stopping WeChat adapter: {e}")
        finally:
            self.im_registry.unregister("wechat")
        logger.info("WeChat adapter stopped") 