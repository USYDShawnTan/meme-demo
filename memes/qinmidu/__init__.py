from datetime import datetime
from typing import Literal
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from pil_utils import BuildImage
from pydantic import Field
from meme_generator import (
    MemeArgsModel,
    MemeArgsType,
    ParserArg,
    ParserOption,
    add_meme,
)
import random, re
import io
import numpy as np


class Model(MemeArgsModel):
    """占位"""
    pass

args_type = MemeArgsType(
    args_model=Model,
    parser_options=[
        ParserOption(
            names=["--上升"],
            args=[],
            help_text="甜蜜粉" 
        ),
        ParserOption(
            names=["--下降"],
            args=[],
            help_text="伤心蓝" 
        ),
        ParserOption(
            names=["无","默认"],
            args=[],
            help_text="随机" 
        ),
    ],
)

# 主函数
def qinmidu(images, texts: list[str], args: Model):
    # 上升或下降
    text = texts[0] if texts else "亲密度"
    text = str(text).strip()
    text = re.sub(r'^(上升){2,}', '上升', text)
    text = re.sub(r'^(下降){2,}', '下降', text)

    if text.startswith("上升"):
        text = text.replace("上升", "", 1).strip()
        arrow = "↑"
    elif text.startswith("下降"):
        text = text.replace("下降", "", 1).strip()
        arrow = "↓"
    else:
        arrow = random.choice(["↑", "↓"])

    text = (text + " " + arrow) if text else ("亲密度 " + arrow)
    is_up = (arrow == "↑")

    # 样式
    padding = 120
    font_size = 200        # 字体大小
    inner_fill = (255, 255, 255)
    inner_stroke_width = int(6 * 1.5 * 1.5)  # 加粗文字描边
    outline_thickness = 40
    bg_color = (255, 255, 255, 255)

    if is_up:
        inner_stroke_color = (220, 50, 120)  # 粉色加深
        outline_color = (255, 216, 240, 255)
    else:
        inner_stroke_color = (50, 80, 140)   # 蓝色加深
        outline_color = (156, 195, 252, 255)

    try:
        font = ImageFont.truetype("msyh.ttc", font_size)
    except Exception:
        font = ImageFont.truetype("arial.ttf", font_size)

    # 测量文本尺寸
    dummy = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(dummy)
    bbox = d.textbbox((0, 0), text, font=font, stroke_width=inner_stroke_width)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # 测量后扩展画布
    canvas_w = int(text_w + padding * 2)
    canvas_h = int(text_h + padding * 2)
    base = Image.new("RGBA", (canvas_w, canvas_h), bg_color)
    cx, cy = canvas_w // 2, canvas_h // 2

    # 文本遮罩
    text_mask = Image.new("L", (canvas_w, canvas_h), 0)
    mask_draw = ImageDraw.Draw(text_mask)
    mask_draw.text(
        (cx, cy),
        text,
        font=font,
        fill=255,
        anchor="mm",
        stroke_width=inner_stroke_width,
    )

    # 棉花边
    edge_mask = text_mask.filter(ImageFilter.MaxFilter(outline_thickness * 2 + 1))
    edge_mask = edge_mask.filter(ImageFilter.GaussianBlur(radius=max(4, outline_thickness // 2)))
    outline_layer = Image.new("RGBA", (canvas_w, canvas_h), outline_color)
    outline_layer.putalpha(edge_mask)

    # 主文字层
    text_layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    draw.text(
        (cx, cy),
        text,
        font=font,
        fill=inner_fill,
        anchor="mm",
        stroke_width=inner_stroke_width,
        stroke_fill=inner_stroke_color,
    )

    # 合成原始图
    result = base.copy()
    result = Image.alpha_composite(result, outline_layer)
    result = Image.alpha_composite(result, text_layer)

    # 有损处理
    downscale_factor = 0.15
    small_w = max(1, int(canvas_w * downscale_factor))
    small_h = max(1, int(canvas_h * downscale_factor))
    result_small = result.resize((small_w, small_h), resample=Image.BILINEAR)
    pixelated = result_small.resize((canvas_w, canvas_h), resample=Image.NEAREST)

    # JPEG 有损压缩
    buffer = io.BytesIO()
    pixelated.convert("RGB").save(buffer, format="JPEG", quality=50)
    buffer.seek(0)
    final_img = Image.open(buffer)


    """ 随机噪点
    #arr = np.array(final_img)
    #noise = np.random.randint(-10, 11, arr.shape, dtype=np.int16)
    #arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    #final_img = Image.fromarray(arr)"""

    # 柔和模糊
    final_img = final_img.filter(ImageFilter.GaussianBlur(radius=2.0))

    # 色彩减淡
    enhancer = ImageEnhance.Color(final_img)
    final_img = enhancer.enhance(0.97)

    return BuildImage(final_img).save_jpg()


# ================= 注册插件 =================
add_meme(
    "qinmidu",
    qinmidu,
    min_texts=0,
    max_texts=1,
    args_type=args_type,
    keywords=["亲密度"],
    date_created=datetime(2025, 11, 4),
    date_modified=datetime(2025, 11, 4),
)
