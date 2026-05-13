"""
图片处理服务：压缩、尺寸调整
"""
from PIL import Image
import io
from typing import Tuple

# 默认压缩配置
DEFAULT_MAX_SIZE: Tuple[int, int] = (1024, 1024)  # 最大边长
DEFAULT_QUALITY: int = 85  # JPEG 质量 (1-100)
DEFAULT_FORMAT: str = "PNG"  # 默认输出格式


def compress_image(
    image_bytes: bytes,
    max_size: Tuple[int, int] = DEFAULT_MAX_SIZE,
    quality: int = DEFAULT_QUALITY,
    output_format: str = DEFAULT_FORMAT,
) -> bytes:
    """
    压缩图片：调整尺寸 + 质量压缩

    Args:
        image_bytes: 原始图片字节
        max_size: 最大尺寸 (width, height)，超过会自动缩放
        quality: 输出质量 (1-100)，仅对 JPEG 有效
        output_format: 输出格式 (PNG/JPEG/WEBP)

    Returns:
        压缩后的图片字节
    """
    input_img = Image.open(io.BytesIO(image_bytes))

    # 转换为 RGBA 以支持透明通道
    if input_img.mode not in ("RGB", "RGBA"):
        input_img = input_img.convert("RGBA")

    # 调整尺寸（保持比例）
    input_img = resize_image(input_img, max_size)

    # 压缩输出
    output = io.BytesIO()
    if output_format.upper() == "JPEG":
        # JPEG 不支持透明，转换为 RGB
        if input_img.mode == "RGBA":
            input_img = input_img.convert("RGB")
        input_img.save(output, format=output_format, quality=quality, optimize=True)
    elif output_format.upper() == "WEBP":
        input_img.save(output, format=output_format, quality=quality, method=6)
    else:
        # PNG 格式，quality 参数无效但可以优化
        input_img.save(output, format=output_format, optimize=True)

    return output.getvalue()


def resize_image(img: Image.Image, max_size: Tuple[int, int]) -> Image.Image:
    """
    调整图片尺寸，保持宽高比

    Args:
        img: PIL 图片对象
        max_size: 最大尺寸 (width, height)

    Returns:
        调整后的图片对象
    """
    width, height = img.size
    max_width, max_height = max_size

    # 如果图片尺寸在限制内，直接返回
    if width <= max_width and height <= max_height:
        return img

    # 计算缩放比例
    ratio = min(max_width / width, max_height / height)
    new_size = (int(width * ratio), int(height * ratio))

    # 使用 LANCZOS 进行高质量缩放
    return img.resize(new_size, Image.Resampling.LANCZOS)


def get_image_info(image_bytes: bytes) -> dict:
    """
    获取图片基本信息

    Returns:
        dict: {width, height, format, size_bytes}
    """
    img = Image.open(io.BytesIO(image_bytes))
    return {
        "width": img.width,
        "height": img.height,
        "format": img.format,
        "mode": img.mode,
        "size_bytes": len(image_bytes),
    }