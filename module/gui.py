import json
import os
import sys
import colorsys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QWidget, QSlider, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLineEdit, QInputDialog, QMessageBox, QComboBox
from PyQt5.QtGui import QKeyEvent, QPixmap

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module.color import Color_HSV, COLORS, ColorUtils, standard_color_info_load, standard_color_info_save
from module.cube import Cube
from module.color_detector import ColorDetectorThread

class App(QMainWindow):
    def __init__(self, auto_detect=True):
        super().__init__()
        self.setWindowTitle('Cube Color Detection Option Panel')
        self.setGeometry(100, 100, 1280, 720)
        self.sliders = {}
        self.init_UI()
        self.cube = Cube()
        self.cube.face_updated.connect(lambda img: self.cube_view.setPixmap(QPixmap.fromImage(img)))
        self.cube.draw()
        # self.cube.error_signal.connect(lambda msg: self.solve_moves_label.setText(msg))
        self.color_detector_thread = ColorDetectorThread(self.cube)
        self.color_detector_thread.frame_ready.connect(self.update_video_frame)
        self.color_detector_thread.color_detected.connect(self.gui_update)
        if auto_detect:
            self.color_detector_thread.start()

            
        self.capture_help_button.clicked.connect(self.color_detector_thread.start_capture_help_mode)


    def init_UI(self):
        # 메인 위젯 생성
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.layout: QHBoxLayout = QHBoxLayout()
        self.mainWidget.setLayout(self.layout)

        self.leftLayout = QVBoxLayout()
        self.rightLayout = QHBoxLayout()

        self.layout.addLayout(self.leftLayout)
        self.layout.addLayout(self.rightLayout)

        self.label = QLabel('Cube Color Detection Option Panel')
        self.leftLayout.addWidget(self.label)

        self.capture_help_button = QPushButton('Capture Helper Start')
        self.leftLayout.addWidget(self.capture_help_button)

        self.standard_combo = QComboBox()
        self.standard_combo_update()
        self.standard_combo.currentTextChanged.connect(self.combo_box_selection_changed)
        self.leftLayout.addWidget(self.standard_combo)

        self.color_load()

        # 슬라이더 추가
        self.add_color_sliders('Red', COLORS['r'])
        self.add_color_sliders('Green', COLORS['g'])
        self.add_color_sliders('Blue', COLORS['b'])
        self.add_color_sliders('Yellow', COLORS['y'])
        self.add_color_sliders('White', COLORS['w'])
        self.add_color_sliders('Orange', COLORS['o'])

        self.standard_color_info_save_button = QPushButton('Save Standard Color Info')
        self.leftLayout.addWidget(self.standard_color_info_save_button)
        self.standard_color_info_save_button.clicked.connect(self.standard_color_info_save_button_clicked)

        # 우측 레이아웃
        self.video_layout = QVBoxLayout()
        self.rightLayout.addLayout(self.video_layout)

        self.video_frame = QLabel()
        self.video_frame.setMinimumSize(640, 420)
        self.video_layout.addWidget(self.video_frame)

        self.solve_moves_label = QLineEdit('Solve Moves : ')
        self.solve_moves_label.setReadOnly(True)
        self.solve_moves_label.setStyleSheet('font-size: 15px;')
        self.solve_moves_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.solve_moves_label.setContentsMargins(10, 10, 10, 10)
        self.video_layout.addWidget(self.solve_moves_label)
        self.solve_moves_label.setMinimumHeight(100)

        self.video_layout.addStretch()
        self.capture_button = QPushButton('Cube Capture')
        self.capture_button.setMinimumHeight(50)
        self.capture_button.clicked.connect(self.clicked_capture_button)
        self.video_layout.addWidget(self.capture_button)

        # 큐브 해답 버튼 추가
        self.solve_button = QPushButton('Solve')
        self.solve_button.setMinimumHeight(50)
        self.solve_button.setEnabled(False)
        self.solve_button.clicked.connect(self.clicked_solve)
        self.video_layout.addWidget(self.solve_button)

        self.cube_view = QLabel()
        self.cube_view.setMinimumSize(512, 512)
        self.rightLayout.addWidget(self.cube_view)

    def keyPressEvent(self, a0: QKeyEvent | None) -> None:
        key = a0.key()
        if key == Qt.Key_S:
            self.clicked_capture_button()
        elif key == Qt.Key_Return:
            self.clicked_solve()
        elif key == Qt.Key_R:
            self.pressed_Key_R()
        else:
            super().keyPressEvent(a0)

    def pressed_Key_R(self):
        self.cube.reset()
        self.solve_moves_label.setText('Cube Reset.. Capture Again..')
        self.solve_button.setEnabled(False)

    def color_load(self):
        # 파일이 존재하면 로드하고, 맨 처음 객체 이름으로 로드하기
        if os.path.exists('color_info.json'):
            with open('color_info.json', 'r') as f:
                data = json.load(f)
                first_name = list(data.keys())[0]
                standard_color_info_load(first_name)

    def standard_combo_update(self):
        self.standard_combo.clear()
        try:
            with open('color_info.json', 'r') as f:
                data = json.load(f)
                self.standard_combo.addItems(data.keys())
        except FileNotFoundError:
            self.standard_combo.addItem("No data available")

    def combo_box_selection_changed(self, name: str):
        if name and name != "No data available":
            standard_color_info_load(name)
            for color_name, color_hsv in COLORS.items():
                self.gui_update(ColorUtils.get_long_color_name(color_name), color_hsv.main_hsv)

    def standard_color_info_save_button_clicked(self):
        # 메시지 박스를 이용해서 이름 입력받기
        name, ok = QInputDialog.getText(self, '기본 색상 저장', '이름을 입력하세요:')
        if ok:
            if name:
                standard_color_info_save(name)
                self.standard_combo_update()
            else:
                QMessageBox.warning(self, "경고", "이름을 입력하세요!", QMessageBox.Ok)

    def add_color_sliders(self, color_name: str, color_hsv: Color_HSV):
        # 그룹 레이아웃
        group_layout = QHBoxLayout()

        group_label = QLabel(color_name)
        group_layout.addWidget(group_label)

        value_label = QLabel(str(color_hsv.main_hsv))
        group_layout.addWidget(value_label)

        color_display = QLabel()
        color_display.setFixedSize(50, 20)
        color_display.setStyleSheet(f'background-color: {self.hsv_to_rgb_css(color_hsv.main_hsv)}')
        group_layout.addWidget(color_display)

        update_button = QPushButton(f'Standard Color Update ({color_name}))')
        update_button.clicked.connect(lambda: self.standard_color_update(color_name))
        group_layout.addWidget(update_button)

        self.leftLayout.addLayout(group_layout)

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

        self.leftLayout.addLayout(hsv_layout)

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

        print(f'{color_name} color updated to ({h}, {s}, {v})')
        current_color = COLORS[ColorUtils.get_short_color_name(color_name)]
        current_color.update_hsv((h, s, v))

        color_display.setStyleSheet(f'background-color: {self.hsv_to_rgb_css((h, s, v))}')
        value_label.setText(f'({h}, {s}, {v})')

    def clicked_solve(self):
        print("Solve Button Clicked")
        try:
            moves = self.cube.solve()
            print(f'해답 : {moves}')
            self.solve_moves_label.setText(f'Solve Moves : {moves}')
        except ValueError as e:
            self.solve_moves_label.setText(f'{str(e)}')

    def clicked_capture_button(self):
        issaved = self.color_detector_thread.save_color_info()
        if issaved:
            result, msg = self.cube.is_valid()
            if result:
                self.solve_button.setEnabled(True)
            else:
                self.solve_button.setEnabled(False)
            self.solve_moves_label.setText(msg)
        else:
            self.solve_moves_label.setText('Capture Failed.. Try Again.. unknown color detected..')
    
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

    def update_video_frame(self, qt_img):
        self.video_frame.setPixmap(QPixmap.fromImage(qt_img))

def start(auto_detect=True):
    app = QApplication(sys.argv)
    main_window = App(auto_detect)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    start(auto_detect=False)