from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from main import update_image, init_camera, video_loop, vid, cam_process


class Window(QWidget):

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

    def button_click_(self):
        update_image(self)

    def button_click_Load(self):
        pass

    def button_click_Start(self):
        global vid
        index = self.comboBox.currentIndex()

        if index == 0:
            cam_process(self, vid)

        elif index == 1:

            pass

        elif index == 2:

            pass

    def handle_combobox_change(self, index):
        if index == 0:
            self.load_button.setEnabled(False)
        else:
            self.load_button.setEnabled(True)

