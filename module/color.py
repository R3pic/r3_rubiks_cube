import json
import numpy as np

class Color_HSV:
    def __init__(self, hsv=None, min_hsv=None, max_hsv=None) -> None:
        if hsv is None and (min_hsv is None or max_hsv is None):
            raise ValueError("HSV or min_hsv and max_hsv should be given")

        if min_hsv is None:
            min_hsv = (hsv[0] - 10, hsv[1] - 50, hsv[2] - 50)
            self.min_hsv = np.clip(min_hsv, 0, 255)
        else:
            self.min_hsv = min_hsv
        if max_hsv is None:
            max_hsv = (hsv[0] + 10, hsv[1] + 50, 255)
            self.max_hsv = np.clip(max_hsv, 0, 255)
        else:
            self.max_hsv = max_hsv
 
        if hsv:
            self.main_hsv = hsv
        else:
            self.main_hsv = (min_hsv[0] + 10, min_hsv[1] + 50, min_hsv[2] + 50)

    def update_hsv(self, hsv: tuple[int, int, int]):
        self.main_hsv = hsv
        self.min_hsv = np.clip((hsv[0] - 10, hsv[1] - 50, hsv[2] - 50), 0, 255)
        self.max_hsv = np.clip((hsv[0] + 10, hsv[1] + 50, 255), 0, 255)

        print("Updated HSV:", self)

    def set_hsv(self, hsv):
        self.main_hsv = hsv

    def set_min_hsv(self, min_hsv):
        self.min_hsv = min_hsv

    def set_max_hsv(self, max_hsv):
        self.max_hsv = max_hsv

    def __repr__(self) -> str:
        return str((self.min_hsv, self.max_hsv))
    
    def __str__(self) -> str:
        return f"Color_HSV(min : {self.min_hsv}, max : {self.max_hsv})\n main : {self.main_hsv}"


COLORS = {
    'o': Color_HSV(min_hsv=(10, 100, 20), max_hsv=(25, 255, 255)),
    'r': Color_HSV(min_hsv=(0, 100, 100), max_hsv=(10, 255, 255)),
    'g': Color_HSV(min_hsv=(40, 50, 50), max_hsv=(90, 255, 255)),
    'b': Color_HSV(min_hsv=(100, 150, 0), max_hsv=(140, 255, 255)),
    'y': Color_HSV(min_hsv=(20, 100, 100), max_hsv=(30, 255, 255)),
    'w': Color_HSV(min_hsv=(0, 0, 50), max_hsv=(180, 50, 255)),
}

def standard_color_info_save(name: str):
    global COLORS

    data = {}

    # JSON 파일이 이미 존재하면 기존 데이터를 로드
    try:
        with open('color_info.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        pass

    # 현재 COLORS 데이터의 main_hsv 정보만 새로운 이름으로 저장
    color_data = {
        color_name: color_hsv.main_hsv.tolist() if isinstance(color_hsv.main_hsv, np.ndarray) else color_hsv.main_hsv
        for color_name, color_hsv in COLORS.items()
    }
    data[name] = color_data

    # JSON 파일에 저장
    with open('color_info.json', 'w') as f:
        json.dump(data, f, indent=4)

def standard_color_info_load(name: str):
    global COLORS

    # JSON 파일에서 데이터를 로드
    try:
        with open('color_info.json', 'r') as f:
            data = json.load(f)

        if name in data:
            color_data = data[name]
            for color_name, main_hsv in color_data.items():
                if color_name in COLORS:
                    COLORS[color_name].update_hsv(main_hsv)
            print(f"Loaded color info for {name}:", COLORS)
        else:
            print(f"No color info found for {name}")
    except FileNotFoundError:
        print("No color info file found")

class ColorUtils:
    @staticmethod
    def get_bgr_color(color_name: str):
        return {
            'r': (0, 0, 255),  # Red
            'g': (0, 255, 0),  # Green
            'b': (255, 0, 0),  # Blue
            'y': (0, 255, 255),  # Yellow
            'w': (255, 255, 255),  # White
            'o': (0, 165, 255),   # Orange
            'u': (0, 0, 0)  # Unknown
        }.get(color_name, (0, 0, 0))

    @staticmethod
    def color_to_face(color_name: str):
        return {
            'g': 'F',
            'o': 'R',
            'r': 'L',
            'y': 'U',
            'w': 'D',
            'b': 'B'
        }.get(color_name, 'U')
    
    @staticmethod
    def face_to_color(face_name: str):
        return {
            'F': 'g',
            'R': 'o',
            'L': 'r',
            'U': 'y',
            'D': 'w',
            'B': 'b'
        }.get(face_name, 'u')

    @staticmethod
    def get_short_color_name(color_name):
        return {
            'Red': 'r',
            'Green': 'g',
            'Blue': 'b',
            'Yellow': 'y',
            'White': 'w',
            'Orange': 'o'
        }.get(color_name, 'u')
    
    @staticmethod
    def get_long_color_name(short_name):
        return {
            'r': 'Red',
            'g': 'Green',
            'b': 'Blue',
            'y': 'Yellow',
            'w': 'White',
            'o': 'Orange'
        }.get(short_name, 'Unknown')
    
    @staticmethod
    def get_color_name(hsv: tuple[int, int, int]):
        for color_name, Color_hsv in COLORS.items():
            lower = np.array(Color_hsv.min_hsv)
            upper = np.array(Color_hsv.max_hsv)
            if np.all(lower <= hsv) and np.all(hsv <= upper):
                return color_name
        return 'u'
    
    @staticmethod
    def color_string_to_face(color_string: str) -> str:
        return "".join([ColorUtils.color_to_face(color) for color in color_string])

def reset_COLORS():
    global COLORS
    COLORS = {
        'r': Color_HSV(min_hsv=(0, 100, 100), max_hsv=(10, 255, 255)),
        'g': Color_HSV(min_hsv=(40, 50, 50), max_hsv=(90, 255, 255)),
        'b': Color_HSV(min_hsv=(100, 150, 0), max_hsv=(140, 255, 255)),
        'y': Color_HSV(min_hsv=(20, 100, 100), max_hsv=(30, 255, 255)),
        'w': Color_HSV(min_hsv=(0, 0, 50), max_hsv=(180, 50, 255)),
        'o': Color_HSV(min_hsv=(10, 100, 20), max_hsv=(25, 255, 255)),
    }