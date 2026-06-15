"""
静态样式3：极简风格
"""
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def create_style_static_3(
    images: List[Image.Image],
    title: str = "",
    subtitle: str = "",
    width: int = 1920,
    height: int = 1080,
    font_path: str = "",
    font_size: int = 120,
    zh_font_size: int = 200,
    en_font_size: int = 80,
    **kwargs
) -> Image.Image:
    """
    创建静态样式3：极简风格
    
    Args:
        images: 图像列表（取第一张作为背景）
        title: 标题文本
        subtitle: 副标题文本
        width: 输出宽度
        height: 输出高度
        font_path: 字体路径
        font_size: 字体大小
        zh_font_size: 中文字体大小
        en_font_size: 英文字体大小
        **kwargs: 其他参数
    
    Returns:
        生成的封面图像
    """
    image = Image.new("RGB", (width, height), (255, 255, 255))
    
    if images:
        img = images[0].copy()
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        img = img.filter(ImageFilter.GaussianBlur(radius=10))
        image = img
    
    draw = ImageDraw.Draw(image)
    
    if title:
        try:
            font = ImageFont.truetype(font_path, zh_font_size) if font_path else ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        
        avg_brightness = sum(image.getpixel((width // 2, height // 2))) / 3
        text_color = (30, 30, 30) if avg_brightness > 128 else (255, 255, 255)
        
        draw.text((text_x, text_y), title, font=font, fill=text_color)
    
    if subtitle:
        try:
            sub_font = ImageFont.truetype(font_path, en_font_size) if font_path else ImageFont.load_default()
        except:
            sub_font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
        sub_width = bbox[2] - bbox[0]
        sub_x = (width - sub_width) // 2
        sub_y = (height // 2) + text_height // 2 + 30
        
        draw.text((sub_x, sub_y), subtitle, font=sub_font, fill=(100, 100, 100))
    
    return image