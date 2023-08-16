from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QPoint, QPointF, QT_VERSION_STR
import sys
import os
import image

__author__ = "Minkey"
__version__ = 'v1.0.0'

class Main_window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.control_press = False
        self.image_file_list = []
        for i in range(1, len(sys.argv)):
            self.image_file_list.append(sys.argv[i])
            self.set_image(sys.argv[i])

    def init_ui(self):
        loadUi('main_window.ui', self)
        self.setWindowTitle('ispq - ' + __version__)
        self.setAcceptDrops(True)

        # image
        self.image = image.View()
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.gb_img_view.setLayout(vbox)
        vbox.addWidget(self.image)

    def set_image(self, file_name):
        self.image.set_image(file_name)

    def keyPressEvent(self, event):
        if(event.key() == Qt.Key_Control):
            self.control_press = True
        if(event.key() == Qt.Key_R):
            if self.control_press:
                self.image.reset_all_image()
                
        QMainWindow.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        if(event.key() == Qt.Key_Control):
            self.control_press = False
        QMainWindow.keyReleaseEvent(self, event)

    def quit(self):
        self.close()

    def version(self):
        msg = QMessageBox()
        msg.setWindowTitle('Minview')
        msg.setText('author : ' + __author__ + '\n' + 
                    'version : ' + __version__)
        msg.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main_window()
    main.show()

    sys.exit(app.exec_())