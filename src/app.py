import sys
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import wsq

from normalize import normalizeMinMax, normalizeMeanVariance
import ridge_orientation as ro

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
            self.showImage(self.imgArray)

    def normalizeMinMax(self):
        try:
            self.imgArray = normalizeMinMax(self.imgArray)
            self.showImage(self.vals2Grayscale(self.imgArray))
        except AttributeError:
            print("An exception occurred! No loaded image found!")

    def normalizeMeanVar(self):
        try:
            self.imgArray = normalizeMeanVariance(self.imgArray)
            self.showImage(self.vals2Grayscale(self.imgArray))
        except AttributeError:
            print("An exception occurred! No loaded image found!")

    def showImage(self, img):
        imgBytes = img.tobytes()

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

    def showOrientation(self):
        # TODO: check for a loaded image
        orientim = ro.getOrientationImage(self.imgArray)

        # TODO: vymysliet ako zobrazit v mojom "image okne" normalny orientim tak ako cez quiver...
        #       moznost je spravit quiver, ulozit na disk, loadnut a ukazat, ale to je krkolomne
        self.showImage(self.vals2Grayscale(orientim))

        orientim = np.rot90(np.rot90(orientim)) # Rotate the orientation image by 180 degrees, because quiver shows it upside down

        spacing = 7
        orientim = orientim[spacing:self.imgShape[0] - spacing:spacing, spacing:self.imgShape[1] - spacing:spacing]

        # Deconstruct the orientation image into its horizontal and vertical components
        u = 2 * np.cos(orientim)
        v = 2 * np.sin(orientim)

        quiveropts = dict(color='red', headlength=0, pivot='middle', headaxislength=0,
                          linewidth=.9, units='xy', width=.05, headwidth=1)

        # Create a subplot and use quiver() to visualize the data
        fig, ax = plt.subplots()
        ax.set_axis_off()
        ax.quiver(u, v, **quiveropts)
        plt.show()

    def createActions(self):
        """Create actions for the application"""
        self.openImageAction = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)

        # TODO: prerobit nejak ten triggered callback, aby sa volala jedna funkcia ale s parametrami na rozlisenie sposobu normalizacie
        #       mozno pomoze: https://www.mfitzp.com/article/qt-transmit-extra-data-with-signals/
        self.normalizeImageActionSimple = QAction("Normalize with min/max method", self, triggered=self.normalizeMinMax)
        self.normalizeImageActionComplex = QAction("Normalize with mean/variance method", self, triggered=self.normalizeMeanVar)

        self.ridgeOrientAction = QAction("Show ridge orientation", self, triggered=self.showOrientation)

    def createMenus(self):
        """Create menubar menus with corresponding actions"""
        self.fileMenu = self.menubar.addMenu("File")
        self.fileMenu.addAction(self.openImageAction)

        self.imageMenu = self.menubar.addMenu("Image")
        self.normalizeSubmenu = self.imageMenu.addMenu("Normalize")
        #self.ridgeOrientSubmenu = self.imageMenu.addMenu("Ridge orientation")

        self.normalizeSubmenu.addAction(self.normalizeImageActionSimple)
        self.normalizeSubmenu.addAction(self.normalizeImageActionComplex)
        self.imageMenu.addAction(self.ridgeOrientAction)

    def __checkForLoadedImage(self):
        if self.imgArray == None:
            return False
        return True

    def vals2Grayscale(self, vals):
        """Redistribute (normalize) values in parameter `vals` to range of an 8 bit grayscale image.
        
        Parameters
        ----------
        vals : numpy_array
            An array of values.

        Returns
        -------
            An array of the same size as `vals` with its values normalized to range 0-255.
        """
        vMin = np.amin(vals)
        vMax = np.amax(vals)
        return np.uint8((vals - vMin) * (255 / (vMax - vMin)))



app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
