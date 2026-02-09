import os
import subprocess
import pytest
import cv2
import numpy as np
import sys 

my_env = os.environ.copy()
my_env["PYTHONIOENCODING"] = "utf-8"

def test_filters_execution():
    input_file = "input/isda.jpg"
    # Run the script
    result = subprocess.run([sys.executable, 'src/main.py', input_file],
                            capture_output=True, text=True, encoding='utf-8', env=my_env)
    
    assert "DONE" in result.stdout
    # Check if the folder exists
    assert os.path.exists("output")

def test_grayscale_filter_logic():
    # UPDATE THIS to the real name in your output folder
    output_path = "output/03_grayscale.png" 
    
    img = cv2.imread(output_path)
    assert img is not None, f"File {output_path} not found!"
    
    # Check if grayscale (all channels equal)
    b, g, r = cv2.split(img)
    assert (b == g).all() and (g == r).all()

def test_blur_filter_logic():
    # UPDATE THIS to the real name in your output folder
    output_path = "output/02_gaussian_blur.png"
    input_path = "input/tota.jpg"
    
    original = cv2.imread(input_path)
    processed = cv2.imread(output_path)
    
    assert processed is not None, f"File {output_path} not found!"
    
    orig_sharpness = cv2.Laplacian(original, cv2.CV_64F).var()
    proc_sharpness = cv2.Laplacian(processed, cv2.CV_64F).var()
    
    assert proc_sharpness < orig_sharpness

def test_background_removal_logic():
    # Update this to whatever the script names the background-removed file
    output_path = "output/01_fg_mask.png" 
    output_path = "output/01_subject_on_white.png" 

    
    img = cv2.imread(output_path)
    assert img is not None, f"File {output_path} not found!"

    # Verification: Check for "White Background"
    # The filter is designed to place the subject on a pure white background (255, 255, 255)
    # We check if at least some pixels in the corners are pure white
    top_left_pixel = img[0, 0]
    assert all(top_left_pixel == [255, 255, 255]), "Background removal failed: Top-left is not white!"
    
    # Advanced check: Ensure it's not JUST a white square (the subject should exist)
    # If the standard deviation is 0, the whole image is one solid color
    assert img.std() > 0, "Background removal failed: Output is just a solid color!"


def test_edge_detect_logic():
    output_path = "output/04_lineart_raw.png"
    img = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    
    assert img is not None, f"File {output_path} not found!"
    
    # 1. Verification: Is it actually Line Art?
    # Black lines on White background means most pixels should be 255 (white).
    white_pixel_ratio = np.sum(img == 255) / img.size
    assert white_pixel_ratio > 0.80, "Edge detection too noisy! Should be >80% white."

    # 2. Verification: Is it Binarized?
    # A good lineart shouldn't have many 'gray' values. 
    # We check if pixels are mostly 0 or 255.
    grays = np.logical_and(img > 20, img < 235)
    assert np.sum(grays) / img.size < 0.05, "Too many gray pixels; should be high contrast."

def test_morphology_logic():
    input_path = "output/04_lineart_raw.png" # The 'raw' edges
    output_path = "output/05_coloring_book.png" # The 'cleaned' edges
    
    raw = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    clean = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    
    assert clean is not None, "Morphology output missing!"

    # 1. Verification: Speck Removal
    # Ink is 0 (black), so we invert to count white blobs as 'components'
    _, raw_labels = cv2.connectedComponents(255 - raw)
    _, clean_labels = cv2.connectedComponents(255 - clean)
    
    assert np.max(clean_labels) < np.max(raw_labels), "Speck removal failed! Cluster count did not decrease."

    # 2. Verification: Thickening (Dilation)
    # More black pixels (0) means thicker lines.
    raw_ink_count = np.sum(raw == 0)
    clean_ink_count = np.sum(clean == 0)
    
    assert clean_ink_count > raw_ink_count, "Thickening failed! Line weight did not increase."

def test_line_quality_metrics():
    # 1. Path Safety: Ensure the filename matches exactly what's in your output folder
    output_path = "output/05_coloring_book.png" 
    img = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    
    # 2. The Guard: Prevent 'NoneType' errors if the image failed to save/load
    assert img is not None, f"Quality test failed: Could not find or read {output_path}."

    # 3. Invert so lines are 255 (white) for analysis
    ink_mask = 255 - img 
    
    # 4. Connectivity Analysis
    # Connectivity=8 catches diagonal pixels, making line segments feel 'longer'
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(ink_mask, connectivity=8)

    # If num_labels is 1, it means there is only background (no lines found!)
    assert num_labels > 1, "Line quality failed: No lines detected in the image!"

    # 5. Extract Sizes (skipping index 0 which is the background)
    sizes = stats[1:, cv2.CC_STAT_AREA]
    
    # QUALITY CHECK A: Continuity
    avg_line_length = np.mean(sizes)
    assert avg_line_length > 10, f"Line quality poor: Average segment length is only {avg_line_length:.2f}px. Lines are too broken!"

    # QUALITY CHECK B: Speck Removal (The 'Polish' test)
    # Check if there are any tiny noise particles (e.g., smaller than 5 pixels)
    tiny_specks = np.sum(sizes < 5)
    assert tiny_specks == 0, f"Line quality poor: Found {tiny_specks} tiny specks that should have been removed by morphology."