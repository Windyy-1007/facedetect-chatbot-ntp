#!/usr/bin/env python3
"""
Simple camera test to verify camera availability
"""
import cv2

def test_camera():
    """Test if camera is available"""
    print("Testing camera access...")
    
    # Try to open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Camera not accessible")
        print("Possible solutions:")
        print("1. Check if camera is connected")
        print("2. Close other applications using the camera")
        print("3. Try a different camera index (1, 2, etc.)")
        return False
    
    print("✅ Camera is accessible")
    
    # Try to read a frame
    ret, frame = cap.read()
    if ret:
        print(f"✅ Frame captured successfully: {frame.shape}")
    else:
        print("❌ Failed to capture frame")
        cap.release()
        return False
    
    cap.release()
    print("✅ Camera test completed successfully")
    return True

if __name__ == "__main__":
    test_camera()