"""
Face Guidance System with MQTT Control
Combines face detection with MQTT robot control
"""
import cv2
import time
import paho.mqtt.client as mqtt

# Camera configuration
CAMERA_SOURCE = 0  # Change this to your camera source if needed

# Face detection parameters
OPTIMAL_FACE_WIDTH = 150  # Optimal face width in pixels (approximately 50cm from camera)
TOO_CLOSE_THRESHOLD = 200  # Face width threshold for "too close"
TOO_FAR_THRESHOLD = 100   # Face width threshold for "too far"

# Position detection parameters
FRAME_CENTER_THRESHOLD = 50  # Pixels from center to trigger position adjustment

# MQTT settings
BROKER_ADDRESS = "192.168.4.1"  # địa chỉ broker
MQTT_PORT = 1883
TOPIC = "VR_control"

# Control rate limiting
COMMAND_RATE_LIMIT = 0.5  # Minimum seconds between commands (2 commands per second)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker:", BROKER_ADDRESS)
        client.subscribe(TOPIC)
    else:
        print(f"❌ Failed to connect to MQTT, return code {rc}")


def on_message(client, userdata, msg):
    print(f"📩 Received: '{msg.payload.decode()}' on topic '{msg.topic}'")


def on_subscribe(mosq, obj, mid, granted_qos):
    print(f"🔔 Subscribed to MQTT topic (mid={mid})")


def on_publish(mosq, obj, mid):
    print(f"📤 MQTT Message {mid} sent to broker")


