import cv2
import numpy as np

def apply(lineart_bw, remove_specks_area=50, thicken_ksize=3, thicken_iters=1):
    """
    Polishes the trace and allows for line weight adjustment.
    """
    # Ensure grayscale
    if len(lineart_bw.shape) == 3:
        img = cv2.cvtColor(lineart_bw, cv2.COLOR_BGR2GRAY)
    else:
        img = lineart_bw.copy()

    # 1. Invert (Ink = 255)
    ink = 255 - img
    
    # 2. Remove small noise/specks
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(ink, connectivity=8)
    cleaned_ink = np.zeros_like(ink)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= remove_specks_area:
            cleaned_ink[labels == i] = 255

    # 3. THICKEN LINES (The 'Line Weight' part)
    if thicken_ksize > 1:
        # Create a circular kernel for smoother thickening
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (thicken_ksize, thicken_ksize))
        cleaned_ink = cv2.dilate(cleaned_ink, kernel, iterations=thicken_iters)

    # 4. Final Smoothing (Makes it look like a vector trace)
    smoothed = cv2.medianBlur(cleaned_ink, 3)

    return 255 - smoothed