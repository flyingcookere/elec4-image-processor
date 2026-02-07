import cv2
import numpy as np

def _xdog(gray, sigma=0.8, k=1.6, gamma=0.98, eps=0.035, phi=12.0):
    """
    XDoG (eXtended Difference of Gaussians)
    Produces sketch-like lines without filling silhouettes.
    Returns: edges in range [0..255] (white edges on black-ish)
    """
    g1 = cv2.GaussianBlur(gray, (0, 0), sigma)
    g2 = cv2.GaussianBlur(gray, (0, 0), sigma * k)
    dog = g1 - gamma * g2

    # Normalize to [-1, 1]
    dog = dog.astype(np.float32)
    dog = dog / (np.max(np.abs(dog)) + 1e-6)

    # Soft threshold (tanh) -> [-1..1]
    out = np.tanh(phi * (dog - eps))
    out = (out + 1.0) * 0.5  # -> [0..1]

    # Invert so edges become bright
    out = (1.0 - out) * 255.0
    return out.astype(np.uint8)

def apply(
    gray_image,
    fg_mask,
    # outer contour
    canny_low=60,
    canny_high=160,

    # texture suppression (higher = smoother, less texture)
    bilateral_d=7,
    bilateral_sigmaColor=90,
    bilateral_sigmaSpace=90,

    # xdog (interior lines)
    xdog_sigma=0.9,
    xdog_k=1.6,
    xdog_gamma=0.985,
    xdog_eps=0.030,
    xdog_phi=14.0,

    # mixing weights
    outer_weight=1.0,
    inner_weight=0.55,

    # keep hair/edges safe
    use_mask_loose=True,
    loose_ksize=13,
):
    """
    LINE-ONLY but recognizable:
    - Outer contour from Canny
    - Interior strokes from XDoG (after edge-preserving smooth)
    Output: BLACK lines on WHITE (uint8 0/255-ish)
    """
    if gray_image is None:
        raise ValueError("gray_image is None")
    if fg_mask is None:
        raise ValueError("fg_mask is None")

    mask = fg_mask.copy()
    if use_mask_loose:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (loose_ksize, loose_ksize))
        mask = cv2.dilate(mask, k, iterations=1)

    # Only subject
    subject = cv2.bitwise_and(gray_image, gray_image, mask=mask)

    # Important: set outside to white so it won't generate lines
    subject_bg_white = subject.copy()
    subject_bg_white[mask == 0] = 255

    # Edge-preserving smooth -> removes shirt texture/noise
    smooth = cv2.bilateralFilter(
        subject_bg_white, bilateral_d, bilateral_sigmaColor, bilateral_sigmaSpace
    )

    # OUTER: clean contour
    outer = cv2.Canny(smooth, canny_low, canny_high)
    outer[mask == 0] = 0

    # INNER: XDoG strokes (eyes, mouth, folds)
    inner = _xdog(
        smooth,
        sigma=xdog_sigma,
        k=xdog_k,
        gamma=xdog_gamma,
        eps=xdog_eps,
        phi=xdog_phi
    )
    # Make inner strictly "edge-ish" (remove gray wash)
    _, inner = cv2.threshold(inner, 200, 255, cv2.THRESH_BINARY)
    inner[mask == 0] = 0

    # Combine (white edges on black)
    edges = cv2.addWeighted(outer, outer_weight, inner, inner_weight, 0)
    _, edges = cv2.threshold(edges, 20, 255, cv2.THRESH_BINARY)

    # Convert to black lines on white
    lineart = 255 - edges
    return lineart
