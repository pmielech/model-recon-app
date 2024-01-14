from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QTimer, QDateTime, QThread, QEventLoop

from main import cv2, Path
from main import init_camera, video_loop, numpy_to_pixmap, convert_collected_to_json

sourceDict = {
    "Cam": 0,
    "Image": 1,
    "Video": 2
}


class Window(QWidget):

    def __init__(self, width=800, height=600):
        super().__init__()

        self.setWindowTitle('Recon App')
        layout = QGridLayout()

        image_frame = QFrame(self)
        layout.addWidget(image_frame, 0, 0, 2, 2)

        self.image_label = QLabel(image_frame)
        self.image_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        image_frame_layout = QVBoxLayout()
        image_frame_layout.addWidget(self.image_label)
        image_frame.setLayout(image_frame_layout)

        button_layout = QVBoxLayout()

        self.comboBox = QComboBox()
        self.comboBox.addItems(['Cam', 'Image', 'Video'])
        self.comboBox.currentIndexChanged.connect(self.handle_combobox_change)
        button_layout.addWidget(self.comboBox)

        # TODO: add camera sources combobox

        self.load_button = QPushButton('Load file')
        self.load_button.clicked.connect(self.button_click_Load)
        self.load_button.setEnabled(False)
        button_layout.addWidget(self.load_button)

        self.load_work_button = QPushButton('Load work-file')
        self.load_work_button.clicked.connect(self.button_click_Load_workFile)
        button_layout.addWidget(self.load_work_button)

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.button_click_Start)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.button_click_Stop)
        button_layout.addWidget(self.stop_button)

        self.circle_label = QLabel()
        layout.addWidget(self.circle_label)

        layout.addLayout(button_layout, 0, 2, 2, 1)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 1)

        self.set_circle_color(Qt.red)
        self.setLayout(layout)

        ## ATRIBUTES
        self.selected_source = None
        self.current_image = None
        self.videoCollectionThread = None
        self.input_path = None
        self.video = None
        self.outfile = None
        self.session = None
        self.image_width = width
        self.image_height = height
        self.set_empty_image()

    def set_circle_color(self, color):
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QColor(color))
        painter.drawEllipse(0, 0, 20, 20)
        painter.end()
        self.circle_label.setPixmap(pixmap)

    def cam_process(self, vid_source):
        self.video, self.outfile, self.session = init_camera(vid_source, self)

        if self.video is None or not self.video.isOpened():
            print('Warning: unable to open video source: ', self.video)

        else:
            self.videoCollectionThread = VideoCaptureThread(self, self.video)
            self.videoCollectionThread.setTerminationEnabled(True)
            self.videoCollectionThread.start()

    def updateUi_image(self, image):
        pixmap = numpy_to_pixmap(image)
        self.image_label.setPixmap(pixmap)

    def set_empty_image(self):
        empty_image = QImage(self.image_width, self.image_height, QImage.Format_RGB32)
        empty_image.fill(Qt.white)
        self.image_label.setPixmap(QPixmap.fromImage(empty_image))

    def load_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Choose image', '',
                                                   'Images (*.png *.jpg *.jpeg *.gif)')
        if file_path:
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap)

    def load_video(self):
        file_dialog = QFileDialog()
        self.input_path, _ = file_dialog.getOpenFileName(self, 'Choose video', '',
                                                         'Video (*.mp4 *.flv *.ts *.mts *.avi *.mov)')

    def get_file_path(self, is_workfile=False):
        self.selected_source = self.comboBox.currentText()
        sel_type = None
        file_format = None
        if not is_workfile:
            if self.selected_source == "Video":
                sel_type = "video"
                file_format = 'Video (*.mp4 *.flv *.ts *.mts *.avi *.mov)'
            elif self.selected_source == "Image":
                sel_type = "image"
                file_format = 'Images (*.png *.jpg *.jpeg *.gif)'

            try:
                if sel_type is not None:
                    file_dialog = QFileDialog()
                    self.input_path, _ = file_dialog.getOpenFileName(self, 'Choose ' + sel_type, '',
                                                                     file_format)

                    self.show_info_message("Success!", "Chosen file: " + self.input_path)

            except Exception as ex:
                print(ex)
        else:
            sel_type = "workfile"
            file_format = 'Text file (*.txt)'
            file_dialog = QFileDialog()
            path, _ = file_dialog.getOpenFileName(self, 'Choose ' + sel_type, '',
                                                  file_format)
            self.convertWorkfile_toJson(path)

    def convertWorkfile_toJson(self, path):
        try:
            session = Path(path).stem
            convert_collected_to_json(session)
            self.show_info_message("Success!", "Operation completed. Successfully saved collected data.")
        except Exception as ex:
            self.show_info_message("Something went wrong!", str(ex))

        pass

    def button_click_Load(self):
        self.get_file_path()

    def button_click_Load_workFile(self):
        self.get_file_path(is_workfile=True)

    def show_info_message(self, title: str, message: str):
        dialog = QMessageBox(self)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setIcon(QMessageBox.Information)
        dialog.exec_()

    def button_click_Stop(self):
        if self.videoCollectionThread is not None:
            self.videoCollectionThread.terminate()
            self.set_circle_color(Qt.red)
            self.video.release()
            self.outfile.release()
            try:
                convert_collected_to_json(str(self.session))
                self.show_info_message("Success!", "Operation completed. Successfully saved collected data.")
            except Exception as ex:
                self.show_info_message("Something went wrong!", str(ex))
        pass

    def button_click_Start(self):

        self.selected_source = self.comboBox.currentText()
        self.set_circle_color(Qt.green)

        selection = self.selected_source
        source = None

        if selection in sourceDict.keys():
            index = sourceDict.get(selection)
            if index > 0:
                source = self.input_path
            else:
                source = 0

        if source is not None:
            if self.videoCollectionThread is None or not self.videoCollectionThread.isRunning():
                self.cam_process(source)

    def handle_combobox_change(self, index):

        if index == 0:
            self.load_button.setEnabled(False)
        else:
            self.load_button.setEnabled(True)


class VideoCaptureThread(QThread):

    def __init__(self, relative_app: QWidget, video: cv2.VideoCapture, *args, **kwargs):
        QThread.__init__(self, *args, **kwargs)
        self.dataCollectionTimer = QTimer()
        self.dataCollectionTimer.moveToThread(self)
        self.frame = None
        self.dataCollectionTimer.timeout.connect(lambda: video_loop(video, relative_app, self))

    def run(self):
        self.dataCollectionTimer.start(50)
        loop = QEventLoop()
        loop.exec_()
