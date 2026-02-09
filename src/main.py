import os
import time
import cv2

from filter_01_bg_removal import apply as bg_remove
from filter_02_gaussian_blur import apply as blur
from filter_03_grayscale import apply as to_gray
from filter_04_edge_detect import apply as outline_edges
from filter_05_morphology import apply as refine_outline

INPUT_DIR = "input"
OUTPUT_DIR = "output"
VALID_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp")


def is_file_stable(path: str, wait_s: float = 0.8) -> bool:
    """
    Helps avoid reading while the file is still copying.
    Checks file size doesn't change within wait_s seconds.
    """
    try:
        s1 = os.path.getsize(path)
        time.sleep(wait_s)
        s2 = os.path.getsize(path)
        return s1 == s2 and s1 > 0
    except OSError:
        return False


def process_one_image(input_path: str):
    filename = os.path.basename(input_path)
    name, _ = os.path.splitext(filename)

    image = cv2.imread(input_path)
    if image is None:
        print(f"❌ Skipped (cannot read): {input_path}")
        return

    out_dir = os.path.join(OUTPUT_DIR, name)
    os.makedirs(out_dir, exist_ok=True)

    subject, fg_mask = bg_remove(image)
    cv2.imwrite(os.path.join(out_dir, "01_subject_on_white.png"), subject)
    cv2.imwrite(os.path.join(out_dir, "01_fg_mask.png"), fg_mask)

    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    fg_mask_loose = cv2.dilate(fg_mask, k, iterations=1)
    cv2.imwrite(os.path.join(out_dir, "01_fg_mask_loose.png"), fg_mask_loose)

    blurred = blur(subject, ksize=3)
    cv2.imwrite(os.path.join(out_dir, "02_gaussian_blur.png"), blurred)

    gray = to_gray(blurred)
    cv2.imwrite(os.path.join(out_dir, "03_grayscale.png"), gray)

    # NOTE: you can choose fg_mask or fg_mask_loose here
    lineart_bw = outline_edges(gray, fg_mask)
    cv2.imwrite(os.path.join(out_dir, "04_lineart_raw.png"), lineart_bw)

    coloring = refine_outline(
        lineart_bw,
        remove_specks_area=50,
        thicken_ksize=3,
        thicken_iters=1
    )
    cv2.imwrite(os.path.join(out_dir, "05_coloring_book.png"), coloring)

    print(f"✅ DONE: {filename} -> {out_dir}")


def watch_and_process(poll_seconds: float = 1.0):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.isdir(INPUT_DIR):
        print(f"❌ '{INPUT_DIR}/' folder not found. Create it and put images inside.")
        return

    print("👀 Watching input/ ... (Press CTRL+C to stop)")
    processed = set()  # filenames already processed

    while True:
        try:
            files = [
                f for f in os.listdir(INPUT_DIR)
                if f.lower().endswith(VALID_EXTS)
            ]

            for f in files:
                in_path = os.path.join(INPUT_DIR, f)

                # skip if already processed this run
                if f in processed:
                    continue

                # wait until file copy is finished
                if not is_file_stable(in_path):
                    continue

                process_one_image(in_path)
                processed.add(f)

            time.sleep(poll_seconds)

        except KeyboardInterrupt:
            print("\n🛑 Stopped watching.")
            break


def main():
    watch_and_process(poll_seconds=1.0)


if __name__ == "__main__":
    main()
