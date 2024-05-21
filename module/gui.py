import sys
import colorsys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QWidget, QSlider, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton


from .color import Color_HSV, COLORS, ColorUtils
from .cube import Cube
from .color_detector import ColorDetectorThread

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cube Color Detection Option Panel')
        self.setGeometry(100, 100, 800, 600)
        self.sliders = {}  # Initialize the dictionary to store slider and label references
        self.cube = Cube()
        self.color_detector_thread = ColorDetectorThread(self.cube)
        self.color_detector_thread.color_detected.connect(self.gui_update)
        self.init_UI()
        self.color_detector_thread.start()

    def init_UI(self):
        # 메인 위젯 생성
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.layout: QVBoxLayout = QVBoxLayout()
        self.mainWidget.setLayout(self.layout)

        self.label = QLabel('Cube Color Detection Option Panel')
        self.layout.addWidget(self.label)

        # 슬라이더 추가
        self.add_color_sliders('Red', COLORS['r'])
        self.add_color_sliders('Green', COLORS['g'])
        self.add_color_sliders('Blue', COLORS['b'])
        self.add_color_sliders('Yellow', COLORS['y'])
        self.add_color_sliders('White', COLORS['w'])
        self.add_color_sliders('Orange', COLORS['o'])

        # 캡쳐 버튼 추가
        self.layout.addStretch()
        self.capture_button = QPushButton('Cube Capture')
        self.capture_button.clicked.connect(lambda: self.color_detector_thread.save_color_info())
        self.layout.addWidget(self.capture_button)

        # 큐브 해답 버튼 추가
        self.layout.addStretch()
        self.solve_button = QPushButton('Solve')
        self.solve_button.clicked.connect(self.clicked_solve)
        self.layout.addWidget(self.solve_button)

    def add_color_sliders(self, color_name: str, color_hsv: Color_HSV):
        # 그룹 레이아웃
        group_layout = QHBoxLayout()

        group_label = QLabel(color_name)
        group_layout.addWidget(group_label)

        value_label = QLabel(str(color_hsv.main_hsv))
        group_layout.addWidget(value_label)

        color_display = QLabel()
        color_display.setFixedSize(50, 20)
        color_display.setStyleSheet(f'background-color: {self.hsv_to_rgb_css(color_hsv.min_hsv)}')
        group_layout.addWidget(color_display)

        update_button = QPushButton(f'Standard Color Update ({color_name}))')
        update_button.clicked.connect(lambda: self.standard_color_update(color_name))
        group_layout.addWidget(update_button)

        self.layout.addLayout(group_layout)

        # 슬라이더 레이아웃
        hsv_layout = QGridLayout()

        hue_label = QLabel('Hue')
        hue_slider = QSlider(Qt.Horizontal)
        hue_slider.setMinimum(0)
        hue_slider.setMaximum(180)
        hue_slider.setValue((color_hsv.min_hsv[0] + color_hsv.max_hsv[0]) // 2)
        hsv_layout.addWidget(hue_label, 0, 0)
        hsv_layout.addWidget(hue_slider, 0, 1)

        sat_label = QLabel('Saturation')
        sat_slider = QSlider(Qt.Horizontal)
        sat_slider.setMinimum(0)
        sat_slider.setMaximum(255)
        sat_slider.setValue((color_hsv.min_hsv[1] + color_hsv.max_hsv[1]) // 2)
        hsv_layout.addWidget(sat_label, 1, 0)
        hsv_layout.addWidget(sat_slider, 1, 1)

        val_label = QLabel('Value')
        val_slider = QSlider(Qt.Horizontal)
        val_slider.setMinimum(0)
        val_slider.setMaximum(255)
        val_slider.setValue((color_hsv.min_hsv[2] + color_hsv.max_hsv[2]) // 2)
        hsv_layout.addWidget(val_label, 2, 0)
        hsv_layout.addWidget(val_slider, 2, 1)

        self.layout.addLayout(hsv_layout)

        # 슬라이더 저장
        self.sliders[color_name] = {
            'hue_slider': hue_slider,
            'sat_slider': sat_slider,
            'val_slider': val_slider,
            'color_display': color_display,
            'value_label': value_label,
        }

        # 슬라이더 이벤트 연결
        hue_slider.valueChanged.connect(lambda: self.on_slider_value_change(color_name))
        sat_slider.valueChanged.connect(lambda: self.on_slider_value_change(color_name))
        val_slider.valueChanged.connect(lambda: self.on_slider_value_change(color_name))

    def hsv_to_rgb_css(self, hsv):
        h, s, v = hsv[0] / 180.0, hsv[1] / 255.0, hsv[2] / 255.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        return f'rgb({r}, {g}, {b})'
    
    def on_slider_value_change(self, color_name):
        hue_slider: QSlider = self.sliders[color_name]['hue_slider']
        sat_slider: QSlider = self.sliders[color_name]['sat_slider']
        val_slider: QSlider = self.sliders[color_name]['val_slider']
        color_display: QLabel = self.sliders[color_name]['color_display']
        value_label: QLabel = self.sliders[color_name]['value_label']

        h = hue_slider.value()
        s = sat_slider.value()
        v = val_slider.value()
        color_display.setStyleSheet(f'background-color: {self.hsv_to_rgb_css((h, s, v))}')
        value_label.setText(f'({h}, {s}, {v})')

    def clicked_solve(self):
        print("Solve Button Clicked")
        try:
            moves = self.cube.solve()
            print(moves)
        except ValueError as e:
            print(e)
    
    def gui_update(self, color_name, hsv):
        h_slider: QSlider = self.sliders[color_name]['hue_slider']
        s_slider: QSlider = self.sliders[color_name]['sat_slider']
        v_slider: QSlider = self.sliders[color_name]['val_slider']
        color_display: QLabel = self.sliders[color_name]['color_display']
        value_label: QLabel = self.sliders[color_name]['value_label']

        h_slider.setValue(hsv[0])
        s_slider.setValue(hsv[1])
        v_slider.setValue(hsv[2])
        color_display.setStyleSheet(f'background-color: {self.hsv_to_rgb_css(hsv)}')
        value_label.setText(f'({hsv[0]}, {hsv[1]}, {hsv[2]})')

    def standard_color_update(self, color_name):
        hsv = self.color_detector_thread.get_captured_center_hsv()

        self.gui_update(color_name, hsv)

        COLORS[ColorUtils.get_short_color_name(color_name)].update_hsv(hsv)

        print(f'{color_name} color updated to {hsv}')
        print(f"Current COLORS MAP : {str(COLORS)}")

def start():
    app = QApplication(sys.argv)
    main_window = App()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    start()