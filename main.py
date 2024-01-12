import os
from datetime import datetime
import time
import cv2
import mediapipe as mp
import sys

from interface import *

OUTPUTDIR = "OUTPUT/"
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.3, model_complexity=1)
mp_drawing = mp.solutions.drawing_utils

width, height = 800, 600
userInput = sys.argv
app = None

fourcc = cv2.VideoWriter_fourcc(*'MP4V')


def init_camera(source):
    global width, height, fourcc
    vid_object = cv2.VideoCapture(source)
    vid_object.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    vid_object.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    filepath = OUTPUTDIR

    if not os.path.exists(filepath):
        try:
            os.mkdir(filepath)
        except Exception as ex:
            sys.exit(ex)

    current_datetime = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
    filepath += 'VID' + current_datetime + '.mp4'

    try:
        outfile = cv2.VideoWriter(filepath, fourcc, 20.0, (width, height))
    except Exception as ex:
        sys.exit(ex)

    return vid_object, outfile


def numpy_to_pixmap(numpy_image):
    num_height, num_width, channel = numpy_image.shape
    q_image = QImage(numpy_image.data, num_width, num_height, QImage.Format_RGBA8888)

    return QPixmap.fromImage(q_image)


def get_frame(video: cv2.VideoCapture):
    global width, height
    frame_res = None
    try:
        _, frame = video.read()
        if frame is not None:
            frame_res = cv2.resize(frame, (width, height), interpolation=cv2.INTER_NEAREST)

    except Exception as ex:
        print(ex)

    return frame_res


def video_loop(video: cv2.VideoCapture, relative_app: QWidget, thread: QThread):
    frame = get_frame(video)
    if frame is not None:
        rec_frame = recognition_process(frame)
        relative_app.outfile.write(rec_frame)
        frame = cv2.cvtColor(rec_frame, cv2.COLOR_BGR2RGBA)
        relative_app.updateUi_image(frame)

    else:
        video.release()
        thread.terminate()


def recognition_process(image):
    global pose, mp_drawing

    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    # results = pose.process(image)
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image=image, landmark_list=results.pose_landmarks,
                                  connections=mp_pose.POSE_CONNECTIONS)

    return image


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = Window()
    window.show()
    sys.exit(app.exec_())
