from datetime import datetime
from pathlib import Path
from random import choice
from pil_utils import BuildImage
from meme_generator import add_meme


plugin_dir = Path(__file__).parent
img_dir = plugin_dir / "images"

def gganma(images, texts, args):
    if not img_dir.exists() or not any(img_dir.iterdir()):
        return BuildImage.new("RGBA", (600, 400), (255, 255, 255)).draw_text(
            (300, 200), "images文件夹内没有图片！", max_fontsize=40, anchor="mm"
        ).save_jpg()

    # 获取所有图片文件（支持jpg/png/gif/webp）
    all_imgs = [p for p in img_dir.iterdir() if p.suffix.lower() in [".jpg", ".png", ".jpeg", ".gif", ".webp"]]
    if not all_imgs:
        return BuildImage.new("RGBA", (600, 400), (255, 255, 255)).draw_text(
            (300, 200), "未检测到图片文件！", max_fontsize=40, anchor="mm"
        ).save_jpg()

    # 随机一张返回
    chosen_path = choice(all_imgs)
    img = BuildImage.open(chosen_path)
    return img.save_jpg()


add_meme(
    "gganma",
    gganma,
    keywords=["干嘛"],
    date_created=datetime(2025, 11, 4),
    date_modified=datetime(2025, 11, 4),
)
