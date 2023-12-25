from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QTimer, QDateTime, QThread, QEventLoop
from main import cv2

relative_app = None
frame = None
vid_object = None


def init_camera():
    global width, height, vid_object
    vid_object = cv2.VideoCapture(0)
    vid_object.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    vid_object.set(cv2.CAP_PROP_FRAME_HEIGHT, height)


def numpy_to_pixmap(numpy_image):
    num_height, num_width, channel = numpy_image.shape
    q_image = QImage(numpy_image.data, num_width, num_height, QImage.Format_RGBA8888)

    return QPixmap.fromImage(q_image)


def get_frame(video: cv2.VideoCapture):
    _, frame = video.read()
    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_NEAREST)

    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)


def video_loop(self, video: cv2.VideoCapture, flag):
    global frame
    frame = get_frame(video)
    if frame is not None:
        pixmap = numpy_to_pixmap(frame)
        self.image_label.setPixmap(pixmap)


def collectProcessData():
    global relative_app
    print("Collecting Process Data")
    print(type(relative_app))


class VideoCaptureThread(QThread):

    def __init__(self, *args, **kwargs):
        QThread.__init__(self, *args, **kwargs)
        self.dataCollectionTimer = QTimer()
        self.dataCollectionTimer.moveToThread(self)
        self.dataCollectionTimer.timeout.connect(video_loop())

    def run(self):
        self.dataCollectionTimer.start(1000)
        loop = QEventLoop()
        loop.exec_()

    def setRelativeApp(self, pass_app):
        global relative_app
        relative_app = pass_app


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
        self.set_empty_image()

    def cam_process(self, video: cv2.VideoCapture):
        video = init_camera()
        self.timer = self.QTimer(self)  # Create Timer
        if video is not None:
            self.timer.timeout.connect(video_loop(self, video))  # Connect timeout to the output function
            self.timer.start(40)  # emit the timeout() signal at x=40ms
            # video_loop(app, video, True)

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

    # def load_video(self):
    #     file_dialog = QFileDialog()
    #     file_path, _ = file_dialog.getOpenFileName(self, 'Choose image', '',
    #                                                'Images (*.png *.jpg *.jpeg *.gif)')
    #     if file_path:
    #         pixmap = QPixmap(file_path)
    #         self.image_label.setPixmap(pixmap)

    # def button_click_(self):
    #     update_image(self)

    def button_click_Load(self):
        pass

    def button_click_Start(self):
        self.videoCollectionThread = VideoCaptureThread()
        self.videoCollectionThread.setTerminationEnabled(True)
        self.videoCollectionThread.setRelativeApp(self)
        self.videoCollectionThread.start()
        # global vid
        # index = self.comboBox.currentIndex()
        #
        # if index == 0:
        #     cam_process(self, vid)
        #
        # elif index == 1:
        #
        #     pass
        #
        # elif index == 2:
        #
        #     pass

    def handle_combobox_change(self, index):
        if index == 0:
            self.load_button.setEnabled(False)
        else:
            self.load_button.setEnabled(True)
