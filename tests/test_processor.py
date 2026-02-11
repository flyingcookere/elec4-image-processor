import os
import sys
import shutil
import subprocess
import pytest
import cv2
import numpy as np

my_env = os.environ.copy()
my_env["PYTHONIOENCODING"] = "utf-8"

ASSET_DIR = "tests/assets"
TEST_IMAGES = ["image.png", "isda.jpg", "tota.jpg"]

@pytest.fixture(params=TEST_IMAGES, scope="function")
def workspace(request):
    image_name = request.param
    name, _ = os.path.splitext(image_name)

    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    input_path = os.path.join("input", image_name)
    out_dir = os.path.join("output", name)

    # copy asset -> input
    shutil.copy(os.path.join(ASSET_DIR, image_name), input_path)

    # run main one-shot (argument provided so watcher won't run)
    result = subprocess.run(
        [sys.executable, "src/main.py", input_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=my_env,
        timeout=180
    )

    assert result.returncode == 0, (
        "main.py failed.\n"
        + "STDOUT:\n" + result.stdout + "\n"
        + "STDERR:\n" + result.stderr
    )

    yield input_path, out_dir

    # cleanup
    if os.path.exists(input_path):
        os.remove(input_path)
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)


def test_grayscale_filter_logic(workspace):
    _, out_dir = workspace
    img = cv2.imread(os.path.join(out_dir, "03_grayscale.png"))
    assert img is not None

    b, g, r = cv2.split(img)
    assert (b == g).all() and (g == r).all()


def test_blur_filter_logic(workspace):
    input_path, out_dir = workspace
    original = cv2.imread(input_path)
    processed = cv2.imread(os.path.join(out_dir, "02_gaussian_blur.png"))

    assert original is not None
    assert processed is not None

    orig_sharpness = cv2.Laplacian(original, cv2.CV_64F).var()
    proc_sharpness = cv2.Laplacian(processed, cv2.CV_64F).var()
    assert proc_sharpness <= orig_sharpness + 1e-6


def test_background_removal_logic(workspace):
    _, out_dir = workspace
    img = cv2.imread(os.path.join(out_dir, "01_subject_on_white.png"))
    assert img is not None

    patch = img[0:10, 0:10]
    assert patch.mean() > 235
    assert img.std() > 0


def test_edge_detect_logic(workspace):
    _, out_dir = workspace
    img = cv2.imread(os.path.join(out_dir, "04_lineart_raw.png"), cv2.IMREAD_GRAYSCALE)
    assert img is not None

    white_ratio = np.mean(img == 255)
    assert 0.30 <= white_ratio <= 0.99


def test_morphology_logic(workspace):
    _, out_dir = workspace
    img = cv2.imread(os.path.join(out_dir, "05_coloring_book.png"), cv2.IMREAD_GRAYSCALE)
    assert img is not None

    gray_ratio = np.mean((img > 20) & (img < 235))
    assert gray_ratio < 0.25


def test_line_quality_metrics(workspace):
    _, out_dir = workspace
    img = cv2.imread(os.path.join(out_dir, "05_coloring_book.png"), cv2.IMREAD_GRAYSCALE)
    assert img is not None

    ink_mask = 255 - img
    _, ink_bin = cv2.threshold(ink_mask, 10, 255, cv2.THRESH_BINARY)
    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(ink_bin, connectivity=8)

    assert num_labels > 1
    assert np.mean(stats[1:, cv2.CC_STAT_AREA]) > 3