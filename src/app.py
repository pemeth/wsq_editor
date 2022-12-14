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
from ParamWindow import ParamWindow

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("WSQ Editor")

        self.statusbarLabel = QLabel("No image loaded")
        self.statusbarLabel.setMinimumSize(1,1)
        self.statusbar.addWidget(self.statusbarLabel)

        self.params = ParamWindow(self)
        self.params.show()

        # Create the actions and menus
        self.createActions()
        self.createMenus()

        self.scaleFactor = 1.0

        self.blendSigmaForSingularities = 14

        self.img = None             # Will hold the image data
        self.imgArray = None        # Will hold the raw image data in a numpy array
        self.imgShape = None        # Will hold the shape of the loaded image
        self.currentImage = None    # Will hold the image currently being shown
        self.filename = "/home/"

        self.filtim = None          # Cache for the filtered image
        self.thinned = None         # Cache for the thinned image
        self.cores = None           # Cache for the core singularity image
        self.deltas = None          # Cache for the delta singularity image
        self.bifurcations = None    # Cache for the bifurcation minutiae
        self.ridgeEndings = None    # Cache for the ridge ending minutiae

    def open(self):
        """Open and show an image"""
        options = QFileDialog.Options()

        head, _ = os.path.split(self.filename)
        self.filename, _ = QFileDialog.getOpenFileName(self, "Open Image", head,
                                                  "Images (*.png *.bmp *.jpg *.jpeg *.wsq *.tif);;Any File (*)",
                                                  options=options)

        if self.filename:
            try:
                self.img = Image.open(self.filename)     # Open image with PIL
            except UnidentifiedImageError as e:
                self.showPopup("The selected file is not a supported image file.", detailedMessage=str(e), icon=QMessageBox.Critical)
                self.filename = "/home/"
                return

            self.img = self.img.convert("L")        # Convert to 8bit grayscale
            self.imgArray = np.asarray(self.img)    # Convert image to numpy array
            self.currentImage = self.imgArray.copy()    # Currently shown image as numpy array

            self.imgShape = self.imgArray.shape
            self.showImage(self.imgArray, normalize=False)

            self.scaleFactor = 1.0

            # image is loaded, enable some of the operations
            self.zoomInAction.setEnabled(True)
            self.zoomOutAction.setEnabled(True)
            self.rotateAction.setEnabled(True)
            self.mirrorAction.setEnabled(True)
            self.translateAction.setEnabled(True)
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

    def openParamWindow(self):
        """Shows the parameter window."""
        self.params.show()

    def exportMinutiaeJSON(self):
        """Detects minutiae and exports them into a JSON file."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.", )
            return
        self.showBifurcations()

        norm = normalizeMeanVariance(self.imgArray)
        butter = butterworth(norm)
        orientim = ridgeOrient(butter, blendSigma=self.params.orientBlend)

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

        self.currentImage = img
        self.imgShape = self.currentImage.shape

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
        img = self.currentImage

        img = np.rot90(img)
        self.imgShape = img.shape

        self.showImage(img, normalize=False)

    def mirrorImage(self):
        """Mirror the image along the x axis."""
        img = self.currentImage

        img = np.flip(img, axis=1)
        self.imgShape = img.shape

        self.showImage(img, normalize=False)

    def translateImage(self):
        """Request x and y translation values from the user and translate the image accordingly."""
        img = self.currentImage

        vals, ok = QInputDialog.getText(self, 'Input Dialog', 'Translation values in format x,y:')

        if not ok:
            return

        x, y = 0, 0
        vals = vals.split(",", 1)

        if not len(vals) == 2:
            self.showPopup("Invalid input")
            return

        try:
            x = int(vals[0])
            y = int(vals[1])
        except ValueError:
            self.showPopup("Invalid input")
            return

        params = (1,0,x,0,1,y)

        img = Image.fromarray(img)
        img = img.transform(img.size, Image.AFFINE, params)

        img = np.asarray(img)
        self.showImage(img, normalize=False)

    def showNormalizeMeanVar(self):
        """Show a normalized version of the loaded input image."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.", )
            return

        try:
            norm = normalizeMeanVariance(self.imgArray)
            self.showImage(norm)
        except AttributeError:
            print("An exception occurred! No loaded image found!")

    def showOrientationPlot(self):
        """Plot a vectorfield of the input image orientations in a new window using matplotlib."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        norm = normalizeMeanVariance(self.imgArray)
        orientim = ridgeOrient(norm, blendSigma=self.params.orientBlend, flip=True)

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
        
        norm = normalizeMeanVariance(self.imgArray)
        orientim = ridgeOrient(norm, blendSigma=self.params.orientBlend)
        self.showImage(orientim)

    def showRoi(self):
        """Get the region of interest of the input image and display it."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return
        norm = normalizeMeanVariance(self.imgArray)
        roi = getRoi(norm, threshold=self.params.roiThresh)
        self.showImage(norm * roi)

    def showFrequency(self):
        """Get the frequency image and display it."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return
        norm = normalizeMeanVariance(self.imgArray)
        orientim = ridgeOrient(norm, blendSigma=self.params.orientBlend)
        butter = butterworth(norm)
        freq = ridgeFreq(butter, orientim, blend_sigma=self.params.freqBlend, blocksize=self.params.freqBlock)
        self.showImage(freq)

    def showButterFilter(self):
        """Filter the input image with a Butterworth filter and display it."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        norm = normalizeMeanVariance(self.imgArray)
        butter = butterworth(norm)

        self.showImage(butter)

    def showGaborFilter(self):
        """Calculate a gabor filtered image and display it."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        norm = normalizeMeanVariance(self.imgArray)
        butter = butterworth(norm)
        mask = getRoi(butter, threshold=self.params.roiThresh)
        orientim = ridgeOrient(butter, blendSigma=self.params.orientBlend)
        freq = ridgeFreq(butter, orientim, blend_sigma=self.params.freqBlend, blocksize=self.params.freqBlock)
        self.filtim = gaborFilter(butter, orientim, freq, mask, blocksize=self.params.gaborSize)
        self.showImage(self.filtim)

    def showThinnedZhangSuen(self):
        """Thin the lines in a binary image with the Zhang-Suen method and display it."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        norm = normalizeMeanVariance(self.imgArray)
        butter = butterworth(norm)
        mask = getRoi(butter, threshold=self.params.roiThresh)
        orientim = ridgeOrient(butter, blendSigma=self.params.orientBlend)
        freq = ridgeFreq(butter, orientim, blend_sigma=self.params.freqBlend, blocksize=self.params.freqBlock)
        self.filtim = gaborFilter(butter, orientim, freq, mask, blocksize=self.params.gaborSize)
        self.thinned = zhangSuen((np.invert(self.filtim) * mask).astype(np.float32))
        self.showImage(self.thinned)

    def showSingularities(self):
        """Find the cores of the fingerprint image and display them superimposed over the original image."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        norm = normalizeMeanVariance(self.imgArray)
        mask = getRoi(norm, threshold=self.params.roiThresh)
        orient = ridgeOrient(norm * mask, blendSigma=self.blendSigmaForSingularities)  # better results with masked image
        self.cores, self.deltas = poincare(orient) * mask
        self.cores, self.deltas = singularityCleanup(self.cores, self.deltas, mask)

        overlaid = overlay(self.imgArray, self.cores, "circle", fill="rgb(0,100,200)", outline="rgb(0,100,200)", offset=self.params.singulSize)
        overlaid = overlay(overlaid, self.deltas, "triangle", fill="rgb(0,255,0)", outline="rgb(0,255,0)", offset=self.params.singulSize)
        self.showImage(overlaid, normalize=False)

    def showBifurcations(self):
        """Find the bifurcations of the fingerprint image and display them superimposed over the original image."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return
        
        norm = normalizeMeanVariance(self.imgArray)
        butter = butterworth(norm)
        mask = getRoi(butter, threshold=self.params.roiThresh)
        orientim = ridgeOrient(butter, blendSigma=self.params.orientBlend)
        freq = ridgeFreq(butter, orientim, blend_sigma=self.params.freqBlend, blocksize=self.params.freqBlock)
        self.filtim = gaborFilter(butter, orientim, freq, mask, blocksize=self.params.gaborSize)
        self.thinned = zhangSuen((np.invert(self.filtim) * mask).astype(np.float32))
        self.bifurcations, self.ridgeEndings = extractMinutiae(self.thinned, mask)
        self.showImage(self.bifurcations)

        overlaid = overlay(self.imgArray, self.bifurcations, "square", outline="rgb(0,255,0)", offset=self.params.minutiaeSize)
        self.showImage(overlaid, normalize=False)

    def showRidgeEndings(self):
        """Find the ridge endings of the fingerprint image and display them superimposed over the original image."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        norm = normalizeMeanVariance(self.imgArray)
        butter = butterworth(norm)
        mask = getRoi(butter, threshold=self.params.roiThresh)
        orientim = ridgeOrient(butter, blendSigma=self.params.orientBlend)
        freq = ridgeFreq(butter, orientim, blend_sigma=self.params.freqBlend, blocksize=self.params.freqBlock)
        self.filtim = gaborFilter(butter, orientim, freq, mask, blocksize=self.params.gaborSize)
        self.thinned = zhangSuen((np.invert(self.filtim) * mask).astype(np.float32))
        self.bifurcations, self.ridgeEndings = extractMinutiae(self.thinned, mask)
        self.showImage(self.ridgeEndings)

        overlaid = overlay(self.imgArray, self.ridgeEndings, "circle", outline="rgb(255,0,0)", offset=self.params.minutiaeSize)
        self.showImage(overlaid, normalize=False)

    def showClass(self):
        """Find out the class of the fingerprint and display it in a popup window."""
        if isinstance(self.imgArray, type(None)):
            self.showPopup("No image loaded.", detailedMessage="Load an image through the \"File\" menu.")
            return

        self.showSingularities()

        fpClass = getClass(self.cores, self.deltas)
        self.showPopup("The fingerprint has the class: " + fpClass)

    def createActions(self):
        """Create actions for the application."""
        self.openImageAction = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        self.exportImageAction = QAction("&Export as...", self, shortcut="Ctrl+E", triggered=self.exportImage)
        self.exportImageAction.setEnabled(False)

        self.normalizeImageActionComplex = QAction("Show normalized image", self, shortcut="R", triggered=self.showNormalizeMeanVar)

        self.ridgeOrientImageAction = QAction("Show ridge orientation image", self, triggered=self.showOrientationImage)
        self.ridgeOrientPlotAction = QAction("Show ridge orientation plot", self, triggered=self.showOrientationPlot)

        self.roiAction = QAction("Show region of interest", self, triggered=self.showRoi)
        self.freqAction = QAction("Show frequency image", self, triggered=self.showFrequency)
        self.gaborAction = QAction("Show Gabor filtered image", self, triggered=self.showGaborFilter)
        self.butterAction = QAction("Show Butterworth filtered image", self, triggered=self.showButterFilter)
        self.thinnedZhangSuenAction = QAction("Show thinned image", self, triggered=self.showThinnedZhangSuen)
        self.singularitiesAction = QAction("Show singularities", self, triggered=self.showSingularities)
        self.bifurcationAction = QAction("Show bifurcation minutiae", self, triggered=self.showBifurcations)
        self.ridgeEndingAction = QAction("Show ridge ending minutiae", self, triggered=self.showRidgeEndings)
        self.fpClassAction = QAction("Show class of the fingerprint", self, triggered=self.showClass)
        self.minutiaeExport = QAction("Save minutiae info to minutiae.json", self, triggered=self.exportMinutiaeJSON)

        self.zoomInAction = QAction("Zoom in 1.25x", self, shortcut="+", triggered=self.zoomIn)
        self.zoomInAction.setEnabled(False)
        self.zoomOutAction = QAction("Zoom out 0.8x", self, shortcut="-", triggered=self.zoomOut)
        self.zoomOutAction.setEnabled(False)
        self.rotateAction = QAction("Rotate by 90 degrees", self, shortcut="/", triggered=self.rotateImage)
        self.rotateAction.setEnabled(False)
        self.mirrorAction = QAction("Mirror the image along the x axis", self, shortcut="*", triggered=self.mirrorImage)
        self.mirrorAction.setEnabled(False)
        self.translateAction = QAction("Translate the image...", self, triggered=self.translateImage)
        self.translateAction.setEnabled(False)

        self.openParamWindowAction = QAction("Open the parameter settings", self, shortcut="P", triggered=self.openParamWindow)

    def createMenus(self):
        """Create menubar menus with corresponding actions."""
        self.fileMenu = self.menubar.addMenu("File")
        self.fileMenu.addAction(self.openImageAction)
        self.fileMenu.addAction(self.exportImageAction)

        self.zoomMenu = self.menubar.addMenu("Transformations")
        self.imageMenu = self.menubar.addMenu("Image")
        self.analysisMenu = self.menubar.addMenu("Analysis")
        self.paramsMenu = self.menubar.addMenu("Parameters")

        # zoom menu
        self.zoomMenu.addAction(self.zoomInAction)
        self.zoomMenu.addAction(self.zoomOutAction)
        self.zoomMenu.addAction(self.rotateAction)
        self.zoomMenu.addAction(self.mirrorAction)
        self.zoomMenu.addAction(self.translateAction)

        # normalization submenu
        self.imageMenu.addAction(self.normalizeImageActionComplex)
        
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
        
        # signularities menu option
        self.analysisMenu.addAction(self.singularitiesAction)

        # minutiae submenu
        self.minutiaeSubmenu = self.analysisMenu.addMenu("Minutiae")
        self.minutiaeSubmenu.addAction(self.bifurcationAction)
        self.minutiaeSubmenu.addAction(self.ridgeEndingAction)

        self.analysisMenu.addAction(self.fpClassAction)

        self.analysisMenu.addAction(self.minutiaeExport)

        self.paramsMenu.addAction(self.openParamWindowAction)

    def __checkForLoadedImage(self):
        """Check if an image is loaded."""
        if self.imgArray == None:
            return False
        return True

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
