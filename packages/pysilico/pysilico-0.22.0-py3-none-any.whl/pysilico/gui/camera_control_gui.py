import sys
import numpy as np
from pysilico.gui.image_show_widget.image_show_basic_widget import ColorMaps

import pysilico
from plico.rpc.zmq_remote_procedure_call import ZmqRpcTimeoutError
from pysilico.types.camera_frame import CameraFrame


def _importPyQt5():
    from PyQt5.Qt import QApplication
    from PyQt5 import QtCore
    from PyQt5 import QtWidgets
    from PyQt5 import uic

    def loadUiWidget(uifilename, parent=None):
        return uic.loadUi(uifilename, parent)

    return QApplication, QtCore, QtWidgets, loadUiWidget, QtCore.pyqtSlot


def _importPySide2():
    from PySide2.QtWidgets import QApplication
    from PySide2 import QtCore
    from PySide2 import QtWidgets
    from PySide2 import QtUiTools

    def loadUiWidget(uifilename, parent=None):
        loader = QtUiTools.QUiLoader()
        uifile = QtCore.QFile(uifilename)
        uifile.open(QtCore.QFile.ReadOnly)
        ui = loader.load(uifile, parent)
        uifile.close()
        return ui

    return QApplication, QtCore, QtWidgets, loadUiWidget, QtCore.Slot


def _importQtPy():
    import os
    
    # 211123 workaround for window not showing bug. When can this be removed? Bah...
    # https://stackoverflow.com/questions/64818879/is-there-any-solution-regarding-to-pyqt-library-doesnt-work-in-mac-os-big-sur
    os.environ["QT_MAC_WANTS_LAYER"]='1'

    if "QT_PREFERRED_BINDING" not in os.environ:
        os.environ["QT_PREFERRED_BINDING"] = os.pathsep.join(
            ["PySide2", "PyQt5", "PySide", "PyQt4"]
            #["PyQt5", "PySide2", "PySide", "PyQt4"]
        )

    import Qt
    from Qt.QtWidgets import QApplication
    from Qt import QtCore
    from Qt import QtWidgets
    from Qt import QtCompat
    from Qt.QtCore import Slot

    def loadUiWidget(uifilename, parent=None):
        ui = QtCompat.loadUi(uifile=uifilename, baseinstance=parent)
        return ui

    print("Qt binding %s" % Qt.__binding__)
    print("Qt version %s" % Qt.__qt_version__)
    print("Qt binding version %s" % Qt.__binding_version__)

    return QApplication, QtCore, QtWidgets, loadUiWidget, Slot


#QApplication, QtCore, QtWidgets, loadUiWidget, Slot= _importPySide2()
#QApplication, QtCore, QtWidgets, loadUiWidget, Slot= _importQtPy()
QApplication, QtCore, QtWidgets, loadUiWidget, Slot= _importPyQt5()




