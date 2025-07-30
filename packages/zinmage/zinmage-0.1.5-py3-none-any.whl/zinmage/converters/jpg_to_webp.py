from PIL import Image
import os
from typing import Optional

from zinmage.utils.helpers import (
    log_success,
    log_error,
    log_start,
    log_done,
    log_info
)

def convert_jpg_to_webp(input_path: str, output_path: Optional[str] = None, quality: int = 80) -> str:
    log_start("JPG ➜ WebP Conversion")

    if not input_path.lower().endswith((".jpg", ".jpeg")):
        log_error("Only JPG/JPEG files are supported.")
        raise ValueError("Only JPG/JPEG files are supported by this function.")

    try:
        log_info(f"Opening image: {input_path}")
        img = Image.open(input_path)
    except FileNotFoundError:
        log_error(f"File not found: {input_path}")
        raise

    if not output_path:
        output_path = os.path.splitext(input_path)[0] + ".webp"

    img.save(output_path, "WEBP", quality=quality)

    log_success(f"Image converted successfully → {output_path}")
    log_done("JPG ➜ WebP Conversion")

    return output_path
