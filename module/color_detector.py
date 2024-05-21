from PyQt5.QtCore import QThread, pyqtSignal
import cv2

from .color import COLORS, ColorUtils
from .cube import Cube

# 색상이 unknown인 경우에는 캡쳐가 되지 않도록 해야한다.

class ColorDetectorThread(QThread):
    color_detected = pyqtSignal(str, tuple)

    def __init__(self, cube):
        super().__init__()
        self.cube: Cube = cube
        self.cap = cv2.VideoCapture(0)
        print("WebCam is Opened:", self.cap.isOpened())

    def run(self):
        print("Thread is running")
        self.cube.draw()
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            # ROI
            height, width, _ = frame.shape
            roi_size = min(height, width) // 2
            roi_x = (width - roi_size) // 2
            roi_y = (height - roi_size) // 2
            roi = frame[roi_y:roi_y + roi_size, roi_x:roi_x + roi_size]
            self.hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            sub_roi_size = roi_size // 3
            self.face_info = ""
            for i in range(3):
                for j in range(3):
                    sub_x = j * sub_roi_size
                    sub_y = i * sub_roi_size
                    sub_roi = self.hsv[sub_y:sub_y + sub_roi_size, sub_x:sub_x + sub_roi_size]
                    hsv_pixel = sub_roi[sub_roi_size // 2, sub_roi_size // 2]
                    color_name = ColorUtils.get_color_name(hsv_pixel)
                    color = ColorUtils.get_bgr_color(color_name)
                    cv2.rectangle(roi, (sub_x, sub_y), (sub_x + sub_roi_size, sub_y + sub_roi_size), color, 2)
                    cv2.putText(roi, color_name, (sub_x + 10, sub_y + sub_roi_size // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    self.face_info += color_name

            frame[roi_y:roi_y + roi_size, roi_x:roi_x + roi_size] = roi

            cv2.circle(frame, (width // 2, height // 2), 10, (255, 255, 255), 2)
            cv2.imshow('Cube Color Detection', frame)
            cv2.waitKey(1)

        self.cap.release()
        cv2.destroyAllWindows()

    def save_color_info(self):
        if len(self.face_info) != 9:
            print("Face information is invalid length:", self.face_info)
            return
        
        center = self.face_info[4]
        captured_face = ColorUtils.color_string_to_face(self.face_info)

        print("captured face info:", self.face_info)
        print("captured face:", captured_face)
        print("center:", center)

        if "u" in self.face_info:
            print("Face information is invalid color:", self.face_info)
            return

        self.cube.updateFace(center, self.face_info)

    def standard_color_update(self, color_name, hsv):
        COLORS[color_name].update_hsv(hsv)
        print(f'{color_name} color updated to {hsv}')
        print(f"Current COLORS MAP : {str(COLORS)}")

    def get_captured_center_hsv(self):
        return self.hsv[self.hsv.shape[0] // 2, self.hsv.shape[1] // 2]

