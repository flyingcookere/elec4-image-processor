import os
import sys
import cv2

OUTPUT_DIR = "output"
VALID_EXTS = (".jpg", ".jpeg", ".png")


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <image_path>")
        return

    input_path = sys.argv[1]

    if not input_path.lower().endswith(VALID_EXTS):
        print("❌ Invalid file type")
        return

    image = cv2.imread(input_path)
    if image is None:
        print("❌ Image not found:", input_path)
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    filename = os.path.basename(input_path)
    name, _ = os.path.splitext(filename)
    output_path = os.path.join(OUTPUT_DIR, f"{name}_output.png")

    cv2.imwrite(output_path, image)
    print(f"✅ Saved: {output_path}")
    print("✅ DONE")


if __name__ == "__main__":
    main()
