"""
静态样式1：单图居中风格
"""
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont


def create_style_static_1(
    images: List[Image.Image],
    title: str = "",
    subtitle: str = "",
    width: int = 1920,
    height: int = 1080,
    font_path: str = "",
    font_size: int = 120,
    zh_font_size: int = 170,
    en_font_size: int = 75,
    **kwargs
) -> Image.Image:
    """
    创建静态样式1：单图居中风格
    
    Args:
        images: 图像列表（取第一张）
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
    # 创建背景
    bg_color = (30, 30, 30)
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # 处理图像
    if images:
        img = images[0].copy()
        # 计算缩放
        img_ratio = img.width / img.height
        target_ratio = width / height
        
        if img_ratio > target_ratio:
            new_width = width
            new_height = int(width / img_ratio)
        else:
            new_height = height
            new_width = int(height * img_ratio)
        
        # 调整大小
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 计算位置（居中）
        x = (width - new_width) // 2
        y = (height - new_height) // 2
        
        # 添加模糊背景
        bg_blur = img.resize((int(width * 0.5), int(height * 0.5)), Image.Resampling.LANCZOS)
        bg_blur = bg_blur.filter(ImageFilter.GaussianBlur(radius=50))
        bg_blur = bg_blur.resize((width, height), Image.Resampling.LANCZOS)
        image.paste(bg_blur, (0, 0))
        
        # 添加前景图像（居中裁剪）
        image.paste(img, (x, y))
    
    # 添加渐变遮罩
    gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gradient_draw = ImageDraw.Draw(gradient)
    
    # 顶部渐变
    for i in range(int(height * 0.4)):
        alpha = int(255 * (1 - i / (height * 0.4)) * 0.7)
        gradient_draw.line([(0, i), (width, i)], fill=(0, 0, 0, alpha))
    
    # 底部渐变
    for i in range(int(height * 0.5), height):
        alpha = int(255 * ((i - height * 0.5) / (height * 0.5)) * 0.9)
        gradient_draw.line([(0, i), (width, i)], fill=(0, 0, 0, alpha))
    
    image = Image.alpha_composite(image.convert("RGBA"), gradient).convert("RGB")
    draw = ImageDraw.Draw(image)
    
    # 添加文字
    if title:
        try:
            font = ImageFont.truetype(font_path, zh_font_size) if font_path else ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # 计算文字位置
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (width - text_width) // 2
        text_y = height - text_height - 80
        
        # 绘制文字阴影
        shadow_offset = 3
        draw.text((text_x + shadow_offset, text_y + shadow_offset), title, font=font, fill=(0, 0, 0))
        draw.text((text_x, text_y), title, font=font, fill=(255, 255, 255))
    
    if subtitle:
        try:
            sub_font = ImageFont.truetype(font_path, en_font_size) if font_path else ImageFont.load_default()
        except:
            sub_font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
        sub_width = bbox[2] - bbox[0]
        sub_x = (width - sub_width) // 2
        sub_y = height - 40
        
        draw.text((sub_x, sub_y), subtitle, font=sub_font, fill=(200, 200, 200))
    
    return image


# 导入ImageFilter（在文件顶部可能漏掉了）
from PIL import ImageFilter