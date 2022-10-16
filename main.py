import sys
import cv2
from PyQt5 import QtGui, QtCore, QtWidgets, uic
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import qimage2ndarray
from moviepy.editor import *
import math as m

class MainWindow(QMainWindow):
    flagrec=False
    codec = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter()
    brow=''
    timer=0.0
    def __init__(self, width=640, height=480, fps=60):
        super(MainWindow, self).__init__()
        uic.loadUi("MainWin.ui", self)
        self.labelREC.setVisible(False)
        self.BrowBut.clicked.connect(self.browsefiles)
        self.video_size = QtCore.QSize(width, height)
        self.height=height
        self.width = width
        self.camera_cap = cv2.VideoCapture(cv2.CAP_DSHOW)
        self.frame_time = QtCore.QTimer()
        self.real_time = QtCore.QTimer()
        self.setup_camera(fps)
        self.fps=fps
        self.Video.setFixedSize(self.video_size)
        self.recVideo.clicked.connect(self.rec)

    def browsefiles(self):
        dirname = QFileDialog.getExistingDirectory(self, 'Open Directory',)
        print(dirname)
        self.linebrow.setText(dirname)
        self.brow=dirname


    def rec(self):
        if self.linebrow.text()!='':
            self.flagrec = not self.flagrec
            if self.flagrec:
                self.timer=0.0
                self.timerLine.setText('0.0')
                self.real_time.timeout.connect(self.timerVideo)
                self.real_time.start(int(100))
                self.labelREC.setVisible(True)
                self.out = cv2.VideoWriter(self.brow+'/output.avi', self.codec, 30.0, (self.width, self.height))
            else:
                self.out.release()
                self.labelREC.setVisible(False)
                self.real_time.stop()
                clip = VideoFileClip(self.brow+'/output.avi')
                clip.write_gif(self.brow+'/gifka.gif', fps=10.0)
        else:
            self.linebrow.setText("Укажите путь для записи")
            self.browsefiles()

    def timerVideo(self):
        self.timer = self.timer+1
        milsek=m.trunc(self.timer%10)
        sek=m.trunc(self.timer/10)
        strTime=str(sek)+'.'+str(milsek)
        self.timerLine.setText(strTime)


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
        cv2.putText(frame, self.VideoText.text(), (int((self.width/100)*(self.PozText.value()+1)), 420), cv2.FONT_HERSHEY_COMPLEX, 1,(0,0,0),2, cv2.LINE_AA)
        if self.flagrec:
            self.out.write(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = qimage2ndarray.array2qimage(frame)
        self.Video.setPixmap(QtGui.QPixmap(image))


def application():
    app = QApplication(sys.argv)
    window = MainWindow()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(window)
    widget.setMinimumWidth(975)
    widget.setMinimumHeight(525)
    widget.show()
    app.exec()

if __name__ == "__main__":
    application()