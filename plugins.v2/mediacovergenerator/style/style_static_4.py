"""
静态样式4：电影胶片风格
"""
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def create_style_static_4(
    images: List[Image.Image],
    title: str = "",
    subtitle: str = "",
    width: int = 1920,
    height: int = 1080,
    font_path: str = "",
    font_size: int = 120,
    zh_font_size: int = 140,
    en_font_size: int = 60,
    **kwargs
) -> Image.Image:
    """
    创建静态样式4：电影胶片风格
    
    Args:
        images: 图像列表
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
    bg_color = (15, 15, 15)
    image = Image.new("RGB", (width, height), bg_color)
    
    if images:
        main_img = images[0].copy()
        img_ratio = main_img.width / main_img.height
        target_ratio = width / height
        
        if img_ratio > target_ratio:
            new_w = width
            new_h = int(width / img_ratio)
        else:
            new_h = height * 0.8
            new_w = int(new_h * img_ratio)
        
        main_img = main_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        x = (width - new_w) // 2
        y = (height - new_h) // 2
        
        image.paste(main_img, (x, y))
        
        border_img = Image.new("RGB", (new_w + 10, new_h + 10), (40, 40, 40))
        border_img.paste(main_img, (5, 5))
        image.paste(border_img, (x - 5, y - 5))
    
    draw = ImageDraw.Draw(image)
    
    # 添加装饰线
    line_y = height - 150
    draw.line([(50, line_y), (width - 50, line_y)], fill=(60, 60, 60), width=2)
    
    if title:
        try:
            font = ImageFont.truetype(font_path, zh_font_size) if font_path else ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (width - text_width) // 2
        text_y = height - text_height - 40
        
        draw.text((text_x, text_y), title, font=font, fill=(255, 255, 255))
    
    if subtitle:
        try:
            sub_font = ImageFont.truetype(font_path, en_font_size) if font_path else ImageFont.load_default()
        except:
            sub_font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
        sub_width = bbox[2] - bbox[0]
        sub_x = (width - sub_width) // 2
        sub_y = height - 30
        
        draw.text((sub_x, sub_y), subtitle, font=sub_font, fill=(150, 150, 150))
    
    return image