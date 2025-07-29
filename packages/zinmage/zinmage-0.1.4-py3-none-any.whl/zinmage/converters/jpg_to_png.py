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

def convert_jpg_to_png(input_path: str, output_path: Optional[str] = None) -> str:
    log_start("JPG ➜ PNG Conversion")

    if not input_path.lower().endswith(".jpg") and not input_path.lower().endswith(".jpeg"):
        log_error("Only JPG/JPEG files are supported.")
        raise ValueError("Only JPG/JPEG files are supported by this function.")

    try:
        log_info(f"Opening image: {input_path}")
        img = Image.open(input_path)
    except FileNotFoundError:
        log_error(f"File not found: {input_path}")
        raise

    if not output_path:
        output_path = os.path.splitext(input_path)[0] + ".png"

    img.save(output_path, "PNG")

    log_success(f"Image converted successfully → {output_path}")
    log_done("JPG ➜ PNG Conversion")

    return output_path
