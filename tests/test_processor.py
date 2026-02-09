import os
import sys
import shutil
import subprocess
import pytest
import cv2
import numpy as np

# Set environment to handle UTF-8 encoding for cross-platform compatibility
my_env = os.environ.copy()
my_env["PYTHONIOENCODING"] = "utf-8"

# Configuration constants
ASSET_DIR = "tests/assets"
TEST_IMAGES = ["isda.jpg", "tota.jpg"]


# --- FIXTURES ---

@pytest.fixture(params=TEST_IMAGES, scope="function")
def workspace(request):
    """
    Setup: Prepares the input/output directories and runs the processor.
    Teardown: Cleans up the files after each test case.
    """
    image_name = request.param
    name, _ = os.path.splitext(image_name)

    # Ensure project structure exists
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    input_path = os.path.join("input", image_name)
    out_dir = os.path.join("output", name)

    # Step 1: Copy asset to the input folder for the script to process
    shutil.copy(os.path.join(ASSET_DIR, image_name), input_path)

    # Step 2: Run main.py as a subprocess (One-shot execution)
    result = subprocess.run(
        [sys.executable, "src/main.py", input_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=my_env,
        timeout=180
    )

    # Assert that the script didn't crash before checking image data
    assert result.returncode == 0, (
        f"Execution failed for {image_name}.\n"
        + "STDOUT:\n" + result.stdout + "\n"
        + "STDERR:\n" + result.stderr
    )

    yield input_path, out_dir

    # Step 3: Cleanup to keep the repository clean (DevOps Best Practice)
    if os.path.exists(input_path):
        os.remove(input_path)
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)


# --- TEST CASES ---

def test_grayscale_filter_logic(workspace):
    """Verifies that the grayscale filter outputs a single-channel look (B=G=R)."""
    _, out_dir = workspace
    img = cv2.imread(os.path.join(out_dir, "03_grayscale.png"))
    assert img is not None, "Grayscale image not found."

    b, g, r = cv2.split(img)
    assert (b == g).all() and (g == r).all()


def test_blur_filter_logic(workspace):
    """Verifies that the Gaussian blur actually reduces image sharpness."""
    input_path, out_dir = workspace
    original = cv2.imread(input_path)
    processed = cv2.imread(os.path.join(out_dir, "02_gaussian_blur.png"))

    assert original is not None and processed is not None

    orig_sharpness = cv2.Laplacian(original, cv2.CV_64F).var()
    proc_sharpness = cv2.Laplacian(processed, cv2.CV_64F).var()
    
    # Allow a tiny margin for floating point errors
    assert proc_sharpness <= orig_sharpness + 1e-6


def test_background_removal_logic(workspace):
    """Checks if the background removal results in a white background (high mean)."""
    _, out_dir = workspace
    img = cv2.imread(os.path.join(out_dir, "01_subject_on_white.png"))
    assert img is not None

    # Check a 10x10 pixel patch in the corner for white pixels
    patch = img[0:10, 0:10]
    assert patch.mean() > 235
    assert img.std() > 0  # Ensure the image isn't just a blank white square


def test_edge_detect_logic(workspace):
    """Ensures the raw line art has a reasonable amount of white space."""
    _, out_dir = workspace
    img = cv2.imread(os.path.join(out_dir, "04_lineart_raw.png"), cv2.IMREAD_GRAYSCALE)
    assert img is not None

    white_ratio = np.mean(img == 255)
    assert 0.30 <= white_ratio <= 0.99


def test_morphology_logic(workspace):
    """Ensures the coloring book output is high contrast (mostly black or white)."""
    _, out_dir = workspace
    img = cv2.imread(os.path.join(out_dir, "05_coloring_book.png"), cv2.IMREAD_GRAYSCALE)
    assert img is not None

    # Ratio of pixels that are 'gray' instead of pure black/white
    gray_ratio = np.mean((img > 20) & (img < 235))
    assert gray_ratio < 0.25


def test_line_quality_metrics(workspace):
    """Measures the connectivity and presence of lines in the final output."""
    _, out_dir = workspace
    img = cv2.imread(os.path.join(out_dir, "05_coloring_book.png"), cv2.IMREAD_GRAYSCALE)
    assert img is not None

    # Invert to count the 'ink' as foreground
    ink_mask = 255 - img
    _, ink_bin = cv2.threshold(ink_mask, 10, 255, cv2.THRESH_BINARY)
    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(ink_bin, connectivity=8)

    assert num_labels > 1  # Background + at least one line
    assert np.mean(stats[1:, cv2.CC_STAT_AREA]) > 3  # Average segment must be meaningful
