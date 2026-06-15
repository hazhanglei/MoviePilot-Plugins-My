import os
import io
import base64
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

from app.log import logger
from app.plugins import _PluginBase
from app.helper.mediaserver import MediaServerHelper
from app.chain.mediaserver import MediaServerChain
from app.core.config import settings

from .utils import ColorHelper, NetworkHelper, ResolutionConfig
from .style import STYLE_MAP, STYLE_NAMES


class MediaCoverGenerator(_PluginBase):
    """Emby媒体库封面生成插件"""

    plugin_name = "Emby媒体库封面V2"
    plugin_desc = "生成媒体库动态/静态封面，支持 Emby/Jellyfin"
    plugin_icon = "image.png"
    plugin_version = "1.0.0"
    plugin_author = "hazhanglei"
    author_url = ""
    plugin_config_prefix = "mediacovergenerator_"
    plugin_order = 2
    auth_level = 1

    _event = threading.Event()

    _enabled = False
    _servers = None
    _selected_servers = []
    _include_libraries = []
    _cover_style = "static_1"
    _output_path = ""
    _width = 1920
    _height = 1080
    _font_path = ""
    _auto_update = False
    _update_interval = 24

    def __init__(self):
        super().__init__()
        self.mediaserver_helper = MediaServerHelper()
        self.mschain = MediaServerChain()
        self._resolution = ResolutionConfig("1080p")

    def init_plugin(self, config: dict = None):
        if config:
            self._enabled = config.get("enabled", False)
            self._selected_servers = config.get("selected_servers", [])
            self._include_libraries = config.get("include_libraries", [])
            self._cover_style = config.get("cover_style", "static_1")
            self._output_path = config.get("output_path", "")
            self._width = int(config.get("width", 1920))
            self._height = int(config.get("height", 1080))
            self._font_path = config.get("font_path", "")
            self._auto_update = config.get("auto_update", False)
            self._update_interval = int(config.get("update_interval", 24))

        if self._selected_servers:
            self._servers = self.mediaserver_helper.get_services(
                name_filters=self._selected_servers
            )

        self._resolution = ResolutionConfig((self._width, self._height))
        self.stop_service()

    def get_state(self) -> bool:
        return self._enabled

    def get_service(self) -> List[Dict[str, Any]]:
        return []

    def stop_service(self):
        self._event.set()

    def get_command(self) -> List[Dict[str, Any]]:
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        return []

    def get_form(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "switch",
                "key": "enabled",
                "label": "启用插件",
                "value": False
            },
            {
                "type": "select",
                "key": "cover_style",
                "label": "封面样式",
                "options": [
                    {"label": "单图居中", "value": "static_1"},
                    {"label": "多图拼接", "value": "static_2"},
                    {"label": "极简风格", "value": "static_3"},
                    {"label": "电影胶片", "value": "static_4"}
                ],
                "value": "static_1"
            },
            {
                "type": "select",
                "key": "resolution",
                "label": "输出分辨率",
                "options": [
                    {"label": "1080p (1920×1080)", "value": "1080p"},
                    {"label": "720p (1280×720)", "value": "720p"},
                    {"label": "4K (3840×2160)", "value": "4k"},
                    {"label": "自定义", "value": "custom"}
                ],
                "value": "1080p"
            },
            {
                "type": "number",
                "key": "width",
                "label": "自定义宽度",
                "placeholder": "1920",
                "value": 1920
            },
            {
                "type": "number",
                "key": "height",
                "label": "自定义高度",
                "placeholder": "1080",
                "value": 1080
            },
            {
                "type": "text",
                "key": "font_path",
                "label": "自定义字体路径",
                "placeholder": "字体文件路径",
                "value": ""
            },
            {
                "type": "text",
                "key": "output_path",
                "label": "本地输出路径",
                "placeholder": "封面保存目录（可选）",
                "value": ""
            },
            {
                "type": "switch",
                "key": "auto_update",
                "label": "自动更新封面",
                "value": False
            },
            {
                "type": "number",
                "key": "update_interval",
                "label": "更新间隔（小时）",
                "placeholder": "24",
                "value": 24
            }
        ]

    def get_page(self) -> List[Dict[str, Any]]:
        return []

    def _find_font(self) -> Optional[str]:
        """查找可用字体"""
        font_paths = [
            self._font_path,
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "C:\\Windows\\Fonts\\msyh.ttc",
            "C:\\Windows\\Fonts\\simhei.ttf",
            "/System/Library/Fonts/PingFang.ttc"
        ]
        for path in font_paths:
            if path and os.path.exists(path):
                return path
        return None

    def _generate_cover(
        self,
        images: List[Image.Image],
        title: str = "",
        subtitle: str = "",
        style: str = "static_1"
    ) -> bytes:
        """生成封面图片"""
        style_func = STYLE_MAP.get(style, STYLE_MAP["static_1"])
        
        font_path = self._find_font()
        zh_font_size = self._resolution.get_font_size(150)
        en_font_size = self._resolution.get_font_size(65)
        
        result = style_func(
            images=images,
            title=title,
            subtitle=subtitle,
            width=self._width,
            height=self._height,
            font_path=font_path,
            zh_font_size=zh_font_size,
            en_font_size=en_font_size
        )
        
        buffer = io.BytesIO()
        result.save(buffer, format="PNG", quality=95)
        return buffer.getvalue()

    def _save_cover(self, cover_bytes: bytes, save_path: str):
        """保存封面到本地"""
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(cover_bytes)

    def update_library_cover(self, library_name: str, library_id: str, server_name: str):
        """更新单个媒体库封面"""
        try:
            service = self._servers.get(server_name)
            if not service:
                logger.warning(f"媒体服务器 {server_name} 未找到")
                return

            items = service.instance.get_items(library_id)
            items_count = len(items) if items else 0

            cover_bytes = self._generate_cover(
                images=[],
                title=library_name,
                subtitle=f"共 {items_count} 部",
                style=self._cover_style
            )

            if self._output_path:
                save_path = os.path.join(self._output_path, f"{library_name}.png")
                self._save_cover(cover_bytes, save_path)
                logger.info(f"封面已保存到: {save_path}")

            cover_base64 = base64.b64encode(cover_bytes).decode()
            service.instance.upload_image(library_id, cover_base64)
            logger.info(f"媒体库 {library_name} 封面已更新")

        except Exception as e:
            logger.error(f"更新媒体库封面失败: {e}")

    def update_all_libraries(self):
        """更新所有媒体库封面"""
        if not self._servers:
            logger.warning("未配置媒体服务器")
            return

        for server_name, service in self._servers.items():
            if service.instance.is_inactive():
                logger.warning(f"媒体服务器 {server_name} 未连接")
                continue

            libraries = service.instance.get_libraries()
            for library in libraries:
                library_name = library.get("Name", "")
                library_id = library.get("Id", "")

                if self._include_libraries and library_name not in self._include_libraries:
                    continue

                self.update_library_cover(library_name, library_id, server_name)


__all__ = ["MediaCoverGenerator"]
