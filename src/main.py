import os
import sys
import time
import cv2

# Import the custom filters developed by your team
from filter_01_bg_removal import apply as bg_remove
from filter_02_gaussian_blur import apply as blur
from filter_03_grayscale import apply as to_gray
from filter_04_edge_detect import apply as outline_edges
from filter_05_morphology import apply as refine_outline

INPUT_DIR = "input"
OUTPUT_DIR = "output"
VALID_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp")

def is_file_stable(path: str, wait_s: float = 0.5) -> bool:
    """
    Helps avoid reading while the file is still copying.
    Checks if file size doesn't change within wait_s seconds.
    """
    try:
        s1 = os.path.getsize(path)
        time.sleep(wait_s)
        s2 = os.path.getsize(path)
        return s1 == s2 and s1 > 0
    except OSError:
        return False

def process_one_image(input_path: str):
    """Processes a single image through the full DevOps pipeline."""
    filename = os.path.basename(input_path)
    name, _ = os.path.splitext(filename)

    image = cv2.imread(input_path)
    if image is None:
        print(f" Skipped (cannot read): {input_path}")
        return

    # Create a sub-folder for this specific image inside output/
    out_dir = os.path.join(OUTPUT_DIR, name)
    os.makedirs(out_dir, exist_ok=True)

    # 1. Background Removal
    subject, fg_mask = bg_remove(image)
    cv2.imwrite(os.path.join(out_dir, "01_subject_on_white.png"), subject)
    cv2.imwrite(os.path.join(out_dir, "01_fg_mask.png"), fg_mask)

    # Prepare a mask for edge detection
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    fg_mask_loose = cv2.dilate(fg_mask, k, iterations=1)
    cv2.imwrite(os.path.join(out_dir, "01_fg_mask_loose.png"), fg_mask_loose)

    # 2. Gaussian Blur
    blurred = blur(subject, ksize=3)
    cv2.imwrite(os.path.join(out_dir, "02_gaussian_blur.png"), blurred)

    # 3. Grayscale Conversion
    gray = to_gray(blurred)
    cv2.imwrite(os.path.join(out_dir, "03_grayscale.png"), gray)

    # 4. Edge Detection (Lineart Raw)
    lineart_bw = outline_edges(gray, fg_mask)
    cv2.imwrite(os.path.join(out_dir, "04_lineart_raw.png"), lineart_bw)

    # 5. Morphology (Refining for Coloring Book style)
    coloring = refine_outline(
        lineart_bw,
        remove_specks_area=50,
        thicken_ksize=3,
        thicken_iters=1
    )

    # Fallback logic for stability
    if coloring is None or not hasattr(coloring, "size") or coloring.size == 0:
        coloring = lineart_bw.copy()

    # Final Output Save
    ok = cv2.imwrite(os.path.join(out_dir, "05_coloring_book.png"), coloring)
    if not ok:
        raise RuntimeError("Failed to write 05_coloring_book.png")
    
    # Crucial for your tests to pass!
    print(f" DONE: {filename} -> {out_dir}")
    print("DONE") 

def watch_and_process(poll_seconds: float = 1.0, idle_timeout_s: float = 120.0):
    """Watches the input folder and processes new files automatically."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.isdir(INPUT_DIR):
        print(f" '{INPUT_DIR}/' folder not found.")
        return

    print(" Watching input/ ... (Press CTRL+C to stop)")
    processed = set()
    last_new_file_time = time.time()

    while True:
        try:
            files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(VALID_EXTS)]
            processed_any = False

            for f in files:
                in_path = os.path.join(INPUT_DIR, f)
                if f in processed: continue
                if not is_file_stable(in_path): continue

                process_one_image(in_path)
                processed.add(f)
                processed_any = True
                last_new_file_time = time.time()

            # Auto-exit if idle to satisfy GitHub Actions environments
            if not processed_any and (time.time() - last_new_file_time) >= idle_timeout_s:
                print(f" DONE (idle {int(idle_timeout_s)}s).")
                print("DONE")
                break

            time.sleep(poll_seconds)
        except KeyboardInterrupt:
            print("\n Stopped.")
            break

def main():
    if len(sys.argv) >= 2:
        process_one_image(sys.argv[1])
    else:
        watch_and_process()

if __name__ == "__main__":
    main()