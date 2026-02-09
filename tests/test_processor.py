import os
import shutil
import subprocess
import pytest
import cv2
import numpy as np

my_env = os.environ.copy()
my_env["PYTHONIOENCODING"] = "utf-8"

# 1. SETUP ASSETS
ASSET_DIR = "tests/assets"
TEST_IMAGES = ["ekal.jpg", "isda.jpg", "tota.jpg"]

@pytest.fixture(params=TEST_IMAGES, scope="function")
def workspace(request):
    """
    SETUP: Copies the image from assets to input and runs the processor.
    """
    image_name = request.param
    input_path = os.path.join("input", image_name)
    
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # Copy the 'Gold Standard' image
    shutil.copy(os.path.join(ASSET_DIR, image_name), input_path)
    
    # Run main.py so the output files exist for your logic tests
    subprocess.run(['python', 'src/main.py', input_path], 
                   capture_output=True, text=True, encoding='utf-8', env=my_env)
    
    yield input_path

    # TEARDOWN: Wipe the workspace so GitHub stays clean
    if os.path.exists(input_path):
        os.remove(input_path)
    for f in os.listdir("output"):
        if f.endswith(".png"):
            os.remove(os.path.join("output", f))

# 2. YOUR INDIVIDUAL FILTER TESTS
# We replaced '@pytest.mark.parametrize' with your 'workspace' fixture.

def test_grayscale_filter_logic(workspace):
    """Verifies the Grayscale output."""
    output_path = "output/03_grayscale.png" 
    img = cv2.imread(output_path)
    assert img is not None
    
    b, g, r = cv2.split(img)
    assert (b == g).all() and (g == r).all()

def test_blur_filter_logic(workspace):
    """Verifies the Gaussian Blur output."""
    output_path = "output/02_gaussian_blur.png"
    original = cv2.imread(workspace) # 'workspace' provides the input path
    processed = cv2.imread(output_path)
    
    assert processed is not None
    orig_sharpness = cv2.Laplacian(original, cv2.CV_64F).var()
    proc_sharpness = cv2.Laplacian(processed, cv2.CV_64F).var()
    assert proc_sharpness < orig_sharpness

def test_background_removal_logic(workspace):
    """Verifies the Background Removal output."""
    output_path = "output/01_subject_on_white.png" 
    img = cv2.imread(output_path)
    assert img is not None
    assert all(img[0, 0] == [255, 255, 255])
    assert img.std() > 0

def test_edge_detect_logic(workspace):
    """Verifies the Edge Detection/Lineart output."""
    output_path = "output/04_lineart_raw.png"
    img = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    assert img is not None
    white_ratio = np.sum(img == 255) / img.size
    assert white_ratio > 0.70

def test_morphology_logic(workspace):
    """Verifies the Morphology/Polish output."""
    output_path = "output/05_coloring_book.png"
    img = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    assert img is not None
    grays = np.logical_and(img > 20, img < 235)
    assert np.sum(grays) / img.size < 0.05

def test_line_quality_metrics(workspace):
    """Verifies the final line quality and connectivity."""
    output_path = "output/05_coloring_book.png" 
    img = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    assert img is not None
    
    ink_mask = 255 - img 
    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(ink_mask, connectivity=8)
    assert num_labels > 1
    
    avg_line_length = np.mean(stats[1:, cv2.CC_STAT_AREA])
    assert avg_line_length > 5