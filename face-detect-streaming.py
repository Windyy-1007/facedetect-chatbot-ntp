from deepface import DeepFace
import cv2
import time
import numpy as np
import os
from datetime import datetime

# Camera configuration
CAMERA_SOURCE = 0  # Change this to your camera source if needed

# Face detection parameters
OPTIMAL_FACE_WIDTH = 150  # Optimal face width in pixels (approximately 50cm from camera)
TOO_CLOSE_THRESHOLD = 200  # Face width threshold for "too close"
TOO_FAR_THRESHOLD = 100   # Face width threshold for "too far"

# Position detection parameters
FRAME_CENTER_THRESHOLD = 50  # Pixels from center to trigger position adjustment

class FaceGuidanceApp:
    def __init__(self):
        self.cap = cv2.VideoCapture(CAMERA_SOURCE)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        if not self.cap.isOpened():
            raise ValueError("Could not open camera")
            
        print("Face Guidance App Started")
        print("Controls:")
        print("- W: Move closer (face too far)")
        print("- S: Move away (face too close)")
        print("- A: Move right (face too left)")
        print("- D: Move left (face too right)")
        print("- Press 'q' to quit")
        
    def detect_faces(self, frame):
        """Detect faces using OpenCV (simplified from DeepFace)"""
        try:
            # Use OpenCV Haar cascades for reliable face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            face_rects = face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            return face_rects
        except Exception as e:
            print(f"Face detection error: {e}")
            return []
    
    def analyze_face_distance(self, face_width):
        """Analyze if face is too close or too far based on width"""
        if face_width > TOO_CLOSE_THRESHOLD:
            print("S")  # Move away (face too close)
            return "TOO_CLOSE"
        elif face_width < TOO_FAR_THRESHOLD:
            print("W")  # Move closer (face too far)
            return "TOO_FAR"
        else:
            return "OPTIMAL"
    
    def analyze_face_position(self, face_center_x, frame_width):
        """Analyze if face is off-center horizontally"""
        frame_center_x = frame_width // 2
        
        if face_center_x < frame_center_x - FRAME_CENTER_THRESHOLD:
            print("D")  # Move left (face too left, so person should move right)
            return "TOO_LEFT"
        elif face_center_x > frame_center_x + FRAME_CENTER_THRESHOLD:
            print("A")  # Move right (face too right, so person should move left)
            return "TOO_RIGHT"
        else:
            return "CENTERED"
    
    def draw_guidance(self, frame, face_rects):
        """Draw guidance information on frame"""
        height, width = frame.shape[:2]
        
        # Draw center guide line
        cv2.line(frame, (width//2, 0), (width//2, height), (0, 255, 0), 1)
        
        # Draw optimal face size guide (circle in center)
        center_x, center_y = width//2, height//2
        optimal_radius = OPTIMAL_FACE_WIDTH // 2
        cv2.circle(frame, (center_x, center_y), optimal_radius, (0, 255, 255), 2)
        
        # Process each detected face
        for (x, y, w, h) in face_rects:
            # Draw face rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            # Calculate face center
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            
            # Draw face center point
            cv2.circle(frame, (face_center_x, face_center_y), 5, (255, 0, 0), -1)
            
            # Analyze distance and position
            distance_status = self.analyze_face_distance(w)
            position_status = self.analyze_face_position(face_center_x, width)
            
            # Display status text
            status_text = f"Distance: {distance_status}, Position: {position_status}"
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Display face width
            cv2.putText(frame, f"Face Width: {w}px", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Display instructions
        instructions = [
            "Instructions:",
            "W - Move closer | S - Move away",
            "A - Move right | D - Move left",
            "Press 'q' to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            y_pos = height - 80 + (i * 20)
            cv2.putText(frame, instruction, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        return frame
    
    def run(self):
        """Main application loop"""
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect faces
                face_rects = self.detect_faces(frame)
                
                # If faces detected, provide guidance
                if len(face_rects) > 0:
                    frame = self.draw_guidance(frame, face_rects)
                else:
                    # No face detected
                    cv2.putText(frame, "No face detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Display frame
                cv2.imshow('Face Guidance System', frame)
                
                # Check for quit
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cap.release()
            cv2.destroyAllWindows()

def main():
    """Main function"""
    try:
        app = FaceGuidanceApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure your camera is connected and not in use by another application")

if __name__ == "__main__":
    main()
