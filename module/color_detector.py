from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
import cv2

from .color import COLORS, ColorUtils
from .cube import Cube

# 색상이 unknown인 경우에는 캡쳐가 되지 않도록 해야한다.

class ColorDetectorThread(QThread):
    color_detected = pyqtSignal(str, tuple)
    frame_ready = pyqtSignal(QImage)

    def __init__(self, cube):
        super().__init__()
        self.capture_help_mode = False
        self.capture_order_list = []
        self.cube: Cube = cube
        self.cap = cv2.VideoCapture(0)
        self.hsv = None
        self.frame = None
        print("WebCam is Opened:", self.cap.isOpened())

    def start_capture_help_mode(self):
        self.capture_help_mode = True
        self.capture_order_list = ["F", "R", "B", "L", "U", "D"]
        self.capture_order_list.reverse()

        # 맨 처음에는 F면을 캡처하도록 현재 화면에 위쪽(노란색) 앞면(초록색) 아래(흰색)을 위치하도록 현재 프레임에 화살표를 그린다.
        self.draw_help_arrow("F", self.frame)

    def draw_help_arrow(self, current_center, frame):
        cv2.putText(frame, f"Capture Helper Mode Activate Current Capture Color : {ColorUtils.get_long_color_name(ColorUtils.face_to_color(current_center))}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        if current_center == "F":
            # U (Yellow)라는 글자가 roi의 위쪽에 위치하도록 한다.
            cv2.putText(frame, "U (Yellow)", (frame.shape[1] // 2 - 10, frame.shape[0] // 2 - 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            # F (Green)라는 글자가 roi의 중앙에 위치하도록 한다.
            cv2.putText(frame, "F (Green)", (frame.shape[1] // 2 - 10, frame.shape[0] // 2 + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            # D (White)라는 글자가 roi의 아래쪽에 위치하도록 한다.
            cv2.putText(frame, "D (Down)", (frame.shape[1] // 2 - 10, frame.shape[0] // 2 + 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        elif current_center == "R":
            # R이 정면에 위치하도록 화살표를 그린다. 좌에서 우로 가는 화살표를 그려야함
            cv2.arrowedLine(frame, (frame.shape[1] // 2 + 50, frame.shape[0] // 2), (frame.shape[1] // 2 - 50, frame.shape[0] // 2), (0, 0, 0), 2)
        elif current_center == "B":
            # B가 정면에 위치하도록 화살표를 그린다. R의 경우와 같은 방향으로 화살표를 그려야함
            cv2.arrowedLine(frame, (frame.shape[1] // 2 + 50, frame.shape[0] // 2), (frame.shape[1] // 2 - 50, frame.shape[0] // 2), (0, 0, 0), 2)
        elif current_center == "L":
            cv2.arrowedLine(frame, (frame.shape[1] // 2 + 50, frame.shape[0] // 2), (frame.shape[1] // 2 - 50, frame.shape[0] // 2), (0, 0, 0), 2)
        elif current_center == "U":
            # U가 정면에 위치하도록 화살표를 그린다. 왼쪽에서 오른쪽으로 가다가 중간에 위로 꺾는 화살표를 그려야함 총 2개를 그려야겠지.
            cv2.arrowedLine(frame, (frame.shape[1] // 2 - 50, frame.shape[0] // 2), (frame.shape[1] // 2 - 50, frame.shape[0] // 2 + 50), (0, 0, 0), 2)
            cv2.arrowedLine(frame, (frame.shape[1] // 2 + 50, frame.shape[0] // 2), (frame.shape[1] // 2 - 50, frame.shape[0] // 2), (0, 0, 0), 2)
        elif current_center == "D":
            # D가 정면에 위치하도록 화살표를 그린다. U의 경우와 같은 방향으로 화살표를 그려야함
            cv2.arrowedLine(frame, (frame.shape[1] // 2, frame.shape[0] // 2 + 50), (frame.shape[1] // 2, frame.shape[0] // 2 - 50), (0, 0, 0), 2)


    def run(self):
        print("Thread is running")
        while self.cap.isOpened():
            ret, self.frame = self.cap.read()
            if not ret:
                break
            # ROI 설정
            height, width, _ = self.frame.shape
            roi_size = min(height, width) // 2
            roi_x = (width - roi_size) // 2
            roi_y = (height - roi_size) // 2
            roi = self.frame[roi_y:roi_y + roi_size, roi_x:roi_x + roi_size]
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
                    
                    # 작은 ROI 그리기
                    cv2.rectangle(roi, (sub_x, sub_y), (sub_x + sub_roi_size, sub_y + sub_roi_size), color, 2)
                    
                    # 작은 ROI 내부의 중앙에 색상을 검출하는 지점 가시화
                    cv2.circle(roi, (sub_x + sub_roi_size // 2, sub_y + sub_roi_size // 2), 2, (0, 0, 0), -1)
                    
                    # 작은 ROI의 중앙 상단에 글씨 표시
                    cv2.putText(roi, color_name, (sub_x + sub_roi_size // 2 - 8, sub_y + sub_roi_size // 2 - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
                    
                    self.face_info += color_name

            self.frame[roi_y:roi_y + roi_size, roi_x:roi_x + roi_size] = roi

            cv2.circle(self.frame, (width // 2, height // 2), 10, (255, 255, 255), 1)

            if self.capture_help_mode:
                self.draw_help_arrow(self.capture_order_list[-1], self.frame)

            # Qt에서 사용할 수 있는 이미지로 변환
            rgb_image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

            self.frame_ready.emit(qt_image)
            cv2.waitKey(1)

        self.cap.release()
        cv2.destroyAllWindows()

    def save_color_info(self) -> bool:
        if len(self.face_info) != 9:
            print("Face information is invalid length:", self.face_info)
            return False
        
        captured_face = ColorUtils.color_string_to_face(self.face_info)
        center = captured_face[4]

        print("captured face info:", self.face_info)
        print("captured face:", captured_face)
        print("center:", center)

        if "u" in self.face_info:
            print("Face information is invalid color:", self.face_info)
            return False
        
        if self.capture_help_mode:
            if self.capture_order_list[-1] == center:
                self.capture_order_list.pop()
            else: 
                print("Not matched center and capture order:", center, self.capture_order_list[-1])
                print("Please capture again ", self.capture_order_list[-1])
                return False
            if len(self.capture_order_list) == 0:
                self.capture_help_mode = False
                print("Capture Help Mode is finished")
        else:
            pass

        self.cube.updateFace(center, captured_face)
        return True

    def standard_color_update(self, color_name, hsv):
        COLORS[color_name].update_hsv(hsv)
        print(f'{color_name} color updated to {hsv}')
        print(f"Current COLORS MAP : {str(COLORS)}")

    def get_captured_center_hsv(self):
        return self.hsv[self.hsv.shape[0] // 2, self.hsv.shape[1] // 2]

