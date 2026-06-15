from .style_static_1 import create_style_static_1
from .style_static_2 import create_style_static_2
from .style_static_3 import create_style_static_3
from .style_static_4 import create_style_static_4

__all__ = [
    'create_style_static_1',
    'create_style_static_2',
    'create_style_static_3',
    'create_style_static_4'
]

STYLE_MAP = {
    "static_1": create_style_static_1,
    "static_2": create_style_static_2,
    "static_3": create_style_static_3,
    "static_4": create_style_static_4
}

STYLE_NAMES = {
    "static_1": "单图居中",
    "static_2": "多图拼接",
    "static_3": "极简风格",
    "static_4": "电影胶片"
}