import cv2
import numpy as np
from PIL import Image
import io

from backgroundremover.bg import remove


def apply(image):
    """
    FILTER 1: AI Background Removal using backgroundremover (U^2-Net)
    Returns:
      subject_on_white (BGR)
      fg_mask (uint8 0/255)
    """
    if image is None:
        raise ValueError("No image provided")

    # OpenCV BGR -> PIL RGB
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_rgb = Image.fromarray(rgb)

    # PIL -> PNG bytes (what backgroundremover expects)
    buf = io.BytesIO()
    pil_rgb.save(buf, format="PNG")
    input_bytes = buf.getvalue()

    # backgroundremover returns image bytes (PNG with alpha)
    out_bytes = remove(input_bytes)

    # bytes -> PIL RGBA
    pil_rgba = Image.open(io.BytesIO(out_bytes)).convert("RGBA")
    rgba = np.array(pil_rgba)  # (H,W,4) in RGBA

    # alpha mask
    alpha = rgba[:, :, 3]
    fg_mask = (alpha > 128).astype(np.uint8) * 255

    # subject on white (RGB)
    foreground = rgba[:, :, :3]
    white_bg = np.full_like(foreground, 255)
    a = (alpha.astype(np.float32) / 255.0)[..., None]
    subject_rgb = (foreground * a + white_bg * (1 - a)).astype(np.uint8)

    # RGB -> BGR for OpenCV
    subject_bgr = cv2.cvtColor(subject_rgb, cv2.COLOR_RGB2BGR)

    return subject_bgr, fg_mask
