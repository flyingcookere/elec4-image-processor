import os
import subprocess
import pytest
import cv2

my_env = os.environ.copy()
my_env["PYTHONIOENCODING"] = "utf-8"

def test_filters_execution():
    input_file = "input/apple.jpg"
    # Run the script
    result = subprocess.run(['python', 'src/main.py', input_file], 
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
    input_path = "input/apple.jpg"
    
    original = cv2.imread(input_path)
    processed = cv2.imread(output_path)
    
    assert processed is not None, f"File {output_path} not found!"
    
    orig_sharpness = cv2.Laplacian(original, cv2.CV_64F).var()
    proc_sharpness = cv2.Laplacian(processed, cv2.CV_64F).var()
    
    assert proc_sharpness < orig_sharpness

def test_background_removal_logic():
    # Update this to whatever the script names the background-removed file
    output_path = "output/01_fg_mask.png" 
    output_path = "output/01_subject.png" 

    
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


    