import cv2
import numpy as np
import kociemba

from .color import ColorUtils

class Cube:
    def __init__(self, cube_str=None):
        if cube_str:
            self.cube = {
                'U': cube_str[:9],
                'L': cube_str[9:18],
                'F': cube_str[18:27],
                'R': cube_str[27:36],
                'B': cube_str[36:45],
                'D': cube_str[45:]
            }
        else:
            self.cube = {
                'U': 'yyyyyyyyy',
                'L': 'bbbbbbbbb',
                'F': 'rrrrrrrrr',
                'R': 'ggggggggg',
                'B': 'ooooooooo',
                'D': 'wwwwwwwww'
            }

    def reset(self):
        self.cube = {
            'U': 'yyyyyyyyy',
            'L': 'bbbbbbbbb',
            'F': 'rrrrrrrrr',
            'R': 'ggggggggg',
            'B': 'ooooooooo',
            'D': 'wwwwwwwww'
        }
        self.draw()

    def show(self):
        print(self)

    def draw(self):
        img_size = 600
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

        if self.is_valid():
            cv2.putText(img, "Valid", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        else:
            cv2.putText(img, "Invalid", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.imshow('Cube', img)

    def updateFace(self, face, colors):
        self.cube[face] = colors
        self.draw()

    def solve(self):
        if not self.is_valid():
            print("Invalid cube state")
            return
        
        cubestring = self.__parse_face()
        moves = kociemba.solve(cubestring)
        return moves

    def is_valid(self):
        try:
            kociemba.solve(self.__parse_face())
            return True
        except ValueError as e:
            return False
    
    def __parse_face(self):
        face_colors = ""
        for face in ['U', 'R', 'F', 'D', 'L', 'B']:
            face_colors += self.cube[face]
        cubestring = ""
        for c in face_colors:
            cubestring += ColorUtils.color_to_face(c)
        return cubestring

    def __str__(self) -> str:
        return f"""
                | {self.cube['U'][0]}  | {self.cube['U'][1]}  | {self.cube['U'][2]}  |
                | {self.cube['U'][3]}  | {self.cube['U'][4]}  | {self.cube['U'][5]}  |
                | {self.cube['U'][6]}  | {self.cube['U'][7]}  | {self.cube['U'][8]}  |
| {self.cube['L'][0]}  | {self.cube['L'][1]}  | {self.cube['L'][2]}  || {self.cube['F'][0]}  | {self.cube['F'][1]}  | {self.cube['F'][2]}  || {self.cube['R'][0]}  | {self.cube['R'][1]}  | {self.cube['R'][2]}  || {self.cube['B'][0]}  | {self.cube['B'][1]}  | {self.cube['B'][2]}  |
| {self.cube['L'][3]}  | {self.cube['L'][4]}  | {self.cube['L'][5]}  || {self.cube['F'][3]}  | {self.cube['F'][4]}  | {self.cube['F'][5]}  || {self.cube['R'][3]}  | {self.cube['R'][4]}  | {self.cube['R'][5]}  || {self.cube['B'][3]}  | {self.cube['B'][4]}  | {self.cube['B'][5]}  |
| {self.cube['L'][6]}  | {self.cube['L'][7]}  | {self.cube['L'][8]}  || {self.cube['F'][6]}  | {self.cube['F'][7]}  | {self.cube['F'][8]}  || {self.cube['R'][6]}  | {self.cube['R'][7]}  | {self.cube['R'][8]}  || {self.cube['B'][6]}  | {self.cube['B'][7]}  | {self.cube['B'][8]}  |
                | {self.cube['D'][0]}  | {self.cube['D'][1]}  | {self.cube['D'][2]}  |
                | {self.cube['D'][3]}  | {self.cube['D'][4]}  | {self.cube['D'][5]}  |
                | {self.cube['D'][6]}  | {self.cube['D'][7]}  | {self.cube['D'][8]}  |"""


def draw_face(img, face_colors, start_x, start_y, square_size):
    for i in range(3):
        for j in range(3):
            color = face_colors[i * 3 + j]
            cv2.rectangle(img, 
                          (start_x + j * square_size, start_y + i * square_size), 
                          (start_x + (j + 1) * square_size, start_y + (i + 1) * square_size), 
                          colors_bgr[color], -1)
            cv2.rectangle(img, 
                          (start_x + j * square_size, start_y + i * square_size), 
                          (start_x + (j + 1) * square_size, start_y + (i + 1) * square_size), 
                          (0, 0, 0), 1)

colors_bgr = {
    'r': (0, 0, 255),  # Red
    'g': (0, 255, 0),  # Green
    'b': (255, 0, 0),  # Blue
    'y': (0, 255, 255),  # Yellow
    'w': (255, 255, 255),  # White
    'o': (0, 165, 255)   # Orange
}

if __name__ == "__main__":
    cube = "wowgybwyogygybyoggrowbrgywrborwggybrbwororbwborgowryby"
    mCube = Cube(cube)

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