from PIL import Image
import os

def convert_png_to_jpg(input_path: str, output_path: str = None) -> str:
    """Convert a PNG image to JPG format."""

    if not input_path.lower().endswith(".png"):
        raise ValueError("Only PNG files are supported by this function.")

    try:
        img = Image.open(input_path).convert("RGB")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {input_path}")

    if not output_path:
        output_path = os.path.splitext(input_path)[0] + ".jpg"

    img.save(output_path, "JPEG")
    return output_path
