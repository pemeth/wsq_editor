# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ParamWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ParamWindow(object):
    def setupUi(self, ParamWindow):
        ParamWindow.setObjectName("ParamWindow")
        ParamWindow.resize(260, 600)
        self.processingGroup = QtWidgets.QGroupBox(ParamWindow)
        self.processingGroup.setGeometry(QtCore.QRect(10, 10, 243, 351))
        self.processingGroup.setObjectName("processingGroup")
        self.label = QtWidgets.QLabel(self.processingGroup)
        self.label.setGeometry(QtCore.QRect(14, 42, 215, 24))
        self.label.setObjectName("label")
        self.label_4 = QtWidgets.QLabel(self.processingGroup)
        self.label_4.setGeometry(QtCore.QRect(14, 290, 151, 24))
        self.label_4.setObjectName("label_4")
        self.orientSlider = QtWidgets.QSlider(self.processingGroup)
        self.orientSlider.setGeometry(QtCore.QRect(14, 70, 181, 23))
        self.orientSlider.setMinimum(1)
        self.orientSlider.setMaximum(25)
        self.orientSlider.setSingleStep(1)
        self.orientSlider.setPageStep(10)
        self.orientSlider.setProperty("value", 3)
        self.orientSlider.setOrientation(QtCore.Qt.Horizontal)
        self.orientSlider.setInvertedAppearance(False)
        self.orientSlider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.orientSlider.setTickInterval(5)
        self.orientSlider.setObjectName("orientSlider")
        self.label_2 = QtWidgets.QLabel(self.processingGroup)
        self.label_2.setGeometry(QtCore.QRect(14, 233, 111, 24))
        self.label_2.setObjectName("label_2")
        self.gaborSlider = QtWidgets.QSlider(self.processingGroup)
        self.gaborSlider.setGeometry(QtCore.QRect(14, 317, 181, 23))
        self.gaborSlider.setMinimum(2)
        self.gaborSlider.setMaximum(12)
        self.gaborSlider.setSingleStep(1)
        self.gaborSlider.setPageStep(2)
        self.gaborSlider.setProperty("value", 5)
        self.gaborSlider.setSliderPosition(5)
        self.gaborSlider.setOrientation(QtCore.Qt.Horizontal)
        self.gaborSlider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.gaborSlider.setTickInterval(4)
        self.gaborSlider.setObjectName("gaborSlider")
        self.roiSlider = QtWidgets.QSlider(self.processingGroup)
        self.roiSlider.setGeometry(QtCore.QRect(14, 263, 181, 18))
        self.roiSlider.setMinimum(1)
        self.roiSlider.setMaximum(10)
        self.roiSlider.setProperty("value", 1)
        self.roiSlider.setOrientation(QtCore.Qt.Horizontal)
        self.roiSlider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.roiSlider.setTickInterval(1)
        self.roiSlider.setObjectName("roiSlider")
        self.label_3 = QtWidgets.QLabel(self.processingGroup)
        self.label_3.setGeometry(QtCore.QRect(14, 113, 207, 24))
        self.label_3.setObjectName("label_3")
        self.freqSlider = QtWidgets.QSlider(self.processingGroup)
        self.freqSlider.setGeometry(QtCore.QRect(14, 140, 181, 23))
        self.freqSlider.setMaximum(25)
        self.freqSlider.setProperty("value", 8)
        self.freqSlider.setOrientation(QtCore.Qt.Horizontal)
        self.freqSlider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.freqSlider.setTickInterval(5)
        self.freqSlider.setObjectName("freqSlider")
        self.orientValLabel = QtWidgets.QLabel(self.processingGroup)
        self.orientValLabel.setGeometry(QtCore.QRect(205, 70, 31, 24))
        self.orientValLabel.setObjectName("orientValLabel")
        self.gaborValLabel = QtWidgets.QLabel(self.processingGroup)
        self.gaborValLabel.setGeometry(QtCore.QRect(205, 317, 31, 24))
        self.gaborValLabel.setObjectName("gaborValLabel")
        self.roiValLabel = QtWidgets.QLabel(self.processingGroup)
        self.roiValLabel.setGeometry(QtCore.QRect(205, 260, 31, 24))
        self.roiValLabel.setObjectName("roiValLabel")
        self.freqValLabel = QtWidgets.QLabel(self.processingGroup)
        self.freqValLabel.setGeometry(QtCore.QRect(205, 140, 31, 24))
        self.freqValLabel.setObjectName("freqValLabel")
        self.freqBlockSlider = QtWidgets.QSlider(self.processingGroup)
        self.freqBlockSlider.setGeometry(QtCore.QRect(9, 200, 181, 23))
        self.freqBlockSlider.setMinimum(25)
        self.freqBlockSlider.setMaximum(50)
        self.freqBlockSlider.setProperty("value", 36)
        self.freqBlockSlider.setOrientation(QtCore.Qt.Horizontal)
        self.freqBlockSlider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.freqBlockSlider.setTickInterval(5)
        self.freqBlockSlider.setObjectName("freqBlockSlider")
        self.label_7 = QtWidgets.QLabel(self.processingGroup)
        self.label_7.setGeometry(QtCore.QRect(9, 173, 207, 24))
        self.label_7.setObjectName("label_7")
        self.freqValLabel_2 = QtWidgets.QLabel(self.processingGroup)
        self.freqValLabel_2.setGeometry(QtCore.QRect(200, 200, 31, 24))
        self.freqValLabel_2.setObjectName("freqValLabel_2")
        self.overlayGroup = QtWidgets.QGroupBox(ParamWindow)
        self.overlayGroup.setGeometry(QtCore.QRect(10, 360, 241, 172))
        self.overlayGroup.setObjectName("overlayGroup")
        self.label_6 = QtWidgets.QLabel(self.overlayGroup)
        self.label_6.setGeometry(QtCore.QRect(14, 103, 191, 24))
        self.label_6.setObjectName("label_6")
        self.minutiaeSlider = QtWidgets.QSlider(self.overlayGroup)
        self.minutiaeSlider.setGeometry(QtCore.QRect(14, 134, 181, 23))
        self.minutiaeSlider.setMinimum(5)
        self.minutiaeSlider.setMaximum(25)
        self.minutiaeSlider.setProperty("value", 5)
        self.minutiaeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.minutiaeSlider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.minutiaeSlider.setTickInterval(5)
        self.minutiaeSlider.setObjectName("minutiaeSlider")
        self.singularitySlider = QtWidgets.QSlider(self.overlayGroup)
        self.singularitySlider.setGeometry(QtCore.QRect(14, 72, 181, 23))
        self.singularitySlider.setMinimum(8)
        self.singularitySlider.setMaximum(25)
        self.singularitySlider.setOrientation(QtCore.Qt.Horizontal)
        self.singularitySlider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.singularitySlider.setTickInterval(5)
        self.singularitySlider.setObjectName("singularitySlider")
        self.label_5 = QtWidgets.QLabel(self.overlayGroup)
        self.label_5.setGeometry(QtCore.QRect(14, 41, 191, 24))
        self.label_5.setObjectName("label_5")
        self.minutiaeValLabel = QtWidgets.QLabel(self.overlayGroup)
        self.minutiaeValLabel.setGeometry(QtCore.QRect(203, 134, 31, 24))
        self.minutiaeValLabel.setObjectName("minutiaeValLabel")
        self.singularityValLabel = QtWidgets.QLabel(self.overlayGroup)
        self.singularityValLabel.setGeometry(QtCore.QRect(203, 72, 31, 24))
        self.singularityValLabel.setObjectName("singularityValLabel")
        self.paramResetButton = QtWidgets.QPushButton(ParamWindow)
        self.paramResetButton.setGeometry(QtCore.QRect(70, 550, 102, 33))
        self.paramResetButton.setObjectName("paramResetButton")

        self.retranslateUi(ParamWindow)

        # connect sliders to update function
        self.freqSlider.valueChanged.connect(ParamWindow.updateSliderValues)
        self.freqBlockSlider.valueChanged.connect(ParamWindow.updateSliderValues)
        self.orientSlider.valueChanged.connect(ParamWindow.updateSliderValues)
        self.roiSlider.valueChanged.connect(ParamWindow.updateSliderValues)
        self.gaborSlider.valueChanged.connect(ParamWindow.updateSliderValues)
        self.singularitySlider.valueChanged.connect(ParamWindow.updateSliderValues)
        self.minutiaeSlider.valueChanged.connect(ParamWindow.updateSliderValues)

        self.paramResetButton.clicked.connect(ParamWindow.resetValues)

        QtCore.QMetaObject.connectSlotsByName(ParamWindow)

    def retranslateUi(self, ParamWindow):
        _translate = QtCore.QCoreApplication.translate
        ParamWindow.setWindowTitle(_translate("ParamWindow", "Parameter settings"))
        self.processingGroup.setTitle(_translate("ParamWindow", "Image processing"))
        self.label.setText(_translate("ParamWindow", "Orientation blending sigma"))
        self.label_4.setText(_translate("ParamWindow", "Gabor kernel size"))
        self.label_2.setText(_translate("ParamWindow", "ROI threshold"))
        self.label_3.setText(_translate("ParamWindow", "Frequency blending sigma"))
        self.orientValLabel.setText(_translate("ParamWindow", "Val"))
        self.gaborValLabel.setText(_translate("ParamWindow", "Val"))
        self.roiValLabel.setText(_translate("ParamWindow", "Val"))
        self.freqValLabel.setText(_translate("ParamWindow", "Val"))
        self.label_7.setText(_translate("ParamWindow", "Frequency block size"))
        self.freqValLabel_2.setText(_translate("ParamWindow", "Val"))
        self.overlayGroup.setTitle(_translate("ParamWindow", "Image analysis overlay"))
        self.label_6.setText(_translate("ParamWindow", "Minutiae marker size"))
        self.label_5.setText(_translate("ParamWindow", "Singularity marker size"))
        self.minutiaeValLabel.setText(_translate("ParamWindow", "Val"))
        self.singularityValLabel.setText(_translate("ParamWindow", "Val"))
        self.paramResetButton.setText(_translate("ParamWindow", "Reset"))

