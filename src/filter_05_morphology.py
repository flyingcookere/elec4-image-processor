import cv2
import numpy as np

def apply(
    lineart_bw,
    remove_specks_area=120,
    close_ksize=3,
    thicken_ksize=3,
    thicken_iters=1,
    auto_binarize=True,
    auto_invert=True,
):
    """
    Polishing for sketch/colouring page:
    - removes small specks
    - closes broken strokes
    - thickens slightly (line weight)

    Input: ideally black lines on white background (uint8).
    Output: black lines on white background (uint8, 0/255).
    """
    if lineart_bw is None:
        raise ValueError("lineart_bw is None")

    # --- ensure 1-channel uint8 ---
    img = lineart_bw
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)

    # --- binarize (important for connected components + morphology) ---
    if auto_binarize:
        # Otsu makes it stable even if input has gray values
        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # --- make sure it's black lines on white background ---
    # If background is mostly dark, invert it.
    if auto_invert:
        # simple heuristic: if mean is dark, invert
        if img.mean() < 127:
            img = 255 - img

    # Safety: kernel sizes should be >=1 and odd
    def _odd_ksize(k):
        k = int(max(1, k))
        return k if (k % 2 == 1) else k + 1

    close_ksize = _odd_ksize(close_ksize)
    thicken_ksize = _odd_ksize(thicken_ksize)
    thicken_iters = int(max(0, thicken_iters))
    remove_specks_area = int(max(0, remove_specks_area))

    # Convert to "ink mask" (white ink = 255) for component filtering
    ink = 255 - img  # ink pixels become 255, background 0

    # Ensure strictly binary
    ink = (ink > 0).astype(np.uint8) * 255

    # --- Remove tiny components ---
    if remove_specks_area > 0:
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(ink, connectivity=8)
        cleaned = np.zeros_like(ink)
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= remove_specks_area:
                cleaned[labels == i] = 255
    else:
        cleaned = ink

    # --- Close gaps (connect broken strokes) ---
    if close_ksize > 1:
        close_k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_ksize, close_ksize))
        closed = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, close_k, iterations=1)
    else:
        closed = cleaned

    # --- Thicken strokes slightly ---
    if thicken_ksize > 1 and thicken_iters > 0:
        thick_k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (thicken_ksize, thicken_ksize))
        thick = cv2.dilate(closed, thick_k, iterations=thicken_iters)
    else:
        thick = closed

    # Back to black lines on white
    final = 255 - thick
    return final
