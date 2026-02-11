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
| **REQ-01** | Auto-detect images in input directory | ✅ DONE | [(https://github.com/flyingcookere/elec4-image-processor/milestone/2)] |
| **REQ-02** | Apply 2+ OpenCV techniques | ✅ DONE | [(https://github.com/flyingcookere/elec4-image-processor/milestone/2), (https://github.com/flyingcookere/elec4-image-processor/milestone/3) ]|
| **REQ-03** | Save to output directory | ✅ DONE | [Milestone 4] |
| **REQ-04** | GitHub Actions Pipeline (Run on Push) | ✅ DONE | [ (https://github.com/flyingcookere/elec4-image-processor/milestone/1) ]|
| **REQ-05** | Advanced Segmentation (GrabCut) | ✅ DONE | [Pull Request #Link](YOUR_GRABCUT_PR_URL_HERE) |
| **REQ-06** | Edge Detection (Canny Filter) | ✅ DONE | [ https://github.com/flyingcookere/elec4-image-processor/milestone/3] |

## ✨ Key Features

* **Automated Detection**: Script scans for supported image formats (JPG, PNG) in `/input`.
* **OpenCV Suite**: High-performance transformations including Grayscale and Edge Detection.
* **Validation Layer**: Integrated **PyTest** suite for logic verification.
* **Infrastructure as Code**: **Docker** support for platform-independent execution.

### 📸 Visual Gallery & Verification

> **Documenter Source:** *Verification of REQ-05 and REQ-06*

| Step | Transformation Technique | Visual Proof |
| :--- | :--- | :--- |
| **01** | **Canny Edge Detection** | <img width="250" alt="Linear_raw" src="https://github.com/user-attachments/assets/af4a2bd5-8ad7-487b-9ba3-5f565aa48243" /> |
| **02** | **Morphological Closing** | <img width="250" alt="Morphological" src="https://github.com/user-attachments/assets/b67d8cc1-bec5-45a4-9c8d-b3f0f0782e55" /> |

Prerequisites
Python Version: 3.10+


## 🖼️ Image Processing Lead

**📥 Ingestion (Scanning the /input Directory)**

The image processing pipeline begins by scanning the /input directory for newly added image files. Once a stable image file is detected, it is loaded into the system using OpenCV. At this stage, no image enhancement or transformation is applied, as the primary objective is only to acquire the raw image data for processing.
We used cv2.imread() to read the input image file and convert it into a matrix representation that can be processed by succeeding OpenCV functions.

**🎛️ Initial Transformation (Gaussian Blur and Grayscale Conversion)**

After ingestion, the image undergoes initial transformation to prepare it for edge detection.
To reduce noise and small texture details that may interfere with edge extraction, we used cv2.GaussianBlur() to smooth the image. This step minimizes high-frequency noise while preserving the overall structure of the subject.
After noise reduction, the smoothed image is converted into grayscale using cv2.cvtColor() with the cv2.COLOR_BGR2GRAY flag. This conversion reduces the image to a single intensity channel, which is required for reliable edge detection since edges are based on changes in pixel intensity rather than color.

## 🧠 Image Processing Logic

**✂️ Canny Edge Detection (Edge Identification)**

To identify edges and object boundaries in the image, we used cv2.Canny(). This function detects edges by analyzing intensity gradients and locating areas with significant brightness changes.
The Canny algorithm internally applies non-maximum suppression to thin the edges and uses a dual-threshold hysteresis process to classify strong and weak edges. Strong edges are retained, while weak edges are preserved only if they are connected to strong edges. This approach allows meaningful contours to be detected while suppressing isolated noise.

**🧩 Morphological Closing (Boundary Refinement)**

The edge map produced by the Canny detector may contain broken lines and small gaps. To refine these boundaries, we applied morphological closing.
We used cv2.getStructuringElement() to define the shape and size of the morphological kernel. Using this kernel, we applied dilation with cv2.dilate() to connect broken edge segments, followed by erosion with cv2.erode() to restore proper line thickness.
This sequence effectively performs morphological closing, which improves boundary continuity and produces smoother, more coherent outlines suitable for the final output.


## 🧩 Image Processing Logic (Jozza, done)
**👤 Ownership & Entry Point**

Lead Engineer: Jozza

Core Entry Point: src/main.py

📦 Filter Modules

- filter_01_bg_removal.py

- filter_02_gaussian_blur.py

- filter_03_grayscale.py

- filter_04_edge_detect.py

- filter_05_morphology.py

The image processing engine is implemented using OpenCV (cv2) with AI-assisted background segmentation.
The pipeline follows a deterministic, stage-based flow.

<br>
<br>

**📥 Ingestion**

src/main.py runs in an automated hot-folder mode that scans /input for valid image files.

Detects supported file types

Verifies file stability before processing

Loads images using cv2.imread()

Implementation: watch_and_process(), is_file_stable()

<br>
<br>

**🧍 Background Removal**

The subject is isolated using an AI-based background remover (U²-Net) to prevent unwanted background edges.

Outputs subject-on-white image and foreground mask

Mask is dilated using cv2.dilate() to preserve fine details

File: filter_01_bg_removal.py

<br>
<br>

**🎛️ Pre-Edge Conditioning**

Gaussian Blur: Noise reduction using cv2.GaussianBlur()

Grayscale: Intensity simplification using cv2.cvtColor(..., COLOR_BGR2GRAY)

Files:
filter_02_gaussian_blur.py, filter_03_grayscale.py

<br>
<br>

**✂️ Edge Detection**

Contours are extracted from the grayscale image, with background suppression using the foreground mask.

File: filter_04_edge_detect.py
Output: 04_lineart_raw.png

<br>
<br>

**🧩 Morphological Refinement**

Edges are cleaned and thickened for visual clarity.

Noise removal

Line reconnection and smoothing

OpenCV Ops: connectedComponentsWithStats(), dilate(), medianBlur()
File: filter_05_morphology.py
Final Output: 05_coloring_book.png

<br>
<br>

**💾 Export & Safety**

All outputs are saved using cv2.imwrite().
A fallback mechanism guarantees final output generation.

Implementation: process_one_image()
