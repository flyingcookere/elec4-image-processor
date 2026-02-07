import os
import sys
import cv2

from filter_02_gaussian_blur import apply as blur
from filter_03_grayscale import apply as to_gray


def main():
    # Check for input image argument
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_image>")
        sys.exit(1)

    input_path = sys.argv[1]
    image = cv2.imread(input_path)

    if image is None:
        print("❌ Image not found:", input_path)
        sys.exit(1)

    os.makedirs("output", exist_ok=True)

    # FILTER 2: Gaussian Blur (noise reduction)
    blurred = blur(image, ksize=11)
    cv2.imwrite("output/02_gaussian_blur.png", blurred)

    # FILTER 3: Grayscale conversion
    gray = to_gray(blurred)
    cv2.imwrite("output/03_grayscale.png", gray)

    print("✅ DONE. Outputs saved in /output")


if __name__ == "__main__":
    main()
