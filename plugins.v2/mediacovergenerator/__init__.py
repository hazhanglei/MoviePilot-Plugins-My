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


class MediaCoverGenerator(_PluginBase):
    """Emby媒体库封面生成插件"""
    
    # 插件名称
    plugin_name = "Emby媒体库封面生成"
    # 插件描述
    plugin_desc = "生成媒体库动态/静态封面，支持 Emby/Jellyfin"
    # 插件图标
    plugin_icon = "image.png"
    # 插件版本
    plugin_version = "1.0.0"
    # 插件作者
    plugin_author = "assistant"
    # 作者主页
    author_url = ""
    # 插件配置项ID前缀
    plugin_config_prefix = "mediacovergenerator_"
    # 加载顺序
    plugin_order = 2
    # 可使用的用户级别
    auth_level = 1
    
    # 退出事件
    _event = threading.Event()
    
    # 私有属性
    _enabled = False
    _servers = None
    _selected_servers = []
    _include_libraries = []
    _cover_style = "classic"
    _output_path = ""
    _width = 1280
    _height = 720
    
    # 预定义风格
    STYLES = {
        "classic": {
            "bg_color": (30, 30, 30),
            "text_color": (255, 255, 255),
            "accent_color": (255, 100, 100),
            "font_size": 48
        },
        "modern": {
            "bg_color": (15, 15, 20),
            "text_color": (200, 200, 220),
            "accent_color": (100, 150, 255),
            "font_size": 42
        },
        "minimal": {
            "bg_color": (255, 255, 255),
            "text_color": (30, 30, 30),
            "accent_color": (50, 50, 50),
            "font_size": 36
        }
    }
    
    def __init__(self):
        super().__init__()
        self.mediaserver_helper = MediaServerHelper()
        self.mschain = MediaServerChain()
    
    def init_plugin(self, config: dict = None):
        """初始化插件"""
        if config:
            self._enabled = config.get("enabled", False)
            self._selected_servers = config.get("selected_servers", [])
            self._include_libraries = config.get("include_libraries", [])
            self._cover_style = config.get("cover_style", "classic")
            self._output_path = config.get("output_path", "")
            self._width = int(config.get("width", 1280))
            self._height = int(config.get("height", 720))
        
        if self._selected_servers:
            self._servers = self.mediaserver_helper.get_services(
                name_filters=self._selected_servers
            )
        
        self.stop_service()
    
    def get_state(self) -> bool:
        """获取插件状态"""
        return self._enabled
    
    def get_service(self) -> List[Dict[str, Any]]:
        """注册服务"""
        return []
    
    def stop_service(self):
        """停止服务"""
        self._event.set()
    
    def get_command(self) -> List[Dict[str, Any]]:
        """注册命令"""
        return []
    
    def get_api(self) -> List[Dict[str, Any]]:
        """注册API"""
        return []
    
    def get_form(self) -> List[Dict[str, Any]]:
        """获取配置表单"""
        return [
            {
                "component": "VForm",
                "content": [
                    {
                        "component": "VSwitch",
                        "props": {
                            "model": "enabled",
                            "label": "启用插件",
                        }
                    },
                    {
                        "component": "VSelect",
                        "props": {
                            "model": "cover_style",
                            "label": "封面风格",
                            "items": [
                                {"title": "经典", "value": "classic"},
                                {"title": "现代", "value": "modern"},
                                {"title": "极简", "value": "minimal"}
                            ]
                        }
                    },
                    {
                        "component": "VTextField",
                        "props": {
                            "model": "width",
                            "label": "封面宽度",
                            "type": "number"
                        }
                    },
                    {
                        "component": "VTextField",
                        "props": {
                            "model": "height",
                            "label": "封面高度",
                            "type": "number"
                        }
                    },
                    {
                        "component": "VTextField",
                        "props": {
                            "model": "output_path",
                            "label": "输出路径"
                        }
                    }
                ]
            }
        ]
    
    def get_page(self) -> List[Dict[str, Any]]:
        """获取页面"""
        return []
    
    def __generate_cover_image(
        self,
        title: str,
        subtitle: str = "",
        items_count: int = 0,
        style: str = "classic",
        width: int = 1280,
        height: int = 720
    ) -> bytes:
        """生成封面图片"""
        config = self.STYLES.get(style, self.STYLES["classic"])
        
        # 创建图片
        image = Image.new("RGB", (width, height), config["bg_color"])
        draw = ImageDraw.Draw(image)
        
        # 加载字体
        try:
            font_path = self.__find_font()
            font = ImageFont.truetype(font_path, config["font_size"]) if font_path else ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()
        
        # 计算标题位置（居中）
        bbox = draw.textbbox((0, 0), title, font=font)
        title_w = bbox[2] - bbox[0]
        title_h = bbox[3] - bbox[1]
        title_x = (width - title_w) // 2
        title_y = (height - title_h) // 2 - 50
        
        # 绘制标题
        draw.text((title_x, title_y), title, font=font, fill=config["text_color"])
        
        # 绘制副标题
        if subtitle:
            try:
                sub_font = ImageFont.truetype(font_path, config["font_size"] // 2) if font_path else font
            except:
                sub_font = font
            bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
            sub_w = bbox[2] - bbox[0]
            sub_x = (width - sub_w) // 2
            sub_y = title_y + title_h + 20
            faded_color = tuple(int(c * 0.7) for c in config["text_color"])
            draw.text((sub_x, sub_y), subtitle, font=sub_font, fill=faded_color)
        
        # 绘制数量统计
        if items_count > 0:
            count_text = f"共 {items_count} 部"
            try:
                count_font = ImageFont.truetype(font_path, config["font_size"] // 3) if font_path else font
            except:
                count_font = font
            bbox = draw.textbbox((0, 0), count_text, font=count_font)
            count_w = bbox[2] - bbox[0]
            count_x = width - count_w - 30
            count_y = height - 40
            draw.text((count_x, count_y), count_text, font=count_font, fill=config["accent_color"])
        
        # 添加渐变效果
        gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        gradient_draw = ImageDraw.Draw(gradient)
        for i in range(height):
            alpha = int(255 * (1 - i / height) * 0.3)
            gradient_draw.line([(0, i), (width, i)], fill=(0, 0, 0, alpha))
        image = Image.alpha_composite(image.convert("RGBA"), gradient).convert("RGB")
        
        # 输出到字节流
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", quality=95)
        return buffer.getvalue()
    
    def __find_font(self) -> Optional[str]:
        """查找可用字体"""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "C:\\Windows\\Fonts\\msyh.ttc",
            "C:\\Windows\\Fonts\\simhei.ttf",
            "/System/Library/Fonts/PingFang.ttc"
        ]
        for path in font_paths:
            if os.path.exists(path):
                return path
        return None
    
    def __save_cover(self, cover_bytes: bytes, save_path: str):
        """保存封面"""
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(cover_bytes)
    
    def update_library_cover(self, library_name: str, library_id: str, server_name: str):
        """更新媒体库封面"""
        try:
            # 获取媒体库信息
            service = self._servers.get(server_name)
            if not service:
                logger.warning(f"媒体服务器 {server_name} 未找到")
                return
            
            # 获取媒体库中的媒体数量
            items = service.instance.get_items(library_id)
            items_count = len(items) if items else 0
            
            # 生成封面
            cover_bytes = self.__generate_cover_image(
                title=library_name,
                subtitle=server_name,
                items_count=items_count,
                style=self._cover_style,
                width=self._width,
                height=self._height
            )
            
            # 保存封面
            if self._output_path:
                save_path = os.path.join(self._output_path, f"{library_name}.png")
                self.__save_cover(cover_bytes, save_path)
                logger.info(f"封面已保存到: {save_path}")
            
            # 上传到媒体服务器
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


# 导出插件类
__all__ = ["MediaCoverGenerator"]