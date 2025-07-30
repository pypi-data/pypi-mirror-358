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
    convert_jpg_to_webp,
    # convert_webp_to_png,
)

# ✅ DYNAMIC CONVERSION MAP
conversion_map = {
    ("png", "jpg"): convert_png_to_jpg,
    ("jpg", "png"): convert_jpg_to_png,
    ("jpg", "webp"): convert_jpg_to_webp,
    # ("webp", "png"): convert_webp_to_png,
}


def show_welcome():
    print(r"""                                                                          
          .--.   _..._    __  __   ___                          __.....__      
          |__| .'     '. |  |/  `.'   `.            .--./)  .-''         '.    
          .--..   .-.   .|   .-.  .-.   '          /.''\\  /     .-''"'-.  `.  
          |  ||  '   '  ||  |  |  |  |  |    __   | |  | |/     /________\   \ 
.--------.|  ||  |   |  ||  |  |  |  |  | .:--.'.  \`-' / |                  | 
|____    ||  ||  |   |  ||  |  |  |  |  |/ |   \ | /("'`  \    .-------------' 
    /   / |  ||  |   |  ||  |  |  |  |  |`" __ | | \ '---. \    '-.____...---. 
  .'   /  |__||  |   |  ||__|  |__|  |__| .'.''| |  /'""'.\ `.             .'  
 /    /___    |  |   |  |                / /   | |_||     ||  `''-...... -'    
|         |   |  |   |  |                \ \._,\ '/\'. __//                    
|_________|   '--'   '--'                 `--'  `"  `'---'                     
              \033[1;36mZinMage v0.1.4 - Image Conversion CLI\033[0m
    """)

    print("📌 \033[1mUsage Examples:\033[0m")
    print("  ▶ zinmage convert input.png --to jpg")
    print("  ▶ zinmage convert photo.jpg --to png")
    print("  ▶ zinmage convert banner.jpg --to webp")

    print("\n🔧 \033[1mFor help:\033[0m zinmage --help")
    print("🌐 \033[1mDocs:\033[0m https://github.com/tinprogrammers/zinmage\n")



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