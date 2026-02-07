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

1. Pre-Processing (Cleaning the Data)
cv2.cvtColor(): The first step in the pipeline. It converts the raw BGR image to Grayscale to reduce data complexity.

cv2.GaussianBlur(): Used to reduce pixel noise by averaging pixel values with a Gaussian kernel.

cv2.bilateralFilter(): A more advanced smoothing technique used to remove noise while keeping the edges sharp.

2. Segmentation & Edge Detection (Finding Shapes)
cv2.Canny(): The primary edge detection algorithm used to find the outlines of objects based on intensity gradients.

cv2.threshold(): Converts a grayscale image into a Binary (Black and White) image, effectively separating the "object" from the "background."

3. Morphological Operations (Refining the Outline)
cv2.getStructuringElement(): Defines the "shape" (kernel) used for morphological math.

cv2.morphologyEx(): Performs advanced operations like "Closing" or "Opening" to remove tiny holes inside the detected objects.

cv2.dilate(): Expands the white pixels in a binary image to make thin outlines thicker and more visible.

4. Image Logic & Composition
cv2.bitwise_and(): A bitwise operation used to apply a "mask" to an image (e.g., showing only the part of the image inside a detected shape).

cv2.addWeighted(): Blends two images together (often used to overlay detected edges back onto the original photo for visualization).

## ▶️ How to Run Locally
Follow these steps to run the project on your computer:

1. Clone the repository
(git clone < repository-url >)
2. Navigate into the project folder
(cd project-folder)
3. Install dependencies
(pip install opencv-python numpy pytest)
4. Run the image processing script
(python main.py)

## 🚦 Status & Traceability Matrix

| ID | System Requirement | Status | Verification (Link) |
| :--- | :--- | :--- | :--- |
| **REQ-01** | Auto-detect images in input directory | ✅ DONE | [Milestone 2](https://github.com/flyingcookere/elec4-image-processor/milestone/2) |
| **REQ-02** | Apply 2+ OpenCV techniques | ✅ DONE | [Milestone 2](https://github.com/flyingcookere/elec4-image-processor/milestone/2), [Milestone 3](https://github.com/flyingcookere/elec4-image-processor/milestone/3) |
| **REQ-03** | Save to output directory | ✅ DONE | [Milestone 4] |
| **REQ-04** | GitHub Actions Pipeline (Run on Push) | ✅ DONE | [Milestone 1](https://github.com/flyingcookere/elec4-image-processor/milestone/1) |

## ✨ Key Features

* **Automated Detection**: Script scans for supported image formats (JPG, PNG) in `/input`.
* **OpenCV Suite**: High-performance transformations including Grayscale and Edge Detection.
* **Validation Layer**: Integrated **PyTest** suite for logic verification.
* **Infrastructure as Code**: **Docker** support for platform-independent execution.

Prerequisites
Python Version: 3.10+
