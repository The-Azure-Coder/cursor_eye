import cv2
import mediapipe as mp
import numpy as np
import threading
import time
import base64
from models.eye_data import EyeData
from api.db_models import Config as ConfigOption
class EyeTrackingService:
    def __init__(self):
        self.eye_data = EyeData()
        self.data_lock = threading.Lock()
        self.tracking_active = False
        self.cam = None
        self.face_mesh = None
        self.smoothed_x = 0.5
        self.smoothed_y = 0.5
        self._initialize_camera()
    
    def _initialize_camera(self):
        try:
            self.cam = cv2.VideoCapture(0) # open cammera if successful
            if not self.cam.isOpened():
                print("Error: Could not start webcam")
                return
            
            # Possible personalizatiion for users: 
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cam.set(cv2.CAP_PROP_FPS, 30)
            
            self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                refine_landmarks=True,
                max_num_faces=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            )
            print("Camera initialized successfully")
        except Exception as e:
            print(f"Camera initilization fail {e}")
            self.cam = None

    def setCameraDataFromConfig(self, configOption: ConfigOption):
        try:
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, configOption.videoWidth),
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, configOption.videoHeight)
            self.cam.set(cv2.CAP_PROP_FPS, configOption.fps)
        except Exception as e:
            print(f"")
            self.cam = None

    def start_tracking(self, socketio_instance):
        """Start eye tracking with WebSocket emission"""
        if not self.cam or not self.cam.isOpened():
            print("Webcam unavailable")
            return False
            
        self.tracking_active = True
        print("Begin eye tracking...")
        
        # Start tracking in a separate thread with socketio instance
        tracking_thread = threading.Thread(
            target=self._tracking_loop, 
            args=(socketio_instance,), 
            daemon=True
        )
        tracking_thread.start()
        return True
    
    def _tracking_loop(self, socketio_instance):
        """Main tracking loop"""
        frame_count = 0
        last_log_time = time.time()
        
        while self.tracking_active and self.cam and self.cam.isOpened():
            success, frame = self.cam.read()
            if not success:
                time.sleep(0.1)
                continue
                
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            output = self.face_mesh.process(rgb_frame)
            landmark_points = output.multi_face_landmarks
            
            frame_h, frame_w, _ = frame.shape
            
            # Reset click events
            with self.data_lock:
                self.eye_data.reset_clicks()
            
            if landmark_points:
                landmarks = landmark_points[0].landmark
                self._update_eye_position(landmarks)
                self._detect_blinks(landmarks)
                self._draw_overlay(frame, landmarks, frame_w, frame_h)
            
            # Add UI elements
            cv2.putText(frame, "Eye Controlled Mouse", (10, frame_h - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            with self.data_lock:
                cv2.putText(frame, f"X: {self.eye_data.eye_x:.3f}", (frame_w - 150, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.putText(frame, f"Y: {self.eye_data.eye_y:.3f}", (frame_w - 150, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Encode frame to JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            frame_data = base64.b64encode(buffer).decode('utf-8')
            
            # Send data via WebSocket
            with self.data_lock:
                socketio_instance.emit('eye_data', {
                    'eye_x': self.eye_data.eye_x,
                    'eye_y': self.eye_data.eye_y,
                    'left_click': self.eye_data.left_click,
                    'right_click': self.eye_data.right_click,
                    'blink_detected': self.eye_data.blink_detected,
                    'video_frame': frame_data
                })
            
            # Log FPS
            frame_count += 1
            current_time = time.time()
            if current_time - last_log_time > 5:
                fps = frame_count / (current_time - last_log_time)
                print(f"Frame Tracking: {fps:.1f}")
                frame_count = 0
                last_log_time = current_time
            
            time.sleep(0.033)
    
    def _update_eye_position(self, landmarks):
        """Update eye position from landmarks"""

         #calculate for better right eye posistioning
        right_eye_landmark_array = [468, 469, 470, 471, 472]
        right_eye_points = [landmarks[i] for i in right_eye_landmark_array]
        right_eye_x = np.mean([p.x for p in right_eye_points])
        right_eye_y = np.mean([p.y for p in right_eye_points])
        
        #calculate for better left eye posistioning
        left_eye_landmark_array = [473, 474, 475, 476, 477]
        left_eye_points = [landmarks[i] for i in left_eye_landmark_array]
        left_eye_x = np.mean([p.x for p in left_eye_points])
        left_eye_y = np.mean([p.y for p in left_eye_points])
        
        raw_x = (right_eye_x + left_eye_x) / 2
        raw_y = (right_eye_y + left_eye_y) / 2
        
        # Apply smoothing for smother movement
        self.smoothed_x = self.smoothed_x * 0.8 + raw_x * 0.2
        self.smoothed_y = self.smoothed_y * 0.8 + raw_y * 0.2
        
        # Apply mapping for screen coordinates
        mapped_x = np.clip(self.smoothed_x, 0.1, 0.9)
        mapped_y = np.clip(self.smoothed_y, 0.1, 0.9)
        
        screen_x = (mapped_x - 0.1) / 0.8
        screen_y = (mapped_y - 0.1) / 0.8
        
        with self.data_lock:
            self.eye_data.eye_x = float(np.clip(screen_x, 0.0, 1.0))
            self.eye_data.eye_y = float(np.clip(screen_y, 0.0, 1.0))
    
    def _detect_blinks(self, landmarks):
        """Detect eye blinks"""
        left_eye_vertical = abs(landmarks[159].y - landmarks[145].y)
        right_eye_vertical = abs(landmarks[386].y - landmarks[374].y)
        
        blink_threshold = 0.015
        
        with self.data_lock:
            if left_eye_vertical < blink_threshold and right_eye_vertical >= blink_threshold:
                self.eye_data.left_click = True
                self.eye_data.blink_detected = True
            elif right_eye_vertical < blink_threshold and left_eye_vertical >= blink_threshold:
                self.eye_data.right_click = True
                self.eye_data.blink_detected = True
    

    def _draw_overlay(self, frame, landmarks, frame_w, frame_h):
        """Draw overlay on frame"""
        # Draw eye landmarks
        combined_landmark_array = [468, 469, 470, 471, 472, 473, 474, 475, 476, 477]
        for landmark in combined_landmark_array:
            x = int(landmarks[landmark].x * frame_w)
            y = int(landmarks[landmark].y * frame_h)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
        
        # Draw crosshair
        with self.data_lock:
            cross_x = int(self.eye_data.eye_x * frame_w)
            cross_y = int(self.eye_data.eye_y * frame_h)
        
        cv2.line(frame, (cross_x-15, cross_y), (cross_x+15, cross_y), (0, 0, 255), 2)
        cv2.line(frame, (cross_x, cross_y-15), (cross_x, cross_y+15), (0, 0, 255), 2)
        
        # Add click indicators
        with self.data_lock:
            if self.eye_data.left_click:
                cv2.putText(frame, "LEFT CLICK", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            elif self.eye_data.right_click:
                cv2.putText(frame, "RIGHT CLICK", (50, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    
    def stop_tracking(self):
        """Stop the eye tracking"""
        self.tracking_active = False
        if self.cam and self.cam.isOpened():
            self.cam.release()
        cv2.destroyAllWindows()
        print("Eye tracking stopped")
    
    def get_eye_data(self):
        """Get current eye data"""
        with self.data_lock:
            return self.eye_data.to_dict()
    
    def is_camera_available(self):
        """Check if camera is available"""
        return self.cam is not None and self.cam.isOpened()
    

ets = EyeTrackingService()