class FaceGuidanceMQTTApp:
    def __init__(self):
        # Initialize camera
        self.cap = cv2.VideoCapture(CAMERA_SOURCE)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Initialize face detector
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        if not self.cap.isOpened():
            raise ValueError("Could not open camera")
        
        # Initialize MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_message = on_message
        self.mqtt_client.on_subscribe = on_subscribe
        self.mqtt_client.on_publish = on_publish
        
        try:
            self.mqtt_client.connect(BROKER_ADDRESS, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
            print("✅ MQTT client started")
        except Exception as e:
            print(f"⚠️  Warning: Could not connect to MQTT broker: {e}")
            print("Continuing in face detection only mode...")
        
        # Command rate limiting
        self.last_command_time = 0
        self.last_command = None
        
        print("\n" + "="*60)
        print("Face Guidance System with MQTT Control Started")
        print("="*60)
        print("Controls:")
        print("- W: Move Forward (when face too far)")
        print("- S: Move Backward (when face too close)")
        print("- A: Move Left (when face too right)")
        print("- D: Move Right (when face too left)")
        print("- Q: Rotate Left (5 degrees)")
        print("- E: Rotate Right (5 degrees)")
        print("- SPACE: Stop")
        print("- ESC or 'q': Quit")
        print("="*60 + "\n")
        
    def send_mqtt_command(self, command):
        """Send command via MQTT with rate limiting"""
        current_time = time.time()
        
        # Check if enough time has passed since last command
        if current_time - self.last_command_time < COMMAND_RATE_LIMIT:
            return False
        
        # Don't send the same command repeatedly
        if command == self.last_command:
            return False
        
        try:
            self.mqtt_client.publish(TOPIC, command)
            print(f"➡️  MQTT: {command}")
            self.last_command_time = current_time
            self.last_command = command
            return True
        except Exception as e:
            print(f"⚠️  MQTT send error: {e}")
            return False
    
    def detect_faces(self, frame):
        """Detect faces using OpenCV Haar cascades"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return faces
    
    def analyze_face_distance(self, face_width):
        """Analyze if face is too close or too far based on width"""
        if face_width > TOO_CLOSE_THRESHOLD:
            self.send_mqtt_command("Backward")  # Move away (face too close)
            return "TOO_CLOSE"
        elif face_width < TOO_FAR_THRESHOLD:
            self.send_mqtt_command("Forward")  # Move closer (face too far)
            return "TOO_FAR"
        else:
            return "OPTIMAL"
    
    def analyze_face_position(self, face_center_x, frame_width):
        """Analyze if face is off-center horizontally"""
        frame_center_x = frame_width // 2
        
        if face_center_x < frame_center_x - FRAME_CENTER_THRESHOLD:
            self.send_mqtt_command("Right")  # Move right (face too left)
            return "TOO_LEFT"
        elif face_center_x > frame_center_x + FRAME_CENTER_THRESHOLD:
            self.send_mqtt_command("Left")  # Move left (face too right)
            return "TOO_RIGHT"
        else:
            return "CENTERED"
    
    def draw_guidance(self, frame, faces):
        """Draw guidance information on frame"""
        height, width = frame.shape[:2]
        
        # Draw center guide line
        cv2.line(frame, (width//2, 0), (width//2, height), (0, 255, 0), 1)
        
        # Draw optimal face size guide (circle in center)
        center_x, center_y = width//2, height//2
        optimal_radius = OPTIMAL_FACE_WIDTH // 2
        cv2.circle(frame, (center_x, center_y), optimal_radius, (0, 255, 255), 2)
        
        # Process each detected face
        for (x, y, w, h) in faces:
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
        
        # Display last command sent
        if self.last_command:
            cmd_text = f"Last Command: {self.last_command}"
            cv2.putText(frame, cmd_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Display instructions
        instructions = [
            "Manual Controls:",
            "W-Forward | S-Backward | A-Left | D-Right",
            "Q-Rotate Left | E-Rotate Right | SPACE-Stop",
            "ESC or 'q' to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            y_pos = height - 80 + (i * 20)
            cv2.putText(frame, instruction, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
        
        return frame
    
    def handle_manual_control(self, key):
        """Handle manual keyboard controls"""
        cmd = None
        
        if key == ord('w'):
            cmd = "Forward"
        elif key == ord('s'):
            cmd = "Backward"
        elif key == ord('a'):
            cmd = "Left"
        elif key == ord('d'):
            cmd = "Right"
        elif key == ord('q'):
            cmd = "RotateLeft"
        elif key == ord('e'):
            cmd = "RotateRight"
        elif key == ord(' '):
            cmd = "Stop"
        
        if cmd:
            # For manual controls, bypass rate limiting
            current_time = time.time()
            if current_time - self.last_command_time >= COMMAND_RATE_LIMIT:
                try:
                    self.mqtt_client.publish(TOPIC, cmd)
                    print(f"🎮 Manual: {cmd}")
                    self.last_command_time = current_time
                    self.last_command = cmd
                except Exception as e:
                    print(f"⚠️  MQTT send error: {e}")
    
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
                faces = self.detect_faces(frame)
                
                # If faces detected, provide guidance
                if len(faces) > 0:
                    frame = self.draw_guidance(frame, faces)
                else:
                    # No face detected
                    cv2.putText(frame, "No face detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    # Show manual controls even when no face detected
                    height, width = frame.shape[:2]
                    instructions = [
                        "Manual Controls:",
                        "W-Forward | S-Backward | A-Left | D-Right",
                        "Q-Rotate Left | E-Rotate Right | SPACE-Stop",
                        "ESC or 'q' to quit"
                    ]
                    for i, instruction in enumerate(instructions):
                        y_pos = height - 80 + (i * 20)
                        cv2.putText(frame, instruction, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
                
                # Display frame
                cv2.imshow('Face Guidance System with MQTT', frame)
                
                # Check for keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                # Handle manual controls
                self.handle_manual_control(key)
                
                # Check for quit
                if key == ord('q') or key == 27:  # 'q' or ESC
                    break
                    
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        self.cap.release()
        cv2.destroyAllWindows()
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        print("✅ Cleanup complete")


def main():
    """Main function"""
    try:
        app = FaceGuidanceMQTTApp()
        app.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your camera is connected and not in use by another application")


if __name__ == "__main__":
    main()
