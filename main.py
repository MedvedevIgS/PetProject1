import sys
import cv2
from PyQt5 import QtGui, QtCore, QtWidgets, uic
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import qimage2ndarray

class MainWindow(QMainWindow):
    def __init__(self, width=640, height=480, fps=30):
        super(MainWindow, self).__init__()
        uic.loadUi("MainWin.ui", self)
        self.video_size = QtCore.QSize(width, height)
        self.camera_cap = cv2.VideoCapture(cv2.CAP_DSHOW)
        self.frame_time = QtCore.QTimer()
        self.setup_camera(fps)
        self.fps=fps
        self.Video.setFixedSize(self.video_size)

    def setup_camera(self, fps):
        self.camera_cap.set(3, self.video_size.width())
        self.camera_cap.set(4, self.video_size.height())
        self.frame_time.timeout.connect(self.display_video_stream)
        self.frame_time.start(int(1000//fps))

    def display_video_stream(self):
        ret, frame = self.camera_cap.read()
        if not ret:
            return False

        frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = qimage2ndarray.array2qimage(frame)
        self.Video.setPixmap(QtGui.QPixmap(image))
def application():
    app = QApplication(sys.argv)
    window = MainWindow()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(window)
    widget.setMinimumWidth(880)
    widget.setMinimumHeight(520)
    widget.show()
    app.exec()

if __name__ == "__main__":
    application()