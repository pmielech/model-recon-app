import time
import cv2
import mediapipe as mp
import sys

from interface import *


width, height = 800, 600
userInput = sys.argv
app = None


def init_camera():
    global width, height
    vid_object = cv2.VideoCapture(0)
    vid_object.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    vid_object.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return vid_object


def numpy_to_pixmap(numpy_image):
    num_height, num_width, channel = numpy_image.shape
    q_image = QImage(numpy_image.data, num_width, num_height, QImage.Format_RGBA8888)

    return QPixmap.fromImage(q_image)


def get_frame(video: cv2.VideoCapture):
    _, frame = video.read()
    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_NEAREST)

    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)


def video_loop(video: cv2.VideoCapture, relative_app: QWidget):
    frame = get_frame(video)
    if frame is not None:
        relative_app.updateUi_image(frame)



def run_cam_process(pass_app: QWidget):
    video = init_camera()
    video_loop(video, pass_app)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = Window()
    window.show()
    sys.exit(app.exec_())
