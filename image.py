from turtle import pos, width
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QPoint, QPointF, QT_VERSION_STR
from PyQt5.QtGui import QImage, QPixmap, QPainterPath, QFont, QColor
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
import keyboard
import numpy as np

resolution_map = {}

resolution_map[4656 * 3496] = [4656,3496]
resolution_map[8192 * 6144] = [8192,6144]
#여기에 resolution을 추가하세요

class View(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.tabs.setTabsClosable(True)
        self.tabs.tabBar().setMouseTracking(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_image)
        self.images = []
        self.is_change = False

    def init_ui(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        self.tabs = QTabWidget()
        vbox.addWidget(self.tabs)

    def reset_all_image(self):
        for image in self.images:
            file_name = image.file_name
            if file_name[-4:] == ".jpg" or file_name[-4:] == ".bmp" or file_name[:-4] == ".png":
                img_array = np.fromfile(file_name, np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            elif file_name[-4:] == ".raw":
                file = open(file_name, 'rb')
                img = np.fromfile(file, dtype='int16', sep="")
                width, height = resolution_map[len(img)]
                img = img.reshape((height,width))
                img = img >> 2
                img = np.uint8(img)
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            image.set_image(img)


    def set_image(self, file_name):
        if file_name[-4:] == ".jpg" or file_name[-4:] == ".bmp" or file_name[-4:] == ".png":
            img_array = np.fromfile(file_name, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif file_name[-4:] == ".raw":
            file = open(file_name, 'rb')
            img = np.fromfile(file, dtype='int16', sep="")
            width, height = resolution_map[len(img)]
            img = img.reshape((height,width))
            img = img >> 2
            img = np.uint8(img)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            print("unsupport")
            exit(-1)

        image = Image()
        image.file_name = file_name
        file_name = file_name.split('\\')[-1]
        file_name = file_name.split('/')[-1]
        image.mouseMoved.connect(self.mouseMoved)
        image.mousePressed.connect(self.mousePressed)
        image.mouseReleased.connect(self.mouseReleased)
        image.wheelPressed.connect(self.wheelPressed)
        self.images.append(image)
        image.set_image(img)
        image.fitInView()
        tab_num = self.tabs.addTab(image, file_name)

    def mouseMoved(self, event):
        for image in self.images:
            image.mouseMoveEventHandler(event)
    def mousePressed(self, event):
        for image in self.images:
            image.mousePressEventHandler(event)
    def mouseReleased(self, event):
        for image in self.images:
            image.mouseReleaseEventHandler(event)
    def wheelPressed(self, event):
        for image in self.images:
            image.wheelEventHandler(event)

    def hasImage(self):
        return self.tabs.isTabEnabled(0)

    def close_image(self):
        index = self.tabs.currentIndex()
        self.tabs.removeTab(index)

    def current_image(self):
        if self.hasImage():
            index = self.tabs.currentIndex()
            return self.images[index]

    def keyPressEvent(self, event):
        tab = -1
        if(event.key() == Qt.Key_1): tab = 0
        if(event.key() == Qt.Key_2): tab = 1
        if(event.key() == Qt.Key_3): tab = 2
        if(event.key() == Qt.Key_4): tab = 3
        if(event.key() == Qt.Key_5): tab = 4
        if(event.key() == Qt.Key_6): tab = 5
        if(event.key() == Qt.Key_7): tab = 6
        if(event.key() == Qt.Key_8): tab = 7
        if(event.key() == Qt.Key_9): tab = 8
        if(event.key() == Qt.Key_0): tab = 9

        center = self.current_image().getCenter()
        for image in self.images:
            image.setCenter(center)
        
        if(self.tabs.isTabEnabled(tab)):
            self.tabs.setCurrentIndex(tab)

        QWidget.keyPressEvent(self, event)
        
class Image(QGraphicsView):
    mouseMoved = pyqtSignal(QtGui.QMouseEvent)
    mousePressed = pyqtSignal(QtGui.QMouseEvent)
    mouseReleased = pyqtSignal(QtGui.QMouseEvent)
    wheelPressed = pyqtSignal(QtGui.QWheelEvent)
    def __init__(self):
        super().__init__()
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.zoom_idx = 0
    
    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            viewrect = self.viewport().rect()
            scenerect = self.transform().mapRect(rect)
            ratio = min(viewrect.width() / scenerect.width(), viewrect.height() / scenerect.height())
            self.scale(ratio, ratio)
            self.zoom_idx = 0

    def set_image(self, image):
        self.image_view = image
        self.height, self.width, self.pattern = image.shape
        self.draw_image()
    
    def draw_image(self):
        qImg = QImage(self.image_view.data, self.width, self.height, self.width * self.pattern, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        
        if pixmap and not pixmap.isNull():
            self._empty = False
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self._photo.setPixmap(QtGui.QPixmap())

    def wheelEventHandler(self, event):
        if event.angleDelta().y() > 0:
            if self.zoom_idx < 30:
                self.zoom_idx = self.zoom_idx + 1
                self.scale(5/4, 5/4)
                self.is_change = True
            else:
                self.is_change = False
        elif event.angleDelta().y() < 0:
            if self.zoom_idx > 0:
                self.zoom_idx = self.zoom_idx - 1
                self.scale(4/5, 4/5)
                self.is_change = True
            else:
                self.is_change = False

    def wheelEvent(self, event):
        if keyboard.is_pressed("ctrl"):
            self.wheelEventHandler(event)
        else:
            self.wheelPressed.emit(event)

    def mouseMoveEventHandler(self, event):
        QGraphicsView.mouseMoveEvent(self, event)

    def mouseMoveEvent(self, event):
        if keyboard.is_pressed("ctrl"):
            self.mouseMoveEventHandler(event)
        else:
            self.mouseMoved.emit(event)

    def mousePressEventHandler(self, event):
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        QGraphicsView.mousePressEvent(self, event)

    def mousePressEvent(self, event):
        if keyboard.is_pressed("ctrl"):
            self.mousePressEventHandler(event)
        else:
            self.mousePressed.emit(event)
    def mouseReleaseEventHandler(self, event):
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
        elif event.button() == Qt.RightButton:
            self.fitInView()
            self.setDragMode(QGraphicsView.NoDrag)
        QGraphicsView.mouseReleaseEvent(self, event)

    def mouseReleaseEvent(self, event):
        if keyboard.is_pressed("ctrl"):
            self.mouseReleaseEventHandler(event)
        else:
            self.mouseReleased.emit(event)

    def setCenter(self, center):
        self.centerOn(center)
    
    def getCenter(self):
        return self.mapToScene(self.rect().center())