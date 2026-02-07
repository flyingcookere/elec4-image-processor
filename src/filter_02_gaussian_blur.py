import cv2

def apply(image, ksize=5):
    ksize = int(ksize)
    if ksize < 3:
        ksize = 3
    if ksize % 2 == 0:
        ksize += 1
    return cv2.GaussianBlur(image, (ksize, ksize), 0)