class CameraControlGui(QtWidgets.QMainWindow):

    def __init__(self):
        super(CameraControlGui, self).__init__()
        self._camera= pysilico.camera('192.168.1.1', 7100)

        self._lastFrame= CameraFrame(np.zeros((10, 10)), 42)

        self._intervalUpper= 1
        self._intervalRefresh= 500
        self._intervalRefreshCameraStatus= 1000

        self._linesPlot1D= None
        self._imShow2D= None

        self._counterUpper= 0
        self._lastCounterUpper= 0

        from pysilico.gui.camera_control_gui_ui import Ui_MainWindow
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        print(self)
        print(self._ui)
        print(self._ui.imageShowWidget)


        self._setUpConnectButton()
        self._setUpExposureTimeLineEdit()
        self._setUpFrameRateLineEdit()
        self._setUpRequestedBinningComboBox()
        self._setUpSpeedMeter()
        self._setUpCameraStatus()
        self._setUpPlotUpper()


    def keyPressEvent(self, event):
        key = event.key()
        print("event key %s" % str(key))
        if key == QtCore.Qt.Key_Escape:
            self.close()
        if key == QtCore.Qt.Key_S:
            self._timerUpper.stop()
        if key == QtCore.Qt.Key_G:
            self._timerUpper.start()
        super(CameraControlGui, self).keyPressEvent(event)



    def _setUpConnectButton(self):
        self._ui.pushButtonConnectToServer.clicked.connect(
            self._onpushButtonConnectToServerClick)


    def _setUpExposureTimeLineEdit(self):
        self._ui.lineEditRequestedExposureTime.editingFinished.connect(
            self._onlineEditRequestedExposureTimeEditingFinished)


    def _setUpFrameRateLineEdit(self):
        self._ui.lineEditRequestedFramerate.editingFinished.connect(
            self._onlineEditRequestedFrameRateEditingFinished)


    def _setUpRequestedBinningComboBox(self):
        self._ui.comboBoxRequestedBinning.addItems(
            ["1", "2", "3", "4", "8", "16", "32"])
        self._ui.comboBoxRequestedBinning.currentIndexChanged.connect(
            self._oncomboBoxRequestedBinningCurrentIndexChanged)


    @Slot()
    def _onpushButtonConnectToServerClick(self):
        self._camera= pysilico.camera(
            self._ui.lineEditServerHostName.text(),
            int(self._ui.lineEditServerPort.text()))


    @Slot()
    def _onlineEditRequestedExposureTimeEditingFinished(self):
        self._camera.setExposureTime(
            float(self._ui.lineEditRequestedExposureTime.text()))


    @Slot()
    def _onlineEditRequestedFrameRateEditingFinished(self):
        self._camera.setFrameRate(
            float(self._ui.lineEditRequestedFramerate.text()))


    @Slot()
    def _oncomboBoxRequestedBinningCurrentIndexChanged(self):
        self._camera.setBinning(
            int(self._ui.comboBoxRequestedBinning.currentText()))


    def _setUpSpeedMeter(self):
        self._timerSpeedMeter= QtCore.QTimer()
        self._timerSpeedMeter.timeout.connect(self._executeRefreshSpeedMeter)
        self._timerSpeedMeter.start(self._intervalRefresh)


    def _setUpCameraStatus(self):
        self._ui.lineEditCurrentExposureTime.setReadOnly(True)
        self._ui.lineEditCurrentFramerate.setReadOnly(True)
        self._ui.lineEditCurrentBinning.setReadOnly(True)
        self._timerCameraStatus= QtCore.QTimer()
        self._timerCameraStatus.timeout.connect(
            self._executeRefreshCameraStatus)
        self._timerCameraStatus.start(self._intervalRefreshCameraStatus)



    def _refreshSpeed(self, label, counterNow,
                      counterBefore, intervalInMilliSec):
        rate= (counterNow - counterBefore) / intervalInMilliSec * 1e3
        label.setText("Refresh rate: %g Hz" % rate)


    def _executeRefreshSpeedMeter(self):
        self._refreshSpeed(self._ui.labelRefreshRate,
                           self._counterUpper,
                           self._lastCounterUpper,
                           self._intervalRefresh)
        self._lastCounterUpper= self._counterUpper


    def _executeRefreshCameraStatus(self):
        try:
            status= self._camera.getStatus()
            expTime= float(status.exposureTimeInMilliSec)
            frameRate= float(status.frameRate)
            binning= status.binning
            self._ui.lineEditCurrentExposureTime.setText("%.3f" % expTime)
            self._ui.lineEditCurrentFramerate.setText("%.3f" % frameRate)
            self._ui.lineEditCurrentBinning.setText("%.3f" % binning)
            self._ui.labelFrameShape.setText(
                "Frame shape %d x %d" % (status.frameWidth,
                                         status.frameHeight))
        except ZmqRpcTimeoutError:
            pass


    def _tryToGetFrameFromCamera(self):
        try:
            self._lastFrame= self._camera.getFrameForDisplay()
        except ZmqRpcTimeoutError:
            pass


    def _executePlotUpper(self):
        self._tryToGetFrameFromCamera()
        frame= self._lastFrame.toNumpyArray().T
        self._ui.imageShowWidget.setImage(frame)
        self._ui.labelFrameCounter.setText(
            "Frame counter: %d" % self._lastFrame.counter())

        percent= np.percentile(frame, [0, 5, 50, 95, 100])
        self._ui.labelFrameValueMax.setText("Max: %g" % percent[4])
        self._ui.labelFrameValueMin.setText("Min: %g" % percent[0])
        self._ui.labelFrameValue5percentile.setText(
            "5%%: %g" % percent[1])
        self._ui.labelFrameValue95percentile.setText(
            "95%%: %g" % percent[3])
        self._counterUpper+= 1


    def _setUpPlotUpper(self):
        self._ui.imageShowWidget.setBackgroundColor('w')
        self._ui.imageShowWidget.setColormap(ColorMaps.GREY)
        self._ui.imageShowWidget.setImageSaturationValues(
            40, 4000)
        self._ui.imageShowWidget.enableSaturationOverlay(False)


        self._timerUpper= QtCore.QTimer()
        self._timerUpper.timeout.connect(self._executePlotUpper)
        self._timerUpper.start(self._intervalUpper)



class Runner(object):


    def __init__(self):
        pass


    def _setUp(self, argv):
        pass


    def run(self, argv):
        self._setUp(argv)
        qtApp = QApplication(argv)
        self._gui = CameraControlGui()
        self._gui.show()
        qtApp.exec_()


    def terminate(self, signal, frame):
        QApplication.quit()


if __name__ == '__main__':
    runner = Runner()
    sys.exit(runner.run(sys.argv[1:]))



