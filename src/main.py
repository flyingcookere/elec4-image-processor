import os
import sys
import cv2

from filter_01_bg_removal import apply as bg_remove
from filter_02_gaussian_blur import apply as blur
from filter_03_grayscale import apply as to_gray
from filter_04_edge_detect import apply as outline_edges
from filter_05_morphology import apply as refine_outline


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_image>")
        sys.exit(1)

    input_path = sys.argv[1]
    image = cv2.imread(input_path)

    if image is None:
        print("❌ Image not found:", input_path)
        sys.exit(1)

    os.makedirs("output", exist_ok=True)

    # FILTER 1: AI BG removal
    subject, fg_mask = bg_remove(image)
    cv2.imwrite("output/01_subject_on_white.png", subject)
    cv2.imwrite("output/01_fg_mask.png", fg_mask)

    # Optional loose mask (helps not cut hair edges)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    fg_mask_loose = cv2.dilate(fg_mask, k, iterations=1)
    cv2.imwrite("output/01_fg_mask_loose.png", fg_mask_loose)

    # FILTER 2: Blur
    blurred = blur(subject, ksize=3)
    cv2.imwrite("output/02_gaussian_blur.png", blurred)

    # FILTER 3: Gray
    gray = to_gray(blurred)
    cv2.imwrite("output/03_grayscale.png", gray)

 # FILTER 4: more detail lines
    lineart_bw = outline_edges(
    gray, fg_mask,
    canny_low=55, canny_high=155,
    bilateral_sigmaColor=110,
    bilateral_sigmaSpace=110,

    inner_weight=0.55,  # raise to add facial details
    outer_weight=1.0
    )
    cv2.imwrite("output/04_lineart_raw.png", lineart_bw)


    # FILTER 5: Morphology polish
    coloring = refine_outline(
        lineart_bw,
        remove_specks_area=25,
        close_ksize=3,
        thicken_ksize=3,
        thicken_iters=1
    )
    cv2.imwrite("output/05_coloring_book.png", coloring)

    print("✅ DONE. Outputs saved in /output")


if __name__ == "__main__":
    main()
