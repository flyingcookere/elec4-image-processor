import cv2
import numpy as np

def apply(gray_image, fg_mask):
    """
    TRACING STYLE: Focuses on clean, high-contrast line extraction.
    """
    if gray_image is None or fg_mask is None:
        raise ValueError("Missing inputs")

    # 1. Heavy Noise Reduction (keeps edges, kills textures)
    # Using bilateral filter heavily to get that 'anime' flat look
    smooth = cv2.bilateralFilter(gray_image, 9, 75, 75)

    # 2. Adaptive Thresholding (This is the secret for 'tracing' look)
    # It looks at local neighborhoods to decide if a pixel is a line
    lineart = cv2.adaptiveThreshold(
        smooth, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        15, # Block size (adjust for line thickness)
        2   # Constant subtracted from mean (adjust to clean noise)
    )

    # 3. Clean the background
    # Ensure anything outside the mask is pure white
    lineart[fg_mask == 0] = 255

    return lineart