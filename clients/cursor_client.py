import socketio
import pyautogui
import time
import sys
import threading
import keyboard

sio = socketio.Client(logger=False, engineio_logger=False)

class EyeControlClient:
    def __init__(self, server_url="http://localhost:5000"):
        self.server_url = server_url
        self.running = False
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Enhanced smoothing parameters
        self.smoothing_factor = 0.85
        self.last_x, self.last_y = self.screen_w // 2, self.screen_h // 2
        self.velocity_x, self.velocity_y = 0, 0

        # Action cooldowns
        self.last_click_time = 0
        self.last_scroll_time = 0
        self.click_cooldown = 0.6
        self.scroll_cooldown = 0.3  
        
        # Drag state
        self.drag_active = False
        
        # Failsafe parameters
        self.emergency_stop = False
        self.movement_threshold = 1500
        self.last_positions = []
        self.max_positions = 10
        
        print(f"Screen size: {self.screen_w}x{self.screen_h}")
        
    def setup_handlers(self):
        """Setup SocketIO event handlers"""
        
        @sio.event
        def connect():
            print("Successfully connected to WebSocket server")
            self.running = True
            
        @sio.event
        def connect_error(data):
            print("Connection failed:", data)
            
        @sio.event
        def disconnect():
            print("Disconnected from WebSocket server")
            self.running = False
            
        @sio.event
        def eye_data(data):
            if not self.emergency_stop:
                self.process_eye_data(data)
            
        @sio.event
        def connected(data):
            print(f"Server: {data['message']}")

    def setup_emergency_hotkeys(self):
        """Emergency keyboard escapes and restart"""
        def emergency_stop():
            if not self.emergency_stop:
                self.emergency_stop = True
                # Release mouse if dragging
                if self.drag_active:
                    pyautogui.mouseUp()
                    self.drag_active = False
                print("EMERGENCY STOP ACTIVATED - Press 'r' to resume")
                pyautogui.moveTo(50, 50)
                
        def resume_control():
            if self.emergency_stop:
                self.emergency_stop = False
                print("resume control")
                
        keyboard.add_hotkey('ctrl+alt+s', emergency_stop)
        keyboard.add_hotkey('ctrl+alt+r', resume_control)
        keyboard.add_hotkey('esc', emergency_stop)

    def check_mouse_velocity(self, x, y):
        """Check if mouse is moving too fast"""
        current_time = time.time()
        self.last_positions.append((x, y, current_time))
        
        if len(self.last_positions) > self.max_positions:
            self.last_positions.pop(0)
            
        if len(self.last_positions) >= 2:
            first_x, first_y, first_time = self.last_positions[0]
            last_x, last_y, last_time = self.last_positions[-1]
            
            distance = ((last_x - first_x)**2 + (last_y - first_y)**2)**0.5
            time_diff = last_time - first_time
            
            if time_diff > 0:
                velocity = distance / time_diff
                if velocity > self.movement_threshold:
                    print(f"High velocity detected: {velocity:.0f} px/s - Emergency stop!")
                    self.emergency_stop = True
                    # Release mouse if dragging
                    if self.drag_active:
                        pyautogui.mouseUp()
                        self.drag_active = False
                    pyautogui.moveTo(self.screen_w // 2, self.screen_h // 2)
                    return True
        return False

    def process_eye_data(self, data):
        """Process eye data and control cursor with new drag/scroll behaviors"""
        try:
            # Get normalized coordinates
            eye_x = data.get('eye_x', 0.5)
            eye_y = data.get('eye_y', 0.5)
            
            # Convert to screen coordinates
            target_x = self.non_linear_map(eye_x) * self.screen_w
            target_y = self.non_linear_map(eye_y) * self.screen_h
            
            # Check for erratic movement
            if self.check_mouse_velocity(target_x, target_y):
                return
                
            # Apply smoothing
            smooth_x, smooth_y = self.advanced_smoothing(target_x, target_y)
            
            # Move cursor (handle drag differently)
            if self.drag_active:
                # During drag, we still move but don't update last position for smoothing
                pyautogui.dragTo(smooth_x, smooth_y, duration=0.1, button='left')
            else:
                pyautogui.moveTo(smooth_x, smooth_y, _pause=False)
                self.last_x, self.last_y = smooth_x, smooth_y
            
            current_time = time.time()
            
            # Handle drag actions
            if data.get('drag_start') and not self.drag_active:
                # Start drag
                self.drag_active = True
                pyautogui.mouseDown()
                print("Drag started - move cursor to drag items")
            
            elif data.get('drag_end') and self.drag_active:
                # End drag
                self.drag_active = False
                pyautogui.mouseUp()
                print("Drag ended - item dropped")
            
            # Handle scroll actions (continuous while in scroll zones)
            if current_time - self.last_scroll_time > self.scroll_cooldown:
                if data.get('scroll_up'):
                    pyautogui.scroll(5)  # Scroll up
                    print("Scrolling up...")
                    self.last_scroll_time = current_time
                elif data.get('scroll_down'):
                    pyautogui.scroll(-5)  # Scroll down
                    print("Scrolling down...")
                    self.last_scroll_time = current_time
            
            # Handle click actions (only if not dragging)
            if not self.drag_active and current_time - self.last_click_time > self.click_cooldown:
                if data.get('left_click'):
                    pyautogui.click()
                    print("Left click")
                    self.last_click_time = current_time
                elif data.get('right_click'):
                    pyautogui.rightClick()
                    print("Right click")
                    self.last_click_time = current_time
                    
        except Exception as e:
            print(f"Processing error: {e}")
            # Ensure mouse is released on error
            if self.drag_active:
                pyautogui.mouseUp()
                self.drag_active = False
    
    def non_linear_map(self, value):
        return value ** 1.5
    
    def advanced_smoothing(self, target_x, target_y):
        # Calculate velocity
        vel_x = target_x - self.last_x
        vel_y = target_y - self.last_y
        
        # Apply damping to velocity
        self.velocity_x = self.velocity_x * 0.7 + vel_x * 0.3
        self.velocity_y = self.velocity_y * 0.7 + vel_y * 0.3
        
        # Apply smoothing with velocity prediction
        smooth_x = (self.last_x * self.smoothing_factor + 
                   target_x * (1 - self.smoothing_factor) + 
                   self.velocity_x * 0.1)
        smooth_y = (self.last_y * self.smoothing_factor + 
                   target_y * (1 - self.smoothing_factor) + 
                   self.velocity_y * 0.1)
        
        # Clamp to screen boundaries
        smooth_x = max(0, min(self.screen_w - 1, smooth_x))
        smooth_y = max(0, min(self.screen_h - 1, smooth_y))
        
        return smooth_x, smooth_y
    
    def run(self):
        """Main execute method"""
        print("Starting Enhanced Eye Control Client...")
        print("CONTROLS:")
        print("Move eyes to control cursor")
        print("Quick wink LEFT eye = Left click")
        print("Quick wink RIGHT eye = Right click")
        print("HOLD LEFT eye closed (1 second) = Start drag")
        print("OPEN LEFT eye = End drag")
        print("Move cursor to TOP of screen = Scroll up")
        print("Move cursor to BOTTOM of screen = Scroll down")
        print("Emergency stops:")
        print("Press ESC to emergency stop")
        print("Press Ctrl+Alt+S to emergency stop") 
        print("Press Ctrl+Alt+R to resume")
        print("=" * 50)
        
        # Setup emergency hotkeys
        try:
            self.setup_emergency_hotkeys()
            print("Emergency escape keys registered")
        except Exception as e:
            print(f" Could not setup esacpe keys: {e}")
        
        # Setup event handlers
        self.setup_handlers()
        
        # Retry connection
        max_retries = 10
        retry_delay = 3
        
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1}/{max_retries}: Connecting to {self.server_url}...")
                sio.connect(self.server_url, wait_timeout=10)
                print("Successfully connected to WebSocket server!")
                
                # Keep the client running
                while self.running:
                    if self.emergency_stop:
                        print("SYSTEM PAUSED - Press Ctrl+Alt+R to resume", end='\r')
                    time.sleep(0.1)
                
                break
                    
            except socketio.exceptions.ConnectionError as e:
                print(f"Connection failed (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Make sure the Flask server is running: python app.py")
            except KeyboardInterrupt:
                print("\nStopping eye control client")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                break
            finally:
                if self.drag_active:
                    pyautogui.mouseUp()
                    self.drag_active = False
                if sio.connected:
                    sio.disconnect()
                self.running = False

if __name__ == "__main__":
    client = EyeControlClient()
    client.run()