import os
import subprocess
import pytest
import cv2
import numpy as np
import glob

my_env = os.environ.copy()
my_env["PYTHONIOENCODING"] = "utf-8"

# Automatically find all images in the input folder
# This ensures we get 'input/tota.jpg' instead of just 'tota.jpg'
input_images = glob.glob(os.path.join("input", "*.jpg")) + glob.glob(os.path.join("input", "*.png"))

@pytest.mark.parametrize("image_path", input_images)
def test_filters_execution(image_path):
    """Checks if the script runs successfully for the given image."""
    result = subprocess.run(['python', 'src/main.py', image_path], 
                            capture_output=True, text=True, encoding='utf-8', env=my_env)
    
    assert "DONE" in result.stdout, f"Execution failed for {image_path}: {result.stdout}"
    assert os.path.exists("output")

@pytest.mark.parametrize("image_path", input_images)
def test_grayscale_filter_logic(image_path):
    """Verifies the Grayscale output."""
    output_path = "output/03_grayscale.png" 
    img = cv2.imread(output_path)
    assert img is not None, f"Grayscale file not found for {image_path}"
    
    b, g, r = cv2.split(img)
    assert (b == g).all() and (g == r).all(), "Grayscale failure: Channels are not equal."

@pytest.mark.parametrize("image_path", input_images)
def test_blur_filter_logic(image_path):
    """Verifies the Gaussian Blur output."""
    output_path = "output/02_gaussian_blur.png"
    original = cv2.imread(image_path)
    processed = cv2.imread(output_path)
    
    assert processed is not None, f"Blur file not found for {image_path}"
    
    orig_sharpness = cv2.Laplacian(original, cv2.CV_64F).var()
    proc_sharpness = cv2.Laplacian(processed, cv2.CV_64F).var()
    
    assert proc_sharpness < orig_sharpness

@pytest.mark.parametrize("image_path", input_images)
def test_background_removal_logic(image_path):
    """Verifies the Background Removal output."""
    output_path = "output/01_subject_on_white.png" 
    img = cv2.imread(output_path)
    assert img is not None, f"BG removal file not found for {image_path}"

    # Check top-left corner for white
    assert all(img[0, 0] == [255, 255, 255]), "BG removal failure: Top-left is not white."
    assert img.std() > 0, "BG removal failure: Output is a solid color."

@pytest.mark.parametrize("image_path", input_images)
def test_edge_detect_logic(image_path):
    """Verifies the Edge Detection/Lineart output."""
    output_path = "output/04_lineart_raw.png"
    img = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    assert img is not None, f"Edge detect file not found for {image_path}"
    
    white_ratio = np.sum(img == 255) / img.size
    assert white_ratio > 0.70, "Edge detection failure: Too much noise."

@pytest.mark.parametrize("image_path", input_images)
def test_morphology_logic(image_path):
    """Verifies the Morphology/Polish output."""
    output_path = "output/05_coloring_book.png"
    img = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    assert img is not None, f"Morphology file not found for {image_path}"

    # Check for binarization
    grays = np.logical_and(img > 20, img < 235)
    assert np.sum(grays) / img.size < 0.05, "Morphology failure: Not binarized."

@pytest.mark.parametrize("image_path", input_images)
def test_line_quality_metrics(image_path):
    """Verifies the final line quality and connectivity."""
    output_path = "output/05_coloring_book.png" 
    img = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    assert img is not None

    ink_mask = 255 - img 
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(ink_mask, connectivity=8)

    assert num_labels > 1, f"Quality failure: No lines detected in {image_path}."

    sizes = stats[1:, cv2.CC_STAT_AREA]
    avg_line_length = np.mean(sizes)
    assert avg_line_length > 5, f"Quality failure: Lines too broken in {image_path}."