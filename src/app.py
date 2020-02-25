import sys
from PIL import Image
from PIL.ImageQt import ImageQt
import wsq
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMenu, QAction, QApplication, QMessageBox,\
                            QScrollArea, QSizePolicy
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

    def open(self):
        """Open and show an image"""
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Open Image", "/home", '',
                                                  "Images (*.png *.bmp *.jpg *.jpeg *.wsq)",
                                                  options=options)

        if filename:
            self.img = Image.open(filename)      # Open image with PIL
            self.img = self.img.convert("L")     # Convert to 8bit grayscale
            data = self.img.tobytes("raw", "L")  # Convert to raw grayscale bytes

            # Calculate number of bytes per line in the image
            bytesPerLine = (self.img.size[0] * self.img.size[1]) / self.img.size[1]

            # Convert raw bytes to 8bit grayscale QImage to be able to render it
            self.img = QImage(data, self.img.size[0], self.img.size[1], bytesPerLine, QImage.Format_Grayscale8)

            if self.img.isNull():
                QMessageBox.information(self, "Editor", "Cannot load %s." % filename)
                return

            # Scale image to the mainImage label size and show the image
            self.mainImage.setPixmap(QPixmap.fromImage(self.img).scaled(self.mainImage.size(),
                                                                   Qt.KeepAspectRatio, Qt.FastTransformation))

    def createActions(self):
        self.openImageAction = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)

    def createMenus(self):
        self.fileMenu = self.menubar.addMenu("File")
        self.fileMenu.addAction(self.openImageAction)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
