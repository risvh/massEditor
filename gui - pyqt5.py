from massEditor import init

init(options=[
    # "regenerate_all",
    # "regenerate_categories",
    # "regenerate_objects",
    # "regenerate_transitions",
    # "regenerate_depths",
    "regenerate_smart",
    ], verbose=True)

from draw import drawObject

img = drawObject(7698)



from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QDialog, QHBoxLayout, QLabel
import sys
from PyQt5.QtGui import QPixmap

class Window(QDialog):
    def __init__(self):
        super().__init__()
        self.title = "PyQt5 Adding Image To Label"
        self.top = 200
        self.left = 500
        self.width = 800
        self.height = 600
        self.InitWindow()
 
    def InitWindow(self):
        # self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        vbox = QHBoxLayout()
        
        # pixmap = QPixmap("112165.png")
        # im2 = img.convert("RGBA")
        # data = im2.tobytes("raw", "BGRA")
        data = img.tobytes("raw", "BGRA")
        qim = QtGui.QImage(data, img.width, img.height, QtGui.QImage.Format_ARGB32)
        pixmap = QtGui.QPixmap.fromImage(qim)
        
        
        labelImage = QLabel(self)
        labelImage.setPixmap(pixmap)
        
        labelImage2 = QLabel(self)
        labelImage2.setPixmap(pixmap)
        
        labelImage3 = QLabel(self)
        labelImage3.setPixmap(pixmap)
        
        vbox.addWidget(labelImage)
        vbox.addWidget(labelImage2)
        vbox.addWidget(labelImage3)
        self.setLayout(vbox)
        self.show()
 
 
 
App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec_())