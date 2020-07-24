"""Main entrypoint to the WSQ Editor application.

Author: Patrik Nemeth
Xlogin: xnemet04
School: Vysoke Uceni Technicke v Brne, Fakulta Informacnich Technologii
"""
import os
import sys
import json
import numpy as np
from PIL import Image, UnidentifiedImageError
import matplotlib.pyplot as plt
try:
    import wsq
except ImportError:
    print("The WSQ image format is not supported. An import error occurred.")
    print("This may happen on Windows machines.")

from normalize import normalizeMeanVariance
from ridge_orientation import ridgeOrient
from region_of_interest import getRoi
from ridge_frequency import ridgeFreq
from filters import gaborFilter, butterworth
from thinning import zhangSuen
from singularities import poincare, singularityCleanup
from minutiae import extractMinutiae
from fp_classes import getClass
from lib import vals2Grayscale, overlay

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QAction, QApplication, QMessageBox, QInputDialog, QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QSize
from MainWindow import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("WSQ Editor")

        self.statusbarLabel = QLabel("No image loaded")
        self.statusbarLabel.setMinimumSize(1,1)
        self.statusbar.addWidget(self.statusbarLabel)

        # Create the actions and menus
        self.createActions()
        self.createMenus()

        self.scaleFactor = 1.0

        self.img = None             # Will hold the image data
        self.imgArray = None        # Will hold the raw image data in a numpy array
        self.imgShape = None        # Will hold the shape of the loaded image
        self.currentImage = None    # Will hold the image currently being shown
        self.filename = None

        self.filtim = None          # Cache for the filtered image
        self.thinned = None         # Cache for the thinned image
        self.cores = None           # Cache for the core singularity image
        self.deltas = None          # Cache for the delta singularity image
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

            self.img = self.img.convert("L")        # Convert to 8bit grayscale
            self.imgArray = np.asarray(self.img)    # Convert image to numpy array

            self.imgShape = self.imgArray.shape
            self.showImage(self.imgArray, normalize=False)

            self.scaleFactor = 1.0

            # image is loaded, enable some of the operations
            self.zoomInAction.setEnabled(True)
            self.zoomOutAction.setEnabled(True)
            self.rotateAction.setEnabled(True)
            self.exportImageAction.setEnabled(True)

            # reset the cached images
            self.filtim = None
            self.thinned = None
            self.cores = None
            self.deltas = None
            self.bifurcations = None
            self.ridgeEndings = None

            self.statusbarLabel.setText("Image: width=" + str(self.imgShape[1]) + ", height=" + str(self.imgShape[0]) + 
                                        "; Filename: " + str(self.filename))
            self.statusbarLabel.setToolTip(self.statusbarLabel.text())

    def exportImage(self):
        """Exports the currently displayed image as a png."""
        try:
            img = vals2Grayscale(self.currentImage)
        except RuntimeWarning:
            self.showPopup("No image exported.", detailedMessage="Cannot export image. An exception occured.")
            return

        img = Image.fromarray(img)

        filename, ok = QInputDialog.getText(self, 'Input Dialog', 'Name of the exported file:')
        head, _ = os.path.split(filename)

        if head != '':
            if not os.path.exists(head):
                self.showPopup("The specified path does not exist.")
                return


        if len(filename) == 0 and ok:
            self.showPopup("No filename specified.")
            return

        filename, ext = os.path.splitext(filename)

        if ext == '':
            ext = ".png"

        if ok:
            try:
                img.save(str(filename) + ext)
            except ValueError:
                self.showPopup("File extension not recognised.")
                return
            except IOError:
                self.showPopup("An IO error occurred.", "This may happen when saving an RGB image in a non-RGB format, such as WSQ.")
                return

    def exportMinutiaeJSON(self):
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.", )
            return
        self.__runAll() # get minutiae

        norm = normalizeMeanVariance(self.imgArray)
        butter = butterworth(norm)
        orientim = ridgeOrient(butter)

        with open("minutiae.json", "w") as f:
            bifIdx = np.nonzero(self.bifurcations)
            endIdx = np.nonzero(self.ridgeEndings)

            orientim = (orientim * 180/np.pi).astype(np.int)    # radians to degrees
            orientim = np.where(orientim == 180, 0, orientim)   # 180 degrees = 0 degrees

            bifOrient = orientim[bifIdx]
            endOrient = orientim[endIdx]

            typedict = {
                "bifurcations" : [],
                "ridgeEndings" : []
            }

            # save the minutiae x and y positions and their angle (not direction!) to a dictionary
            x,y,angle = 0,1,2
            for bifs,ends in zip(zip(bifIdx[1], bifIdx[0], bifOrient), zip(endIdx[1], endIdx[0], endOrient)):
                typedict["bifurcations"].append({
                    "X" : int(bifs[x]),
                    "Y" : int(bifs[y]),
                    "angle" : int(bifs[angle])
                })
                typedict["ridgeEndings"].append({
                    "X" : int(ends[x]),
                    "Y" : int(ends[y]),
                    "angle" : int(ends[angle])
                })

            # dump the dictionary as a json
            json.dump(typedict, f)

    def showImage(self, img, normalize=True):
        """Shows an image in the main window."""
        if normalize:
            img = vals2Grayscale(img)

        imgBytes = img.tobytes()

        # calculate number of bytes per line in the image
        bytesPerLine = (self.imgShape[1] * self.imgShape[0]) / self.imgShape[0]

        # check if image is grayscale or RGB and convert to QImage
        if len(img.shape) == 2:
            # convert raw bytes to 8bit grayscale QImage to be able to render it
            self.img = QImage(imgBytes, self.imgShape[1], self.imgShape[0],
                                bytesPerLine, QImage.Format_Grayscale8)
        else:
            # the image is RGB, so 3 times as many bytes per line
            bytesPerLine *= 3
            self.img = QImage(imgBytes, self.imgShape[1], self.imgShape[0], bytesPerLine, QImage.Format_RGB888)

        if self.img.isNull():
            QMessageBox.information(self, "Editor", "Cannot load %s." % self.filename)
            return

        # scale the mainImage label size to image and show the image
        self.mainImage.setPixmap(QPixmap.fromImage(self.img).scaled(QSize(self.imgShape[1], self.imgShape[0]),
                                                                    Qt.KeepAspectRatio,
                                                                    Qt.FastTransformation))

        self.mainImage.resize(self.mainImage.pixmap().size())
        #self.mainImage.adjustSize()
        self.scrollArea.setVisible(True)
        self.scaleImage(1)

    def scaleImage(self, factor):
        """Scales the image and the containing QLabel to a resized image by `factor`."""
        # prevent from scaling to over half or twice the size
        if ((factor < 1.0 and self.scaleFactor >= 0.5) or
            (factor > 1.0 and self.scaleFactor <= 2.0)):
            self.scaleFactor *= factor

        self.mainImage.resize(self.scaleFactor * self.mainImage.pixmap().size())

    def zoomIn(self):
        """Callback for the `zoomInAction` QAction. Calls `scaleImage` with a constant 1.25 zoom factor."""
        self.scaleImage(1.25)

    def zoomOut(self):
        """Callback for the `zoomOutAction` QAction. Calls `scaleImage` with a constant 0.8 zoom factor."""
        self.scaleImage(0.8)

    def rotateImage(self):
        """Rotate the image counter-clockwise."""
        #TODO rotating some images skews them, don't know why
        if self.img.format() == QImage.Format_RGB888:
            channels = 3
        else:
            channels = 1

        s = self.img.bits().asstring(self.imgShape[0] * self.imgShape[1] * channels)
        
        if channels == 3:
            img = np.fromstring(s, dtype=np.uint8).reshape((self.imgShape[0], self.imgShape[1], channels))
        else:
            img = np.fromstring(s, dtype=np.uint8).reshape((self.imgShape[0], self.imgShape[1]))

        img = img.astype(np.uint8)

        img = np.rot90(img)
        self.imgShape = img.shape

        self.showImage(img, normalize=False)

    def showNormalizeMeanVar(self):
        """Show a normalized version of the loaded input image."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.", )
            return

        try:
            norm = normalizeMeanVariance(self.imgArray)
            self.showImage(norm)
            self.currentImage = norm
        except AttributeError:
            print("An exception occurred! No loaded image found!")

    def showOrientationPlot(self):
        """Plot a vectorfield of the input image orientations in a new window using matplotlib."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        orientim = ridgeOrient(self.imgArray, flip=True)

        orientim = np.rot90(np.rot90(orientim)) # rotate the orientation image by 180 degrees, because quiver shows it upside down

        spacing = 7
        orientim = orientim[spacing:self.imgShape[0] - spacing:spacing, spacing:self.imgShape[1] - spacing:spacing]

        # deconstruct the orientation image into its horizontal and vertical components
        u = 2 * np.cos(orientim)
        v = 2 * np.sin(orientim)

        quiveropts = dict(color='red', headlength=0, pivot='middle', headaxislength=0,
                          linewidth=.9, units='xy', width=.05, headwidth=1)

        # create a subplot and use quiver() to visualize the data
        fig, ax = plt.subplots()
        ax.set_axis_off()
        ax.quiver(u, v, **quiveropts)
        plt.show()
    
    def showOrientationImage(self):
        """Show a grayscale representation of the orientations of the input image."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return
        
        orientim = ridgeOrient(self.imgArray)
        self.showImage(orientim)
        self.currentImage = orientim

    def showRoi(self):
        """Get the region of interest of the input image and display it."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return
        roi = getRoi(self.imgArray)
        self.showImage(roi)
        self.currentImage = roi

    def showFrequency(self):
        """Get the frequency image and display it."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return
        norm = normalizeMeanVariance(self.imgArray)
        orientim = ridgeOrient(norm)
        freq = ridgeFreq(norm, orientim)
        self.showImage(freq)
        self.currentImage = freq

    def showButterFilter(self):
        """Filter the input image with a Butterworth filter and display it."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        norm = normalizeMeanVariance(self.imgArray)
        butter = butterworth(norm)

        self.showImage(butter)
        self.currentImage = butter

    def showGaborFilter(self):
        """Calculate a gabor filtered image and display it."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        if not isinstance(self.filtim, type(None)):
            # app has it cached
            self.showImage(self.filtim)
        else:
            norm = normalizeMeanVariance(self.imgArray)
            butter = butterworth(norm)
            mask = getRoi(butter)
            orientim = ridgeOrient(butter)
            freq = ridgeFreq(butter, orientim)
            self.filtim = gaborFilter(butter, orientim, freq, mask)
            self.showImage(self.filtim)
        self.currentImage = self.filtim

    def showThinnedZhangSuen(self):
        """Thin the lines in a binary image with the Zhang-Suen method and display it."""
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
            butter = butterworth(norm)
            mask = getRoi(butter)
            orientim = ridgeOrient(butter)
            freq = ridgeFreq(butter, orientim)
            self.filtim = gaborFilter(butter, orientim, freq, mask)
            self.thinned = zhangSuen((np.invert(self.filtim) * mask).astype(np.float32))
            self.showImage(self.thinned)
        self.currentImage = self.thinned

    def showCores(self):
        """Find the cores of the fingerprint image and display them superimposed over the original image."""
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
            self.cores, self.deltas = singularityCleanup(self.cores, self.deltas, mask)
            self.showImage(self.cores)

        overlaid = overlay(self.imgArray, self.cores, "circle", fill="rgb(0,100,200)", outline="rgb(0,100,200)", offset=6)
        self.showImage(overlaid, normalize=False)
        self.currentImage = overlaid

    def showDeltas(self):
        """Find the deltas of the fingerprint image and display them superimposed over the original image."""
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
            self.cores, self.deltas = singularityCleanup(self.cores, self.deltas, mask)
            self.showImage(self.deltas)

        overlaid = overlay(self.imgArray, self.deltas, "triangle", fill="rgb(100,0,100)", outline="rgb(100,0,100)", offset=6)
        self.showImage(overlaid, normalize=False)
        self.currentImage = overlaid

    def showBifurcations(self):
        """Find the bifurcations of the fingerprint image and display them superimposed over the original image."""
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
            butter = butterworth(norm)
            mask = getRoi(butter)
            orientim = ridgeOrient(butter)
            freq = ridgeFreq(butter, orientim)
            self.filtim = gaborFilter(butter, orientim, freq, mask)
            self.thinned = zhangSuen((np.invert(self.filtim) * mask).astype(np.float32))
            self.bifurcations, self.ridgeEndings = extractMinutiae(self.thinned)
            self.showImage(self.bifurcations)

        overlaid = overlay(self.imgArray, self.bifurcations, "square", outline="rgb(0,255,0)")
        self.showImage(overlaid, normalize=False)
        self.currentImage = overlaid

    def showRidgeEndings(self):
        """Find the ridge endings of the fingerprint image and display them superimposed over the original image."""
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
            butter = butterworth(norm)
            mask = getRoi(butter)
            orientim = ridgeOrient(butter)
            freq = ridgeFreq(butter, orientim)
            self.filtim = gaborFilter(butter, orientim, freq, mask)
            self.thinned = zhangSuen((np.invert(self.filtim) * mask).astype(np.float32))
            self.bifurcations, self.ridgeEndings = extractMinutiae(self.thinned)
            self.showImage(self.ridgeEndings)
        
        overlaid = overlay(self.imgArray, self.ridgeEndings, "circle", outline="rgb(255,0,0)")
        self.showImage(overlaid, normalize=False)
        self.currentImage = overlaid

    def showClass(self):
        """Find out the class of the fingerprint and display it in a popup window."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        if isinstance(self.deltas, type(None)):
            # not cached
            mask = getRoi(self.imgArray)
            orient = ridgeOrient(self.imgArray * mask)    # better results with masked image
            self.cores, self.deltas = poincare(orient) * mask
            self.cores, self.deltas = singularityCleanup(self.cores, self.deltas, mask)

        fpClass = getClass(self.cores, self.deltas)
        self.showPopup("The fingerprint has the class: " + fpClass)

    def autoAnalysis(self):
        """Run all of the algorithms and cache the results of the slow algorithms, so they can be accessed again with no speed penalty."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        self.__runAll()
        self.showPopup("Complete!", detailedMessage="Analysis outputs are cached.")

    def createActions(self):
        """Create actions for the application."""
        self.openImageAction = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        self.exportImageAction = QAction("&Export as...", self, shortcut="Ctrl+E", triggered=self.exportImage)
        self.exportImageAction.setEnabled(False)

        self.normalizeImageActionComplex = QAction("Show normalized image with mean/variance method", self, triggered=self.showNormalizeMeanVar)

        self.ridgeOrientImageAction = QAction("Show ridge orientation image", self, triggered=self.showOrientationImage)
        self.ridgeOrientPlotAction = QAction("Show ridge orientation plot", self, triggered=self.showOrientationPlot)

        self.roiAction = QAction("Show region of interest", self, triggered=self.showRoi)
        self.freqAction = QAction("Show frequency image", self, triggered=self.showFrequency)
        self.gaborAction = QAction("Show Gabor filtered image", self, triggered=self.showGaborFilter)
        self.butterAction = QAction("Show Butterworth filtered image", self, triggered=self.showButterFilter)
        self.thinnedZhangSuenAction = QAction("Show thinned binary image", self, triggered=self.showThinnedZhangSuen)
        self.coresAction = QAction("Show core singularities", self, triggered=self.showCores)
        self.deltasAction = QAction("Show delta singularities", self, triggered=self.showDeltas)
        self.bifurcationAction = QAction("Show bifurcation minutiae", self, triggered=self.showBifurcations)
        self.ridgeEndingAction = QAction("Show ridge ending minutiae", self, triggered=self.showRidgeEndings)
        self.fpClassAction = QAction("Show class of the fingerprint", self, triggered=self.showClass)
        self.autoAnalysisAction = QAction("Run all", self, triggered=self.autoAnalysis)
        self.minutiaeExport = QAction("Save minutiae info to minutiae.json", self, triggered=self.exportMinutiaeJSON)

        self.zoomInAction = QAction("Zoom in 1.25x", self, shortcut="+", triggered=self.zoomIn)
        self.zoomInAction.setEnabled(False)
        self.zoomOutAction = QAction("Zoom out 0.8x", self, shortcut="-", triggered=self.zoomOut)
        self.zoomOutAction.setEnabled(False)
        self.rotateAction = QAction("Rotate by 90 degrees", self, shortcut="/", triggered=self.rotateImage)
        self.rotateAction.setEnabled(False)

    def createMenus(self):
        """Create menubar menus with corresponding actions."""
        self.fileMenu = self.menubar.addMenu("File")
        self.fileMenu.addAction(self.openImageAction)
        self.fileMenu.addAction(self.exportImageAction)

        self.zoomMenu = self.menubar.addMenu("Transformations")
        self.imageMenu = self.menubar.addMenu("Image")
        self.analysisMenu = self.menubar.addMenu("Analysis")

        # zoom menu
        self.zoomMenu.addAction(self.zoomInAction)
        self.zoomMenu.addAction(self.zoomOutAction)
        self.zoomMenu.addAction(self.rotateAction)

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
        self.imageMenu.addAction(self.butterAction)
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

        self.analysisMenu.addAction(self.fpClassAction)

        self.analysisMenu.addAction(self.autoAnalysisAction)
        self.analysisMenu.addAction(self.minutiaeExport)

    def __checkForLoadedImage(self):
        """Check if an image is loaded."""
        if self.imgArray == None:
            return False
        return True

    def __runAll(self):
        """Run all of the algorithms."""
        norm = normalizeMeanVariance(self.imgArray)
        butter = butterworth(norm)
        mask = getRoi(butter)
        orientim = ridgeOrient(butter)
        freq = ridgeFreq(butter, orientim)

        # check cache; if not cached run algorithm
        if isinstance(self.filtim, type(None)):
            self.filtim = gaborFilter(butter, orientim, freq, mask)
        if isinstance(self.thinned, type(None)):
            self.thinned = zhangSuen((np.invert(self.filtim) * mask).astype(np.float32))
        if isinstance(self.bifurcations, type(None)):
            self.bifurcations, self.ridgeEndings = extractMinutiae(self.thinned)
        if isinstance(self.cores, type(None)):
            orient = ridgeOrient(butter * mask)
            self.cores, self.deltas = poincare(orient) * mask

    def showPopup(self, message, detailedMessage="", icon=QMessageBox.Information):
        """Shows an informative popup window with `message` as it's main text."""
        popup = QMessageBox()
        popup.setWindowTitle("WSQ Editor")
        popup.setText(message)
        popup.setInformativeText(detailedMessage)
        popup.setIcon(icon)
        popup.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
