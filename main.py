import sys
import cv2
from PyQt5 import QtGui, QtCore, QtWidgets, uic
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import qimage2ndarray
from moviepy.editor import *
import math as m
import os



class MainWindow(QMainWindow):
    flagrec=False
    codec = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter()
    brow=''
    timer=0.0
    cv2_base_dir = os.path.dirname(os.path.abspath(cv2.__file__))
    haar_model_front = os.path.join(cv2_base_dir, 'data/haarcascade_frontalface_default.xml')
    haar_model_prof = os.path.join(cv2_base_dir, 'data/haarcascade_profileface.xml')
    haar_model_eye = os.path.join(cv2_base_dir, 'data/haarcascade_eye.xml')
    haar_model_smile = os.path.join(cv2_base_dir, 'data/haarcascade_smile.xml')
    cascade_smile=cv2.CascadeClassifier(haar_model_smile)
    cascade_front=cv2.CascadeClassifier(haar_model_front)
    cascade_prof = cv2.CascadeClassifier(haar_model_prof)
    cascade_eye = cv2.CascadeClassifier(haar_model_eye)

    def __init__(self, width=640, height=480, fps=30):
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
                clip.write_gif(self.brow+'/gifka.gif', fps=30.0)
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
        face_front=self.cascade_front.detectMultiScale(frame, scaleFactor=2, minNeighbors=5, minSize=(20, 20))
        '''if face_front!=():
            print('x')
            print(face_front[0][0]+face_front[0][2])
            print('y')
            print(face_front[0][1]+face_front[0][3])'''
        for (x, y, w, h) in face_front[:1]:
            cv2.rectangle(frame, (x+10, y), (x+w-10, y+h), (255, 0, 0),2)
        if face_front==():
            face_prof = self.cascade_prof.detectMultiScale(frame, scaleFactor=3, minNeighbors=2, minSize=(20, 20))
            for (x, y, w, h) in face_prof[:1]:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if face_front != ():
            face_eye = self.cascade_eye.detectMultiScale(frame, scaleFactor=2, minNeighbors=4, minSize=(20, 20))
            for (x, y, w, h) in face_eye:
                if x>face_front[0][0] and y>face_front[0][1] and x+w < face_front[0][0]+face_front[0][2] and y+h < face_front[0][1] + face_front[0][3]:
                    cv2.rectangle(frame, (x, y + 3), (x + w, y + h - 3), (0, 0, 255), 2)

            face_smile = self.cascade_smile.detectMultiScale(frame, scaleFactor=2, minNeighbors=20, minSize=(20, 20))
            for (x, y, w, h) in face_smile[:1]:
                if x > face_front[0][0] and y > face_front[0][1] and x + w < face_front[0][0] + face_front[0][2] and y + h < face_front[0][1] + face_front[0][3] and y + h > face_front[0][1] + face_front[0][3]/2:
                    cv2.rectangle(frame, (x, y + 3), (x + w, y + h - 3), (0, 255, 255), 2)



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