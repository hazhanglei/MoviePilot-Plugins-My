"""
静态样式2：多图拼接风格
"""
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def create_style_static_2(
    images: List[Image.Image],
    title: str = "",
    subtitle: str = "",
    width: int = 1920,
    height: int = 1080,
    font_path: str = "",
    font_size: int = 120,
    zh_font_size: int = 150,
    en_font_size: int = 65,
    **kwargs
) -> Image.Image:
    """
    创建静态样式2：多图拼接风格
    
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
    bg_color = (20, 20, 20)
    image = Image.new("RGB", (width, height), bg_color)
    
    # 使用最多4张图片
    use_images = images[:4]
    
    if use_images:
        # 计算布局
        cols = 2 if len(use_images) >= 2 else 1
        rows = (len(use_images) + cols - 1) // cols
        
        cell_width = width // cols
        cell_height = height // rows
        
        for i, img in enumerate(use_images):
            row = i // cols
            col = i % cols
            
            img_ratio = img.width / img.height
            target_ratio = cell_width / cell_height
            
            if img_ratio > target_ratio:
                new_w = cell_width
                new_h = int(cell_width / img_ratio)
            else:
                new_h = cell_height
                new_w = int(cell_height * img_ratio)
            
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            x = col * cell_width + (cell_width - new_w) // 2
            y = row * cell_height + (cell_height - new_h) // 2
            
            image.paste(img, (x, y))
    
    # 添加渐变遮罩
    gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gradient_draw = ImageDraw.Draw(gradient)
    
    for i in range(height):
        alpha = int(255 * (1 - i / height) * 0.6)
        gradient_draw.line([(0, i), (width, i)], fill=(0, 0, 0, alpha))
    
    image = Image.alpha_composite(image.convert("RGBA"), gradient).convert("RGB")
    draw = ImageDraw.Draw(image)
    
    # 添加文字
    if title:
        try:
            font = ImageFont.truetype(font_path, zh_font_size) if font_path else ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2 - 40
        
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
        sub_y = (height // 2) + 40
        
        draw.text((sub_x, sub_y), subtitle, font=sub_font, fill=(200, 200, 200))
    
    return image