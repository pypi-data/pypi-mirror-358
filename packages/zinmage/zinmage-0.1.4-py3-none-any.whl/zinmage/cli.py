import argparse
import os
from zinmage.utils.helpers import (
    log_info,
    log_error,
    log_start,
    log_success,
    log_done,
)

# ✅ IMPORT ALL AVAILABLE CONVERSIONS
from zinmage import (
    convert_png_to_jpg,
    convert_jpg_to_png,
    # convert_jpg_to_webp,
    # convert_webp_to_png,
)

# ✅ DYNAMIC CONVERSION MAP
conversion_map = {
    ("png", "jpg"): convert_png_to_jpg,
    ("jpg", "png"): convert_jpg_to_png,
    # ("jpg", "webp"): convert_jpg_to_webp,
    # ("webp", "png"): convert_webp_to_png,
}


def show_welcome():
    print("\n🖼️  Welcome to \033[1;36mZinmage v0.1.4\033[0m")
    print("📦 A minimalist image conversion tool for developers & creators.")
    print("-" * 60)
    print("\n✨ Features:")
    print("  🔄 Convert PNG ⇄ JPG")
    print("  🧪 JPG ⇨ WEBP (coming soon)")
    print("  🚀 CLI & Python library support")
    print("  🧠 Smart format detection")
    print("  💻 Fully open-source")

    print("\n📌 Usage Examples:")
    print("  ▶ zinmage convert input.png --to jpg")
    print("  ▶ zinmage convert photo.jpg --to png")

    print("\n🔧 For help: zinmage --help")
    print("🌐 Docs: https://github.com/tinprogrammers/zinmage\n")


def main():
    parser = argparse.ArgumentParser(description="🖼 Zinmage - Minimal Image Converter")
    subparser = parser.add_subparsers(dest="command")

    convert_parser = subparser.add_parser("convert", help="Convert image formats")
    convert_parser.add_argument("input", help="Input image file path")
    convert_parser.add_argument("--to", required=True, help="Target format (jpg, png, webp...)")

    args = parser.parse_args()

    # 🖼️ Show welcome screen if no command
    if args.command is None:
        show_welcome()
        return

    if args.command == "convert":
        input_path = args.input
        target_format = args.to.lower()

        if not os.path.isfile(input_path):
            log_error(f"❌ File not found: {input_path}")
            return

        input_ext = os.path.splitext(input_path)[1].lower().replace(".", "")
        key = (input_ext, target_format)

        if key in conversion_map:
            log_start(f"{input_ext.upper()} ➜ {target_format.upper()} Conversion")
            try:
                conversion_map[key](input_path)
                log_success("Conversion complete.")
            except Exception as e:
                log_error(f"Unexpected error: {e}")
            log_done("Conversion finished")
        else:
            log_error(f"Conversion from {input_ext} → {target_format} is not supported.")

    else:
        log_error("Unknown command.")