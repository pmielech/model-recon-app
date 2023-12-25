import time

from interface import *
import cv2
import mediapipe as mp
import sys

width, height = 800, 600
vid = None
img = None
label_widget = None
userInput = sys.argv
app = None


if __name__ == '__main__':
    # vid = init_camera()
    app = QApplication(sys.argv)

    window = Window()
    window.show()
    sys.exit(app.exec_())
