class EyeData:
    def __init__(self):
        self.eye_x = 0.5
        self.eye_y = 0.5
        self.left_click = False
        self.right_click = False
        self.blink_detected = False
        self.scroll_up = False
        self.scroll_down = False
        self.drag_active = False
        self.drag_start = False
        self.drag_end = False
        self.left_eye_closed = False
        self.right_eye_closed = False

    def to_dict(self):
        return {
            'eye_x': self.eye_x,
            'eye_y': self.eye_y,
            'left_click': self.left_click,
            'right_click': self.right_click,
            'blink_detected': self.blink_detected,
            'scroll_up': self.scroll_up,
            'scroll_down': self.scroll_down,
            'drag_active': self.drag_active,
            'drag_start': self.drag_start,
            'drag_end': self.drag_end,
            'left_eye_closed': self.left_eye_closed,
            'right_eye_closed': self.right_eye_closed
        }
    def reset_clicks(self):
        self.left_click = False
        self.right_click = False
        self.blink_detected = False
        self.scroll_up = False
        self.scroll_down = False
        self.drag_start = False
        self.drag_end = False
        self.left_eye_closed = False
        self.right_eye_closed = False

