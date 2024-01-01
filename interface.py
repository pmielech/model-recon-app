from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QTimer, QDateTime, QThread, QEventLoop

from main import cv2, width, height, run_cam_process
from main import init_camera, video_loop, numpy_to_pixmap

sourceDict = {
    "Cam": 0,
    "Image": 1,
    "Video": 2
}


class Window(QWidget):
    width, height = 800, 600

    def __init__(self):
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

        self.load_button = QPushButton('Load file')
        self.load_button.clicked.connect(self.button_click_Load)
        self.load_button.setEnabled(False)

        button_layout.addWidget(self.load_button)

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.button_click_Start)

        button_layout.addWidget(self.start_button)

        layout.addLayout(button_layout, 0, 2, 2, 1)

        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 1)

        self.setLayout(layout)

        self.selected_source = None
        self.current_image = None
        self.videoCollectionThread = None
        self.input_path = None

        self.set_empty_image()

    def cam_process(self, vid_source):
        video = init_camera(vid_source)

        self.videoCollectionThread = VideoCaptureThread(self, video)
        self.videoCollectionThread.setTerminationEnabled(False)
        self.videoCollectionThread.start()

    def updateUi_image(self, image):
        pixmap = numpy_to_pixmap(image)
        self.image_label.setPixmap(pixmap)

    def set_empty_image(self):
        empty_image = QImage(800, 600, QImage.Format_RGB32)
        empty_image.fill(Qt.white)
        self.image_label.setPixmap(QPixmap.fromImage(empty_image))

    def load_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Choose image', '', 'Images (*.png *.jpg *.jpeg *.gif)')
        if file_path:
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap)

    def load_video(self):
        file_dialog = QFileDialog()
        self.input_path, _ = file_dialog.getOpenFileName(self, 'Choose video', '',
                                                         'Video (*.mp4 *.flv *.ts *.mts *.avi *.mov)')

    def get_file_path(self):
        self.selected_source = self.comboBox.currentText()
        sel_type = None
        file_format = None

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
        except Exception as ex:
            print(ex)

    def button_click_Load(self):
        self.get_file_path()

    def button_click_Start(self):

        self.selected_source = self.comboBox.currentText()

        selection = self.selected_source
        source = None

        if selection in sourceDict.keys():
            index = sourceDict.get(selection)
            if index > 0:
                source = self.input_path
            else:
                source = 0

        if source is not None:
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
