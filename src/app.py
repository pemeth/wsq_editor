import sys
import numpy as np
from PIL import Image
import wsq
from normalize import normalize
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMenu, QAction, QApplication, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPalette
from PyQt5.QtCore import Qt
from MainWindow import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("WSQ Editor")

        # Create the actions and menus
        self.createActions()
        self.createMenus()

        self.img = None     # Will hold the image data
        self.imgArray = None    # Will hold the raw image data in a numpy array
        self.imgShape = None    # Will hold the shape of the loaded image
        self.filename = None

    def open(self):
        """Open and show an image"""
        options = QFileDialog.Options()
        self.filename, _ = QFileDialog.getOpenFileName(self, "Open Image", "/home", '',
                                                  "Images (*.png *.bmp *.jpg *.jpeg *.wsq)",
                                                  options=options)

        if self.filename:
            self.img = Image.open(self.filename)     # Open image with PIL
            self.img = self.img.convert("L")    # Convert to 8bit grayscale
            self.imgArray = np.asarray(self.img)     # Convert image to numpy array
            #imgBytes = self.imgArray.tobytes() # Convert to raw grayscale bytes

            self.imgShape = self.imgArray.shape
            self.showImage()

    def normalize(self):
        self.imgArray = normalize(self.imgArray)
        self.showImage()

    def showImage(self):
        imgBytes = self.imgArray.tobytes()

        # Calculate number of bytes per line in the image
        bytesPerLine = (self.imgShape[1] * self.imgShape[0]) / self.imgShape[0]

        # Convert raw bytes to 8bit grayscale QImage to be able to render it
        self.img = QImage(imgBytes, self.imgShape[1], self.imgShape[0],
                            bytesPerLine, QImage.Format_Grayscale8)

        if self.img.isNull():
            QMessageBox.information(self, "Editor", "Cannot load %s." % self.filename)
            return

        # Scale image to the mainImage label size and show the image
        self.mainImage.setPixmap(QPixmap.fromImage(self.img).scaled(self.mainImage.size(),
                                                                    Qt.KeepAspectRatio,
                                                                    Qt.FastTransformation))

    def createActions(self):
        """Create actions for the application"""
        self.openImageAction = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)

        self.normalizeImageAction = QAction("Normalize", self, triggered=self.normalize)

    def createMenus(self):
        """Create menubar menus with corresponding actions"""
        self.fileMenu = self.menubar.addMenu("File")
        self.fileMenu.addAction(self.openImageAction)

        self.imageMenu = self.menubar.addMenu("Image")
        self.imageMenu.addAction(self.normalizeImageAction)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
