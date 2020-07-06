import sys
import numpy as np
from PIL import Image, UnidentifiedImageError
import matplotlib.pyplot as plt
import wsq

from normalize import normalizeMeanVariance
from ridge_orientation import ridgeOrient
from region_of_interest import getRoi
from ridge_frequency import ridgeFreq
from filters import gaborFilter
from thinning import zhangSuen
from  singularities import poincare
from minutiae import extractMinutiae

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

        self.filtim = None  # Cache for the filtered image
        self.thinned = None # Cache for the thinned image
        self.cores = None   # Cache for the core singularity image
        self.deltas = None  # Cache for the delta singularity image
        self.bifurcations = None    # Cache for the bifurcation minutiae
        self.ridgeEndings = None    # Cache for the ridge ending minutiae

    def open(self):
        """Open and show an image"""
        options = QFileDialog.Options()
        self.filename, _ = QFileDialog.getOpenFileName(self, "Open Image", "/home",
                                                  "Images (*.png *.bmp *.jpg *.jpeg *.wsq);;Any File (*)",
                                                  options=options)

        if self.filename:
            try:
                self.img = Image.open(self.filename)     # Open image with PIL
            except UnidentifiedImageError as e:
                self.showPopup("The selected file is not a supported image file.", detailedMessage=str(e), icon=QMessageBox.Critical)
                self.filename = None
                return

            self.img = self.img.convert("L")    # Convert to 8bit grayscale
            self.imgArray = np.asarray(self.img)     # Convert image to numpy array
            #imgBytes = self.imgArray.tobytes() # Convert to raw grayscale bytes

            self.imgShape = self.imgArray.shape
            self.showImage(self.imgArray, normalize=False)

            # reset the cached images
            self.filtim = None
            self.thinned = None
            self.cores = None
            self.deltas = None
            self.bifurcations = None
            self.ridgeEndings = None

    def showImage(self, img, normalize=True):
        if normalize:
            img = self.vals2Grayscale(img)

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

    def showNormalizeMeanVar(self):
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.", )
            return

        try:
            self.imgArray = normalizeMeanVariance(self.imgArray)
            self.showImage(self.imgArray)
        except AttributeError:
            print("An exception occurred! No loaded image found!")

    def showOrientationPlot(self):
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        orientim = ridgeOrient(self.imgArray, flip=True)

        # TODO: vymysliet ako zobrazit v mojom "image okne" normalny orientim tak ako cez quiver...
        #       moznost je spravit quiver, ulozit na disk, loadnut a ukazat, ale to je krkolomne

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
    
    def showOrientationImage(self):
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return
        
        orientim = ridgeOrient(self.imgArray)
        self.showImage(orientim)

    def showRoi(self):
        """Get the region of interest of the input image and display it"""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return
        roi = getRoi(self.imgArray)
        self.showImage(roi)

    def showFrequency(self):
        """Get the frequency image and display it"""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return
        norm = normalizeMeanVariance(self.imgArray)
        orientim = ridgeOrient(norm)
        freq = ridgeFreq(norm, orientim)
        self.showImage(freq)

    def showGaborFilter(self):
        """Calculate a gabor filtered image and display it"""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        if not isinstance(self.filtim, type(None)):
            # app has it cached
            self.showImage(self.filtim)
        else:
            norm = normalizeMeanVariance(self.imgArray)
            mask = getRoi(norm)
            orientim = ridgeOrient(norm)
            freq = ridgeFreq(norm, orientim)
            self.filtim = gaborFilter(norm, orientim, freq, mask)
            self.showImage(self.filtim)

    def showThinnedZhangSuen(self):
        """Thin the lines in a binary image with the Zhang-Suen method and display it"""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        if not isinstance(self.thinned, type(None)):
            # app has thinned cached - show it
            self.showImage(self.thinned)
        elif not isinstance(self.filtim, type(None)):
            # app has filtim cached - only thinning needs to be done
            self.thinned = zhangSuen(self.filtim.astype(np.float32))
            self.showImage(self.thinned)
        else:
            # nothing is cached
            norm = normalizeMeanVariance(self.imgArray)
            mask = getRoi(norm)
            orientim = ridgeOrient(norm)
            freq = ridgeFreq(norm, orientim)
            self.filtim = gaborFilter(norm, orientim, freq, mask)
            self.thinned = zhangSuen((np.invert(self.filtim) * mask).astype(np.float32))
            self.showImage(self.thinned)

    def showCores(self):
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        if not isinstance(self.cores, type(None)):
            # cached
            self.showImage(self.cores)
        else:
            mask = getRoi(self.imgArray)
            orient = ridgeOrient(self.imgArray * mask)    # better results with masked image
            self.cores, self.deltas = poincare(orient) * mask
            self.showImage(self.cores)

    def showDeltas(self):
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        if not isinstance(self.deltas, type(None)):
            # cached
            self.showImage(self.deltas)
        else:
            mask = getRoi(self.imgArray)
            orient = ridgeOrient(self.imgArray * mask)    # better results with masked image
            self.cores, self.deltas = poincare(orient) * mask
            self.showImage(self.deltas)

    def showBifurcations(self):
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return
        
        if not isinstance(self.bifurcations, type(None)):
            # app has bifurcations cached - show them
            self.showImage(self.bifurcations)
        elif not isinstance(self.thinned, type(None)):
            # app has thinned cached - extract minutiae
            self.bifurcations, self.ridgeEndings = extractMinutiae(self.thinned)
            self.showImage(self.bifurcations)
        elif not isinstance(self.filtim, type(None)):
            # app has filtim cached - thin and extract minutiae
            self.thinned = zhangSuen(self.filtim.astype(np.float32))
            self.bifurcations, self.ridgeEndings = extractMinutiae(self.thinned)
            self.showImage(self.bifurcations)
        else:
            # nothing is cached
            norm = normalizeMeanVariance(self.imgArray)
            mask = getRoi(norm)
            orientim = ridgeOrient(norm)
            freq = ridgeFreq(norm, orientim)
            self.filtim = gaborFilter(norm, orientim, freq, mask)
            self.thinned = zhangSuen((np.invert(self.filtim) * mask).astype(np.float32))
            self.bifurcations, self.ridgeEndings = extractMinutiae(self.thinned)
            self.showImage(self.bifurcations)

    def showRidgeEndings(self):
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        if not isinstance(self.ridgeEndings, type(None)):
            # app has ridgeEndings cached - show them
            self.showImage(self.ridgeEndings)
        elif not isinstance(self.thinned, type(None)):
            # app has thinned cached - extract minutiae
            self.bifurcations, self.ridgeEndings = extractMinutiae(self.thinned)
            self.showImage(self.ridgeEndings)
        elif not isinstance(self.filtim, type(None)):
            # app has filtim cached - thin and extract minutiae
            self.thinned = zhangSuen(self.filtim.astype(np.float32))
            self.bifurcations, self.ridgeEndings = extractMinutiae(self.thinned)
            self.showImage(self.ridgeEndings)
        else:
            # nothing is cached
            norm = normalizeMeanVariance(self.imgArray)
            mask = getRoi(norm)
            orientim = ridgeOrient(norm)
            freq = ridgeFreq(norm, orientim)
            self.filtim = gaborFilter(norm, orientim, freq, mask)
            self.thinned = zhangSuen((np.invert(self.filtim) * mask).astype(np.float32))
            self.bifurcations, self.ridgeEndings = extractMinutiae(self.thinned)
            self.showImage(self.ridgeEndings)

    def createActions(self):
        """Create actions for the application"""
        self.openImageAction = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)

        self.normalizeImageActionComplex = QAction("Show normalized image with mean/variance method", self, triggered=self.showNormalizeMeanVar)

        self.ridgeOrientImageAction = QAction("Show ridge orientation image", self, triggered=self.showOrientationImage)
        self.ridgeOrientPlotAction = QAction("Show ridge orientation plot", self, triggered=self.showOrientationPlot)

        self.roiAction = QAction("Show region of interest", self, triggered=self.showRoi)
        self.freqAction = QAction("Show frequency image", self, triggered=self.showFrequency)
        self.gaborAction = QAction("Show gabor filtered image", self, triggered=self.showGaborFilter)
        self.thinnedZhangSuenAction = QAction("Show thinned binary image", self, triggered=self.showThinnedZhangSuen)
        self.coresAction = QAction("Show core singularities", self, triggered=self.showCores)
        self.deltasAction = QAction("Show delta singularities", self, triggered=self.showDeltas)
        self.bifurcationAction = QAction("Show bifurcation minutiae", self, triggered=self.showBifurcations)
        self.ridgeEndingAction = QAction("Show ridge ending minutiae", self, triggered=self.showRidgeEndings)

    def createMenus(self):
        """Create menubar menus with corresponding actions"""
        self.fileMenu = self.menubar.addMenu("File")
        self.fileMenu.addAction(self.openImageAction)

        self.imageMenu = self.menubar.addMenu("Image")
        self.analysisMenu = self.menubar.addMenu("Analysis")

        # normalization submenu
        self.normalizeSubmenu = self.imageMenu.addMenu("Normalize")
        self.normalizeSubmenu.addAction(self.normalizeImageActionComplex)
        
        # orientation submenu
        self.ridgeOrientSubmenu = self.imageMenu.addMenu("Ridge orientation")
        self.ridgeOrientSubmenu.addAction(self.ridgeOrientImageAction)
        self.ridgeOrientSubmenu.addAction(self.ridgeOrientPlotAction)

        # main image menu
        self.imageMenu.addAction(self.roiAction)
        self.imageMenu.addAction(self.freqAction)
        self.imageMenu.addAction(self.gaborAction)
        self.imageMenu.addAction(self.thinnedZhangSuenAction)
        
        # signularities submenu        
        self.signularitiesSubmenu = self.analysisMenu.addMenu("Singularities")
        self.signularitiesSubmenu.addAction(self.coresAction)
        self.signularitiesSubmenu.addAction(self.deltasAction)

        # minutiae submenu
        self.minutiaeSubmenu = self.analysisMenu.addMenu("Minutiae")
        self.minutiaeSubmenu.addAction(self.bifurcationAction)
        self.minutiaeSubmenu.addAction(self.ridgeEndingAction)

    def __checkForLoadedImage(self):
        if self.imgArray == None:
            return False
        return True

    def vals2Grayscale(self, vals):
        """Redistribute (normalize) values in parameter `vals` to range of an 8 bit grayscale image.
        This method implicitly converts the `vals` datatype to a float32 for the calculations and
        returns an array of uint8.
        
        Parameters
        ----------
        vals : numpy_array
            An array of values.

        Returns
        -------
            An array of the same size as `vals` with its values normalized to range 0-255.
        """
        vals = np.float32(vals)
        vMin = np.amin(vals)
        vMax = np.amax(vals)
        return np.uint8((vals - vMin) * (255 / (vMax - vMin)))

    def showPopup(self, message, detailedMessage="", icon=QMessageBox.Information):
        """Shows an informative popup window with `message` as it's main text."""
        popup = QMessageBox()
        popup.setWindowTitle("WSQ Editor")
        popup.setText(message)
        popup.setInformativeText(detailedMessage)
        popup.setIcon(icon)
        popup.exec_()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
