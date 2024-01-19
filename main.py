import os
from datetime import datetime
from pathlib import Path
import time
import cv2
import mediapipe as mp
import sys
import json
import csv

from interface import *
from Frame_class import Frame

JSON_TEMP = "JSON_TEMPLATE.json"
OUTPUTDIR = "OUTPUT/"
WORKDIR = "OUTPUT/WORKFILES/"

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=1)
mp_drawing = mp.solutions.drawing_utils

width, height = 800, 600
userInput = sys.argv
app = None

fourcc = cv2.VideoWriter_fourcc(*'MP4V')
global_frame_cnt = 0
font = cv2.FONT_HERSHEY_SIMPLEX


def check_dir(path):
    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except Exception as ex:
            sys.exit(ex)


def init_camera(source, relative_app: QWidget):
    global width, height, fourcc, global_frame_cnt
    vid_object = cv2.VideoCapture(source)
    vid_object.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    vid_object.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    check_dir(OUTPUTDIR)
    check_dir(WORKDIR)

    filepath = OUTPUTDIR
    global_frame_cnt = 0

    current_datetime = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
    filepath += 'VID' + current_datetime + '.mp4'

    try:
        outfile = cv2.VideoWriter(filepath, fourcc, 30.0, (width, height))
    except Exception as ex:
        relative_app.show_info_message("Something went wrong!", str(ex))

    return vid_object, outfile, current_datetime


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


def create_json(path, session):
    data = None
    with open(JSON_TEMP, 'r', encoding='utf-8') as temp_file:
        data = json.load(temp_file)
        data['session'] = session
        with open(OUTPUTDIR + path, 'a', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4)


def add_frame_to_txt(frame, path):
    with open(path, 'a', encoding='utf-8') as json_file:
        fr_data = json.loads(frame.to_json())
        json.dump(fr_data, json_file, indent=4)
        json_file.write(os.linesep + ',')


def convert_collected_to_json(session):
    json_data = None
    create_json('LOG' + session + '.json', session)
    with open(OUTPUTDIR + 'LOG' + session + '.json', 'r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)

    with open(OUTPUTDIR + 'LOG' + session + '.json', 'w', encoding='utf-8') as json_file:
        if json_data is not None:
            with open(WORKDIR + session + '.txt', 'r', encoding='utf-8') as txt_file:
                str_data = txt_file.read()
            str_data = '[\n' + str_data[:-1] + '\n]'
            list_data = json.loads(str_data)
            json_data['frames'] = list_data
            json.dump(json_data, json_file, indent=4)


def convert_collected_to_csv(session):
    with open(WORKDIR + session + '.txt', 'r', encoding='utf-8') as txt_file:
        str_data = txt_file.read()
    str_data = '[\n' + str_data[:-1] + '\n]'
    list_data = json.loads(str_data)

    with open(OUTPUTDIR + 'LOG' + session + '.csv', 'w', newline='') as csvfile:
        data_writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        col_names = ['Frame index', 'attribute']
        sample_fr = Frame(0)
        for landmark in sample_fr.landmarks_desc.values():
            col_names.append(landmark)
        data_writer.writerow(col_names)
        for frame in list_data:
            x_vals = [frame['index'], 'x']
            y_vals = [frame['index'], 'y']
            z_vals = [frame['index'], 'z']
            vis_vals = [frame['index'], 'vis']
            for landmark in frame['landmarks']:
                x_vals.append(landmark['x'])
                y_vals.append(landmark['y'])
                z_vals.append(landmark['z'])
                vis_vals.append(landmark['visibility'])
            data_writer.writerow(x_vals)
            data_writer.writerow(y_vals)
            data_writer.writerow(z_vals)
            data_writer.writerow(vis_vals)


def build_log(relative_app: QWidget):
    session = relative_app.session

    if relative_app.output_filetype == "csv":
        convert_collected_to_csv(session)
    else:
        convert_collected_to_json(session)


def video_loop(video: cv2.VideoCapture, relative_app: QWidget, thread: QThread):
    global global_frame_cnt
    txt_path = WORKDIR + str(relative_app.session)
    while thread.isRunning():
        frame = get_frame(video)
        if frame is not None:
            rec_frame, frame_obj = recognition_process(frame)
            cv2.putText(rec_frame, str(global_frame_cnt), (10, 50), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

            relative_app.outfile.write(rec_frame)
            if frame_obj is not None:
                add_frame_to_txt(frame_obj, txt_path + '.txt')

            frame = cv2.cvtColor(rec_frame, cv2.COLOR_BGR2RGBA)
            relative_app.updateUi_image(frame)
            global_frame_cnt += 1

        else:
            thread.terminate()
            video.release()
            relative_app.outfile.release()
            relative_app.show_info_message("Connection lost",
                                           "Lost connection with the camera source or video just ended."
                                           "Converting collected data...")
            relative_app.set_circle_color(Qt.red)
            try:
                # convert_collected_to_json(str(relative_app.session))
                build_log(relative_app)
                relative_app.show_info_message("Success!", "Operation completed. Successfully saved collected data.")
                break

            except Exception as ex:
                relative_app.show_info_message("Something went wrong!", str(ex))
                break
        QtTest.QTest.qWait(30)


def recognition_process(image):
    global pose, mp_drawing, global_frame_cnt, width, height
    json_str = None
    frame = None

    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image=image, landmark_list=results.pose_landmarks,
                                  connections=mp_pose.POSE_CONNECTIONS)

        frame = Frame(global_frame_cnt)
        for index, landmark in enumerate(results.pose_landmarks.landmark):
            if landmark is not None:
                try:
                    frame.set_landmark_params(index, landmark.x * width, landmark.y * height, landmark.z, landmark.visibility)
                except Exception as ex:
                    print(ex)

    return image, frame


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = Window(width=width, height=height)
    window.show()
    sys.exit(app.exec_())
