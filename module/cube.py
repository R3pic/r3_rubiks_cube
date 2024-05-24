import cv2
import numpy as np
import kociemba
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QImage

from .color import ColorUtils

class Cube(QObject):
    # error_signal = pyqtSignal(str)
    face_updated = pyqtSignal(QImage)

    def __init__(self, cube_str=None):
        super().__init__()
        # default_cube = 'yyyyyyyyybbbbbbbbbrrrrrrrrrgggggggggooooooooowwwwwwwww'
        self.set_cube(cube_str)
        # self.draw()

    def set_cube(self, cube_str=None):
        default_cube = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'
        self.cube = {
            'U': cube_str[:9] if cube_str else default_cube[:9],
            'R': cube_str[9:18] if cube_str else default_cube[9:18],
            'F': cube_str[18:27] if cube_str else default_cube[18:27],
            'D': cube_str[27:36] if cube_str else default_cube[27:36],
            'L': cube_str[36:45] if cube_str else default_cube[36:45],
            'B': cube_str[45:] if cube_str else default_cube[45:]
        }

    def reset(self):
        self.set_cube()
        self.draw()

    def _parse_face(self):
        return ''.join([self.cube['U'], self.cube['R'], self.cube['F'], self.cube['D'], self.cube['L'], self.cube['B']])

    def draw(self):
        img_size = 512
        square_size = img_size // 12
        img = np.ones((img_size, img_size, 3), dtype=np.uint8) * 255

        positions = {
            'U': (square_size * 3, 0),
            'L': (0, square_size * 3),
            'F': (square_size * 3, square_size * 3),
            'R': (square_size * 6, square_size * 3),
            'B': (square_size * 9, square_size * 3),
            'D': (square_size * 3, square_size * 6)
        }

        draw_face(img, self.cube['U'], *positions['U'], square_size)
        draw_face(img, self.cube['D'], *positions['D'], square_size)
        draw_face(img, self.cube['B'], *positions['B'], square_size)
        draw_face(img, self.cube['F'], *positions['F'], square_size)
        draw_face(img, self.cube['L'], *positions['L'], square_size)
        draw_face(img, self.cube['R'], *positions['R'], square_size)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        height, width, _ = img.shape
        bytes_per_line = 3 * width
        q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.face_updated.emit(q_img)

    def updateFace(self, center, colors):
        self.cube[center] = colors
        self.draw()

    def solve(self):
        result, message = self.is_valid()
        if not result:
            print(f"from Cube.solve() {message}")
            return
        
        cubestring = self._parse_face()
        moves = kociemba.solve(cubestring)
        return moves

    def is_valid(self) -> tuple[bool, str]:
        try:
            kociemba.solve(self._parse_face())
            return (True, "You Can Solve This Cube")
        except ValueError as e:
            e_str = str(e)
            if "Probably" in e_str:
                # self.error_signal.emit("This Cube is Invalid")
                return (False, "This Cube is Invalid")
            else:
                # self.error_signal.emit(e_str)
                return (False, e_str)


def draw_face(img, faces, start_x, start_y, square_size):
    for i in range(3):
        for j in range(3):
            index = i * 3 + j
            face = faces[index]
            cv2.rectangle(img, 
                          (start_x + j * square_size, start_y + i * square_size), 
                          (start_x + (j + 1) * square_size, start_y + (i + 1) * square_size), 
                          colors_bgr[face], -1)
            cv2.rectangle(img, 
                          (start_x + j * square_size, start_y + i * square_size), 
                          (start_x + (j + 1) * square_size, start_y + (i + 1) * square_size), 
                          (0, 0, 0), 1)
            if index == 4:
                cv2.putText(img, face, (start_x + j * square_size + 10, start_y + i * square_size + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

colors_bgr = {
    'L': (0, 0, 255),  # Red
    'F': (0, 255, 0),  # Green
    'B': (255, 0, 0),  # Blue
    'U': (0, 255, 255),  # Yellow
    'D': (255, 255, 255),  # White
    'R': (0, 165, 255)   # Orange
}

if __name__ == "__main__":
    cube = "wowgybwyogygybyoggrowbrgywrborwggybrbwororbwborgowryby"
    mCube = Cube(cube)
    mCube.draw()
    cubestring = ""
    for c in cube:
        cubestring += ColorUtils.color_to_face(c)
    
    print("반환값 : ",cubestring)

    moves = kociemba.solve(cubestring)
    print(moves)

    # cube2 = "wywryoryrgbygbybwgbbgrrowgbywrgggroybooworoboryyrwbwwg"
    # count = {
    #     'w': 0,
    #     'y': 0,
    #     'r': 0,
    #     'g': 0,
    #     'b': 0,
    #     'o': 0
    # }
    # for c in cube2:
    #     count[c] += 1
    
    # print(count)
    # utils.pprint(cube2)
    # mCube2 = Cube(cube2)
    # mCube2.draw()
    # moves2 = utils.solve(cube2, 'Kociemba')
    # print(moves2)


    cv2.waitKey(0)