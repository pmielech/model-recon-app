from interface import *
import cv2
import mediapipe as mp
import sys

width, height = 800, 600
vid = None
img = None
label_widget = None
userInput = sys.argv


def init_camera():
    global width, height
    video = cv2.VideoCapture(0)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return video


def get_frame(video: cv2.VideoCapture):
    _, frame = video.read()
    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_NEAREST)

    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

def numpy_to_pixmap(numpy_image):
    num_height, num_width, channel = numpy_image.shape
    q_image = QImage(numpy_image.data, num_width, num_height, QImage.Format_RGBA8888)

    return QPixmap.fromImage(q_image)


def update_image(self: QWidget):
    global vid, img
    if vid is None:
        vid = init_camera()
    else:
        frame = get_frame(vid)
        if frame is not None:
            pixmap = numpy_to_pixmap(frame)
            self.image_label.setPixmap(pixmap)


if __name__ == '__main__':
    # vid = init_camera()

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
