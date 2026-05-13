"""
rembg 背景移除服务
支持多种模型选择，轻量模型适合低内存服务器
"""
from rembg import remove
from PIL import Image
import io

# 可用模型列表
# u2net - 标准版，效果好但内存占用较高
# u2netp - 轻量版，推荐用于低配置服务器
# silueta - 超轻量版(43MB)，内存占用最小
MODEL_OPTIONS = ["u2net", "u2netp", "silueta"]
DEFAULT_MODEL = "u2netp"  # 默认使用轻量模型


def remove_background(image_bytes: bytes, model_name: str = DEFAULT_MODEL) -> bytes:
    """
    使用 rembg 移除图片背景

    Args:
        image_bytes: 原始图片的字节数据
        model_name: 使用的模型名称，可选: u2net, u2netp, silueta

    Returns:
        去除背景后的 PNG 图片字节数据
    """
    input_img = Image.open(io.BytesIO(image_bytes))

    # 根据模型名称选择模型
    model = model_name if model_name in MODEL_OPTIONS else DEFAULT_MODEL

    output = remove(input_img, model_name=model)

    buf = io.BytesIO()
    output.save(buf, format="PNG")
    return buf.getvalue()


def remove_background_light(image_bytes: bytes) -> bytes:
    """
    使用轻量模型移除背景（推荐用于低内存服务器）
    等同于 remove_background(image_bytes, model_name='u2netp')
    """
    return remove_background(image_bytes, model_name="u2netp")


def remove_background_ultra_light(image_bytes: bytes) -> bytes:
    """
    使用超轻量模型移除背景（内存占用最小）
    等同于 remove_background(image_bytes, model_name='silueta')
    """
    return remove_background(image_bytes, model_name="silueta")
