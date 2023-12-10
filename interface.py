from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from main import update_image


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
        load_button = QPushButton('Get frame')
        load_button.clicked.connect(self.button_click_)

        button_layout.addWidget(load_button)

        self.comboBox = QComboBox()
        self.comboBox.addItems(['Image', 'Video', 'Cam'])
        self.comboBox.currentIndexChanged.connect(self.handle_combobox_change)
        button_layout.addWidget(self.comboBox)

        button_layout.addWidget(QPushButton('Start'))

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

    def button_click_(self):
        update_image(self)

    def handle_combobox_change(self, index):
        selected_option = self.comboBox.currentText()
