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

def convert_png_to_jpg(input_path: str, output_path: Optional[str] = None) -> str:
    log_start("PNG ➜ JPG Conversion")

    if not input_path.lower().endswith(".png"):
        log_error("Only PNG files are supported.")
        raise ValueError("Only PNG files are supported by this function.")

    try:
        log_info(f"Opening image: {input_path}")
        img = Image.open(input_path).convert("RGB")
    except FileNotFoundError:
        log_error(f"File not found: {input_path}")
        raise

    if not output_path:
        output_path = os.path.splitext(input_path)[0] + ".jpg"

    img.save(output_path, "JPEG")

    log_success(f"Image converted successfully → {output_path}")
    log_done("PNG ➜ JPG Conversion")

    return output_path
