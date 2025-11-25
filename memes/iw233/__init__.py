from datetime import datetime
import io
import random
import requests
from pathlib import Path
from pil_utils import BuildImage
from meme_generator import add_meme

# 本地缓存路径
cache_dir = Path(__file__).parent / "images" / "iw233_cache"
cache_dir.mkdir(parents=True, exist_ok=True)

def iw233(images, texts, args):
    url = "https://t.alcy.cc/xhl"  # 可换成 moez
    
    headers = {"User-Agent": "Mozilla/5.0"}
    frame = None

    # 先尝试网络获取
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        img_bytes = io.BytesIO(res.content)
        frame = BuildImage.open(img_bytes)
        print("网络图片获取成功！")
        
        # 同步保存到本地缓存
        local_file = cache_dir / f"{datetime.now().timestamp()}.jpg"
        frame.save_jpg(local_file)
    except Exception as e:
        print(f"网络图片获取失败: {e}")
        # 回退本地缓存
        cached_files = list(cache_dir.glob("*"))
        if cached_files:
            local_file = random.choice(cached_files)
            frame = BuildImage.open(local_file)
            print(f"使用本地缓存图片: {local_file.name}")
        else:
            raise RuntimeError("无法获取网络图片，且本地缓存为空！") from e

    return frame.save_jpg()

# 注册插件
add_meme(
    "iw233",
    iw233,
    min_texts=0,
    max_texts=0,
    keywords=["随机狐狸", "iw233"],
    date_created=datetime(2025, 11, 6),
    date_modified=datetime(2025, 11, 6),
)
