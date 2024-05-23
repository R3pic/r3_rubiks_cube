import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from module.cube import Cube

class TestCubeString(unittest.TestCase):
    def test_cube_string(self):
        cube = Cube()
        cube_str = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'
        
        self.assertEqual(cube_str, cube._parse_face())

if __name__ == '__main__':
    unittest.main()