class ParamWindow(QtWidgets.QMainWindow, Ui_ParamWindow):
    def __init__(self, parent=None):
        super(ParamWindow, self).__init__(parent)
        self.setupUi(self)

        self.orientBlendOrig = self.orientSlider.value()
        self.freqBlendOrig = self.freqSlider.value()
        self.freqBlockOrig = self.freqBlockSlider.value()
        self.roiThreshOrig = self.roiSlider.value()
        self.gaborSizeOrig = self.gaborSlider.value()
        self.singulSizeOrig = self.singularitySlider.value()
        self.minutiaeSizeOrig = self.minutiaeSlider.value()

        self.orientBlend = self.orientBlendOrig
        self.freqBlend = self.freqBlendOrig
        self.freqBlock = self.freqBlockOrig
        self.roiThresh = self.roiThreshOrig / 10 # so the values are floats (0.1 to 1.0)
        self.gaborSize = self.gaborSizeOrig * 2 + 1 # so the slider moves by 2 and lands on odd numbers
        self.singulSize = self.singulSizeOrig
        self.minutiaeSize = self.minutiaeSizeOrig

        self.updateSliderValues()

    def updateSliderValues(self):
        self.orientBlend = self.orientSlider.value()
        self.freqBlend = self.freqSlider.value()
        self.freqBlock = self.freqBlockSlider.value()
        self.roiThresh = self.roiSlider.value() / 10
        self.gaborSize = self.gaborSlider.value() * 2 + 1
        self.singulSize = self.singularitySlider.value()
        self.minutiaeSize = self.minutiaeSlider.value()

        self.updateSliderLabels()

    def updateSliderLabels(self):
        self.orientValLabel.setText(str(self.orientBlend))
        self.freqValLabel.setText(str(self.freqBlend))
        self.freqValLabel_2.setText(str(self.freqBlock))
        self.roiValLabel.setText(str(self.roiThresh))
        self.gaborValLabel.setText(str(self.gaborSize))
        self.singularityValLabel.setText(str(self.singulSize))
        self.minutiaeValLabel.setText(str(self.minutiaeSize))

    def resetValues(self):
        self.orientSlider.setValue(self.orientBlendOrig)
        self.freqSlider.setValue(self.freqBlendOrig)
        self.freqBlockSlider.setValue(self.freqBlockOrig)
        self.roiSlider.setValue(self.roiThreshOrig)
        self.gaborSlider.setValue(self.gaborSizeOrig)
        self.singularitySlider.setValue(self.singulSizeOrig)
        self.minutiaeSlider.setValue(self.minutiaeSizeOrig)

        self.updateSliderValues()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ParamWindow = QtWidgets.QDialog()
    ui = Ui_ParamWindow()
    ui.setupUi(ParamWindow)
    ParamWindow.show()
    sys.exit(app.exec_())
