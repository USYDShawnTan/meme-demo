from datetime import datetime
from pathlib import Path
from random import choice
from pil_utils import BuildImage
from meme_generator import add_meme

# === 基础路径 ===
plugin_dir = Path(__file__).parent
img_dir = plugin_dir / "images"

def gganma(images, texts, args):
    """
    随机从 images 文件夹中取出一张图像返回
    """
    if not img_dir.exists() or not any(img_dir.iterdir()):
        # 如果没找到图片文件
        return BuildImage.new("RGBA", (600, 400), (255, 255, 255)).draw_text(
            (300, 200), "images文件夹内没有图片！", max_fontsize=40, anchor="mm"
        ).save_jpg()

    # 获取所有图片文件（支持jpg/png/gif/webp）
    all_imgs = [p for p in img_dir.iterdir() if p.suffix.lower() in [".jpg", ".png", ".jpeg", ".gif", ".webp"]]

    # 如果没有合法图片，返回提示
    if not all_imgs:
        return BuildImage.new("RGBA", (600, 400), (255, 255, 255)).draw_text(
            (300, 200), "未检测到图片文件！", max_fontsize=40, anchor="mm"
        ).save_jpg()

    # 随机选择一张
    chosen_path = choice(all_imgs)

    # 打开图片并返回
    img = BuildImage.open(chosen_path)
    return img.save_jpg()


# === 注册插件 ===
add_meme(
    "gganma",
    gganma,
    keywords=["干嘛"],
    date_created=datetime(2025, 11, 4),
    date_modified=datetime(2025, 11, 4),
)
