# Face Recognition Guidance App

A real-time face detection application that provides guidance for optimal camera positioning using computer vision.

## Features

- **Face Detection**: Real-time face detection using OpenCV
- **Distance Guidance**: 
  - Prints `W` when face is too far (move closer)
  - Prints `S` when face is too close (move away)
- **Position Guidance**:
  - Prints `A` when face is too far left (move right)  
  - Prints `D` when face is too far right (move left)
- **Visual Feedback**: Shows face boundaries, center guides, and optimal positioning circle

## Requirements

- Python 3.7+
- OpenCV
- Camera/Webcam

## Installation

1. **Create and activate virtual environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**
   ```powershell
   pip install opencv-python
   ```

## Usage

### Quick Test
Test your camera first:
```powershell
.\.venv\Scripts\python.exe test_camera.py
```

### Run the Application

**Simple Version (Recommended):**
```powershell
.\.venv\Scripts\python.exe simple_face_guidance.py
```

**Advanced Version (with DeepFace):**
```powershell
# Install additional dependencies first
pip install deepface tf-keras tensorflow

# Then run
.\.venv\Scripts\python.exe face-detect-streaming.py
```

## How It Works

### Distance Detection
- **Optimal Distance**: Face width ~150 pixels (approximately 50cm from camera)
- **Too Close**: Face width > 200 pixels → Prints `S`
- **Too Far**: Face width < 100 pixels → Prints `W`

### Position Detection  
- **Center Threshold**: 50 pixels from frame center
- **Too Left**: Face center < (frame_center - 50) → Prints `D`
- **Too Right**: Face center > (frame_center + 50) → Prints `A`

### Visual Guide
- **Green Line**: Center of frame
- **Yellow Circle**: Optimal face size zone
- **Blue Rectangle**: Detected face boundary
- **Blue Dot**: Face center point

## Controls

- **W**: Move closer to camera (face too far)
- **S**: Move away from camera (face too close) 
- **A**: Move right (face too far left)
- **D**: Move left (face too far right)
- **Q**: Quit application

## Files

- `simple_face_guidance.py` - Basic OpenCV implementation (recommended)
- `face-detect-streaming.py` - Advanced DeepFace implementation  
- `test_camera.py` - Camera connectivity test
- `face-detect-img.py` - Static image processing (empty template)

## Troubleshooting

### Camera Issues
- Ensure camera is connected and not used by other applications
- Try different camera indices (0, 1, 2, etc.) in the CAMERA_SOURCE variable
- Run `test_camera.py` to verify camera accessibility

### Performance Issues
- Use `simple_face_guidance.py` for better performance
- Reduce frame resolution if needed
- Close unnecessary applications

### DeepFace Issues
If using the advanced version:
```powershell
pip install deepface tf-keras tensorflow pillow
```

## Configuration

Edit these constants in the Python files to customize behavior:

```python
CAMERA_SOURCE = 0              # Camera index
OPTIMAL_FACE_WIDTH = 150       # Target face width in pixels  
TOO_CLOSE_THRESHOLD = 200      # Face width for "too close"
TOO_FAR_THRESHOLD = 100        # Face width for "too far"
FRAME_CENTER_THRESHOLD = 50    # Position tolerance in pixels
```

## Examples

**Console Output:**
```
Face Guidance App Started
Controls:
- W: Move closer (face too far)
- S: Move away (face too close)  
- A: Move right (face too left)
- D: Move left (face too right)
- Press 'q' to quit
W
W  
S
A
D
```

The letters correspond to movement directions for optimal face positioning.