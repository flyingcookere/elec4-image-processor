# [Project Title: Automated Image Processing Pipeline]
Automated Image Processing using DevOps CI Pipeline

## Requirements!!
Python 3 | OpenCV | GitHub Actions | PyTest 

## 📝 Project Overview
The Automated Image Processing Pipeline is a Python-based computer vision system that applies a sequence of OpenCV image processing techniques to extract clean object outlines from images.

The pipeline removes background noise, smooths image textures, converts images into grayscale, detects edges, and refines contours using morphological operations. These steps work together to transform raw images into simplified structural representations suitable for visualization or further analysis.

The system demonstrates how multiple image-processing filters can be combined into a single automated workflow.

## 🖼️ OpenCV Function Reference
The following OpenCV functions were used in this milestone:

* cv2.cvtColor() — Converts images between color spaces (BGR, RGB, Grayscale)
* cv2.GaussianBlur() — Applies Gaussian smoothing to reduce noise
* cv2.bilateralFilter() — Smooths image while preserving edges
* cv2.Canny() — Detects edges in the image
* cv2.threshold() — Converts grayscale image into binary image
* cv2.addWeighted() — Blends two images together
* cv2.bitwise_and() — Applies masking to isolate image regions
* cv2.getStructuringElement() — Creates kernel for morphological operations
* cv2.morphologyEx() — Performs morphological transformations
* cv2.dilate() — Expands object boundaries in a binary image

## ▶️ How to Run Locally
Follow these steps to run the project on your computer:

1. Clone the repository
git clone <repository-url>

2. Navigate into the project folder
cd project-folder

3. Install dependencies
pip install opencv-python numpy pytest

4. Run the image processing script
python main.py



Prerequisites
Python Version: 3.10+
