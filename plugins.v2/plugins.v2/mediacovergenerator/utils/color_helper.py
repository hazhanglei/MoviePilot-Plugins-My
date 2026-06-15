"""
通用颜色处理工具类
提供从图像中提取颜色、颜色转换、颜色验证等功能
"""
import re
import colorsys
import random
from collections import Counter
from typing import List, Tuple, Optional, Union
from PIL import Image
import numpy as np
from app.log import logger


class ColorHelper:
    """通用颜色处理工具类"""

    MACARON_FALLBACK_COLORS = [
        (237, 159, 77),
        (186, 225, 255),
        (255, 223, 186),
        (202, 231, 200),
        (255, 182, 193),
        (221, 160, 221),
        (176, 196, 222),
        (255, 218, 185),
    ]

    COLOR_NAMES = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128),
        'pink': (255, 192, 203),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'lime': (0, 255, 0),
        'navy': (0, 0, 128),
        'teal': (0, 128, 128),
        'silver': (192, 192, 192),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128),
        'maroon': (128, 0, 0),
        'olive': (128, 128, 0),
        'aqua': (0, 255, 255),
        'fuchsia': (255, 0, 255),
        'white': (255, 255, 255),
        'black': (0, 0, 0),
    }

    @staticmethod
    def rgb_to_hsv(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """RGB转HSV"""
        r, g, b = [x / 255.0 for x in rgb]
        return colorsys.rgb_to_hsv(r, g, b)

    @staticmethod
    def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
        """HSV转RGB"""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))

    @staticmethod
    def is_not_black_white_gray_near(color: Tuple[int, int, int], threshold: int = 30) -> bool:
        """检查颜色是否不是黑白灰"""
        r, g, b = color
        if max(r, g, b) < threshold:
            return False
        if min(r, g, b) > 255 - threshold:
            return False
        if abs(r - g) < threshold and abs(g - b) < threshold and abs(r - b) < threshold:
            return False
        return True

    @staticmethod
    def color_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """计算两个颜色在HSV空间中的距离"""
        h1, s1, v1 = ColorHelper.rgb_to_hsv(color1)
        h2, s2, v2 = ColorHelper.rgb_to_hsv(color2)
        h_dist = min(abs(h1 - h2), 1 - abs(h1 - h2))
        return h_dist * 5 + abs(s1 - s2) + abs(v1 - v2)

    @staticmethod
    def adjust_color_macaron(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """调整颜色为马卡龙风格"""
        h, s, v = ColorHelper.rgb_to_hsv(color)
        s = min(0.6, max(0.3, s))
        v = min(0.9, max(0.6, v))
        return ColorHelper.hsv_to_rgb(h, s, v)

    @staticmethod
    def darken_color(color: Tuple[int, int, int], factor: float = 0.7) -> Tuple[int, int, int]:
        """将颜色加深"""
        r, g, b = color
        return (int(r * factor), int(g * factor), int(b * factor))

    @staticmethod
    def lighten_color(color: Tuple[int, int, int], factor: float = 1.3) -> Tuple[int, int, int]:
        """将颜色变亮"""
        r, g, b = color
        return (min(255, int(r * factor)), min(255, int(g * factor)), min(255, int(b * factor)))

    @staticmethod
    def parse_color_string(color_str: str) -> Optional[Tuple[int, int, int]]:
        """解析颜色字符串"""
        if not color_str:
            return None

        color_str = color_str.strip().lower()

        if color_str.startswith('#'):
            hex_color = color_str[1:]
            try:
                if len(hex_color) == 3:
                    hex_color = ''.join([c * 2 for c in hex_color])
                elif len(hex_color) == 4:
                    hex_color = ''.join([c * 2 for c in hex_color])
                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    return (r, g, b)
                if len(hex_color) == 8:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    return (r, g, b)
            except ValueError:
                logger.warning(f"无效的十六进制颜色: {color_str}")
                return None

        rgb_match = re.match(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_str)
        if rgb_match:
            try:
                r, g, b = map(int, rgb_match.groups())
                if all(0 <= c <= 255 for c in (r, g, b)):
                    return (r, g, b)
            except ValueError:
                logger.warning(f"无效的RGB颜色: {color_str}")
                return None

        rgba_match = re.match(
            r'rgba\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([01]?(?:\.\d+)?)\s*\)',
            color_str,
        )
        if rgba_match:
            try:
                r = int(rgba_match.group(1))
                g = int(rgba_match.group(2))
                b = int(rgba_match.group(3))
                if all(0 <= c <= 255 for c in (r, g, b)):
                    return (r, g, b)
            except ValueError:
                logger.warning(f"无效的RGBA颜色: {color_str}")
                return None

        if color_str in ColorHelper.COLOR_NAMES:
            return ColorHelper.COLOR_NAMES[color_str]

        logger.warning(f"无法解析的颜色格式: {color_str}")
        return None

    @staticmethod
    def extract_dominant_colors(image: Image.Image, num_colors: int = 5,
                                style: str = "auto") -> List[Tuple[int, int, int]]:
        """从图像中提取主要颜色"""
        img = image.copy()
        img.thumbnail((150, 150))
        img = img.convert('RGB')
        pixels = list(img.getdata())

        filtered_pixels = [p for p in pixels if ColorHelper.is_not_black_white_gray_near(p)]
        if not filtered_pixels:
            logger.warning("图像中没有找到有效的颜色，使用默认颜色")
            return ColorHelper.MACARON_FALLBACK_COLORS[:num_colors]

        color_counter = Counter(filtered_pixels)
        candidate_colors = color_counter.most_common(num_colors * 5)

        extracted_colors = []
        min_color_distance = 0.15

        for color, _ in candidate_colors:
            if style == "macaron":
                adjusted_color = ColorHelper.adjust_color_macaron(color)
            elif style == "vibrant":
                h, s, v = ColorHelper.rgb_to_hsv(color)
                s = min(1.0, s * 1.3)
                adjusted_color = ColorHelper.hsv_to_rgb(h, s, v)
            elif style == "muted":
                h, s, v = ColorHelper.rgb_to_hsv(color)
                s = s * 0.7
                adjusted_color = ColorHelper.hsv_to_rgb(h, s, v)
            else:
                adjusted_color = color

            if not any(ColorHelper.color_distance(adjusted_color, existing) < min_color_distance
                       for existing in extracted_colors):
                extracted_colors.append(adjusted_color)
                if len(extracted_colors) >= num_colors:
                    break

        while len(extracted_colors) < num_colors:
            fallback_color = random.choice(ColorHelper.MACARON_FALLBACK_COLORS)
            if not any(ColorHelper.color_distance(fallback_color, existing) < min_color_distance
                       for existing in extracted_colors):
                extracted_colors.append(fallback_color)
            else:
                extracted_colors.append(fallback_color)
                break

        return extracted_colors[:num_colors]

    @staticmethod
    def get_background_color(image: Image.Image, color_mode: str = "auto",
                             custom_color: Optional[str] = None,
                             config_color: Optional[str] = None) -> Tuple[int, int, int]:
        """根据模式获取背景颜色"""
        if color_mode == "custom" and custom_color:
            parsed_color = ColorHelper.parse_color_string(custom_color)
            if parsed_color:
                return parsed_color
            logger.warning(f"无法解析自定义颜色 {custom_color}，回退到自动模式")

        if color_mode == "config" and config_color:
            parsed_color = ColorHelper.parse_color_string(config_color)
            if parsed_color:
                return parsed_color
            logger.warning(f"无法解析配置颜色 {config_color}，回退到自动模式")

        colors = ColorHelper.extract_dominant_colors(image, num_colors=1, style="macaron")
        return ColorHelper.darken_color(colors[0], 0.85) if colors else (100, 100, 100)