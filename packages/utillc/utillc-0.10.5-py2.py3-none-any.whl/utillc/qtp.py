
try :

    from PyQt5 import QtGui
    from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout
    from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout, QPushButton, QLineEdit, QSlider, QSpinBox, QCheckBox, QSizePolicy

    from PyQt5.QtGui import QPixmap
    import sys, os
    import cv2
    from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
    import numpy as np
    from utillc import *
    import cv2
    import threading
    from functools import partial
    import queue
    import time

except Exception as e11 :
    pass
    #print("without qt5 or cv2 " + str(e11))

#EKOX(dir(mp_face_mesh))
import numpy as np

__all__ = ( 'video')


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    def __init__(self) :        
        super().__init__()        
        self.queue = queue.Queue(maxsize=50)

    def run(self):
        while True:
            image = self.queue.get()
            #EKOX(image is None)
            if not (image is None) :
                self.change_pixmap_signal.emit(image)

class App(QMainWindow):
    def foo(self, *arg, **kwargs):
        t = ('click', arg[0].x(), arg[0].y())
        self.cb(t)
        #EKOX(t)
        self.queue.put(t)

    def key(self, *arg, **kwargs):
        EKOX(arg)
        EKOX(kwargs)
        
    def __init__(self, cb, nslider=0, title="demo", gui=None):
        super().__init__()
        self.queue = queue.Queue()
        self.cb = cb
        self.gui= gui
        self.setWindowTitle(title)
        self.disply_width = 640
        self.display_height = 480
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)
        # create a text label
        self.textLabel = QLabel('xxx')
        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)

        
        quit = QPushButton("Quit")
        quit.clicked.connect(lambda : (os._exit(0), sys.exit(0)))
        self.counter = QLabel('')
        self.image_label.mousePressEvent = self.foo
        self.image_label.keyPressEvent = self.key
        self.image_label.keyReleaseEvent = self.key

        # create a vertical box layout and add the two labels
        hbox = QWidget()
        hbox.setLayout(QHBoxLayout())
        vbox.addWidget(hbox)

        hbox.layout().addWidget(self.textLabel)
        hbox.layout().addWidget(quit)
        hbox.layout().addWidget(self.counter)

        # set the vbox layout as the widgets layout
        self.setLayout(vbox)

        lslider = []
        def update(n) :
            #EKOX(self.xRotationSlider.value())
            self.cb((self.gui, 'slider', n, lslider[n].value()))

        for i in range(nslider) :
            EKOX(i)
            xRotationSlider = QSlider(Qt.Horizontal)
            lslider.append(xRotationSlider)
            vbox.addWidget( xRotationSlider)
            xRotationSlider.valueChanged.connect(partial(update, n=i))

        
        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()
        self.count=0


    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        self.count += 1
        self.counter.setText(str(self.count))
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

class GUI(threading.Thread):
    def __init__(self, cb, nslider) :
        super().__init__()
        self.queue = queue.Queue(maxsize=50)
        self.cb = cb
        self.nslider = nslider
        pass
    def run(self) :
        EKO()
        app = QApplication(sys.argv)
        self.a = App(self.cb, self.nslider, gui=self)
        self.a.show()
        self.queue.put(1)
        EKO()
        app.exec()
        EKO()
        #os._exit(0)
    def push(self, image) :
        self.a.thread.queue.put(image)

    def go(self) :
        EKO()
        self.start()
        EKO()
        self.queue.get()
        EKO()
        
    def wait(self) :
        EKO()
        time.sleep(9999999)
        EKO()
        self.join()
        EKO()
        while(True) :
            a = self.queue.get()
            EKOX(a)
        
        

donothing = lambda x : 1

def video(cb=donothing, nslider=0) :
    gui = GUI(cb, nslider)
    EKO()
    gui.go()
    EKO()
    return gui

    
if __name__=="__main__":
    def cb(x) :
        EKOX(x)
    gui = video(cb, 3)
    time.sleep(9999999)
    gui.wait()
    
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened():
        success, image = cap.read()
        #EKOX(image is None)
        gui.push(image)
    EKO()

    gui = video(cb, 3)

    
