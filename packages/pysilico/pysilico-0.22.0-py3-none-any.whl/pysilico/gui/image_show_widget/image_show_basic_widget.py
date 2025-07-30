import numpy as np
from pyqtgraph.graphicsItems.ImageItem import ImageItem
from pyqtgraph.graphicsItems.ViewBox import ViewBox
import pyqtgraph as pg
from pyqtgraph.colormap import ColorMap

import os
from numpy import nanmax, nanmin

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui


"""
ImageShowBasicWidget.py -  Widget for basic image dispay and analysis
Copyright 2010  Luke Campagnola
Distributed under MIT/X11 license. See license.txt for more infomation.

Widget used for displaying 2D or 3D data. Features:
  - float or int (including 16-bit int) image display via ImageItem
  - zoom/pan via GraphicsView
  - black/white level controls
  - time slider for 3D data sets
  - ROI plotting
  - Image normalization through a variety of methods
"""


class ColorMaps(object):

    BGYR = 'BGYR'
    BLUE = 'BLUE'
    GREY = 'GREY'
    INV_BLUE = 'INV_BLUE'
    INV_RED = 'INV_RED'
    RED = 'RED'
    SATURATION = 'SATURATION'

    def __init__(self):
        self._createColorMaps()

    def _createColorMapSaturation(self):
        pos = np.array([0.0, 0.1, 0.5, 0.9, 1.0])
        color = np.array([[0, 0, 255, 128],
                          [255, 255, 255, 0],
                          [255, 255, 255, 0],
                          [255, 255, 255, 0],
                          [255, 0, 0, 128]], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 128)
        return lut

    def _createColorMapBGYR(self):
        pos = np.array([0.0, 0.33, 0.66, 1.0])
        color = np.array([[0, 0, 255, 255],
                          [0, 255, 0, 255],
                          [255, 255, 0, 255],
                          [255, 0, 0, 255]], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)
        return lut

    def _createColorMapRed(self):
        pos = np.array([0.0, 1.0])
        color = np.array([[0, 0, 0, 255],
                          [255, 64, 0, 255]], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)
        return lut

    def _createColorMapInvRed(self):
        pos = np.array([0.0, 1.0])
        color = np.array([[255, 64, 0, 64],
                          [255, 255, 255, 64]], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)
        return lut

    def _createColorMapBlue(self):
        pos = np.array([0.0, 1.0])
        color = np.array([[0, 0, 0, 255],
                          [0, 64, 255, 255]], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)
        return lut

    def _createColorMapInvBlue(self):
        pos = np.array([0.0, 1.0])
        color = np.array([[0, 64, 255, 64],
                          [255, 255, 255, 64]], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)
        return lut

    def _createColorMapGrey(self):
        pos = np.array([0.0, 1.0])
        color = np.array([[0, 0, 0, 255],
                          [255, 255, 255, 255]], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)
        return lut

    def _createColorMaps(self):
        self._maps = {}
        self._maps[self.BGYR] = self._createColorMapBGYR()
        self._maps[self.BLUE] = self._createColorMapBlue()
        self._maps[self.GREY] = self._createColorMapGrey()
        self._maps[self.INV_BLUE] = self._createColorMapInvBlue()
        self._maps[self.INV_RED] = self._createColorMapInvRed()
        self._maps[self.RED] = self._createColorMapRed()
        self._maps[self.SATURATION] = self._createColorMapSaturation()

    def get(self, mapName):
        return self._maps[mapName]


class ImageShowBasicWidget(QtWidgets.QWidget):

    def __init__(self,
                 parent=None,
                 name="ImageShowWidget",
                 view=None,
                 imageItem=None,
                 *args):
        super(ImageShowBasicWidget, self).__init__()

        self.name = name
        self.image = None
        self.axes = {}
        self.imageDisp = None
        self._useAutoLevels = True
        self._cursorx = 0
        self._cursory = 0

        from .image_show_basic_widget_ui import Ui_Form
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.scene = self.ui.graphicsView.scene()

        if view is None:
            self.view = ViewBox()
        else:
            self.view = view
        self.ui.graphicsView.setCentralItem(self.view)
        self.view.setAspectLocked(True)
        # self.view.invertY()

        if imageItem is None:
            self.imageItem = ImageItem()
        else:
            self.imageItem = imageItem
        self.view.addItem(self.imageItem)
        self.imageItem.setBorder('k')
        self.imageItem.setLevels([0, 255])

        # wrap functions from view box
        for fn in ['addItem', 'removeItem']:
            setattr(self, fn, getattr(self.view, fn))

        self._colormaps = ColorMaps()
        self.setColormap(ColorMaps.GREY)

        # self._addOverlay()
        self._setupSaturarationOverlay()
        self._setupCrossHairOverlay()
        self._setupMouseMovedSignalProxy()

        self.view.register(self.name)

    def _onMouseMove(self, ev):
        mousePoint = self.view.mapSceneToView(ev[0])
        try:
            szX, szY = self.imageDisp.shape
            self._cursorx = int(np.clip(mousePoint.x(), 0, szX - 1))
            self._cursory = int(np.clip(mousePoint.y(), 0, szY - 1))
            self._updateLabelInfo()
        except Exception:
            pass

    def _updateLabelInfo(self):
        value = self.imageDisp[self._cursorx, self._cursory]
        self.ui.labelInfo.setText(
            "X:%4d Y:%4d I:  %g" % (
                self._cursorx, self._cursory, value))

    def _setupMouseMovedSignalProxy(self):
        self._mouseMoveProxy = pg.SignalProxy(
            self.scene.sigMouseMoved,
            rateLimit=20,
            slot=self._onMouseMove)

    def _setupSaturarationOverlay(self):
        self._wantsSaturationOverlay = False
        self._maxSaturation = np.inf
        self._minSaturation = -np.inf
        self._saturationOverlayImageItem = ImageItem()
        self._saturationOverlayImage = None
        self.view.addItem(self._saturationOverlayImageItem)
        self._saturationOverlayImageItem.setCompositionMode(
            QtGui.QPainter.CompositionMode_SourceOver)
        self._saturationOverlayImageItem.setLookupTable(
            self._colormaps.get(ColorMaps.SATURATION))

    def _setupCrossHairOverlay(self):
        self._crossHairCoords = None
        self._crossHairOverlayImageItem = ImageItem()
        self._crossHairOverlayImage = None
        self.view.addItem(self._crossHairOverlayImageItem)
        self._crossHairOverlayImageItem.setCompositionMode(
            QtGui.QPainter.CompositionMode_Screen)
        self._crossHairOverlayImageItem.setLookupTable(
            self._colormaps.get(ColorMaps.GREY))


#     def _addOverlay(self):
#         self.overlayImageItem = ImageItem()
#         self.view.addItem(self.overlayImageItem)
#         self.overlayImageItem.setCompositionMode(
#             #QtGui.QPainter.CompositionMode_Plus)
#             QtGui.QPainter.CompositionMode_SourceOver)
#             #QtGui.QPainter.CompositionMode_Overlay)
#         overlayImage= np.identity(100)
#         overlayImage[25:75, 25:75]=1
#         self.overlayImageItem.setImage(overlayImage)
#         self.overlayImageItem.setLookupTable(
#                 self._colormaps.get(ColorMaps.INV_BLUE))

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_C:
            print("event key %s: rollColorMap" % str(key))
            self._rollColorMap()
        if key == QtCore.Qt.Key_H:
            self._onCrossHairKeyEvent()
        if key == QtCore.Qt.Key_L:
            self._useAutoLevels = not self._useAutoLevels
            print("event key %s: toggle autolevels %s" % (
                str(key), self._useAutoLevels))
        if key == QtCore.Qt.Key_O:
            self._optimizeLevels()
            print("event key %s: optimize levels " % str(key))
        if key == QtCore.Qt.Key_Q:
            self._wantsSaturationOverlay = not \
                self._wantsSaturationOverlay
            self._updateImage()
        super(ImageShowBasicWidget, self).keyPressEvent(event)

    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            ev.accept()
            print("click on %s" % ev.pos())

    def setColormap(self, colorMapName):
        self.imageItem.setLookupTable(
            self._colormaps.get(colorMapName))
        self._currentColorMapName = colorMapName

    def _onCrossHairKeyEvent(self):
        crossHairCoords = [self._cursorx, self._cursory]
        if self._crossHairCoords is None:
            self._crossHairCoords = crossHairCoords
            print("set cross hair in x:%d y:%d" % (
                self._crossHairCoords[1],
                self._crossHairCoords[0]))
        else:
            self._crossHairCoords = None
            print("delete cross hair")

    def _rollColorMap(self):
        if self._currentColorMapName == ColorMaps.BGYR:
            self.setColormap(ColorMaps.RED)
        elif self._currentColorMapName == ColorMaps.RED:
            self.setColormap(ColorMaps.BLUE)
        elif self._currentColorMapName == ColorMaps.BLUE:
            self.setColormap(ColorMaps.GREY)
        elif self._currentColorMapName == ColorMaps.GREY:
            self.setColormap(ColorMaps.BGYR)

    def _optimizeLevels(self):
        self._useAutoLevels = False
        self.setLevels(self.levelMin, self.levelMax)
        self._updateImage()

    def setBackgroundColor(self, color):
        self.view.setBackgroundColor(color)

    def setOverlayImage(self, overlayImage):
        self.overlayImageItem.setImage(overlayImage)

    def setImageSaturationValues(self,
                                 minSaturation,
                                 maxSaturation):
        self._minSaturation = minSaturation
        self._maxSaturation = maxSaturation

    def enableSaturationOverlay(self, trueOrFalse):
        self._wantsSaturationOverlay = trueOrFalse

    def _showCrossHair(self):
        crossHair = np.ones(self.imageDisp.shape, dtype=np.ubyte) * 0
        if self._crossHairCoords:
            crossHair[self._crossHairCoords[0], :] = 255
            crossHair[:, self._crossHairCoords[1]] = 255
            if not np.array_equal(crossHair, self._crossHairOverlayImage):
                self._crossHairOverlayImageItem.setImage(
                    crossHair, levels=[0, 255])
                self._crossHairOverlayImage = crossHair
        else:
            if self._crossHairOverlayImage is not None:
                self._crossHairOverlayImageItem.clear()
                self._crossHairOverlayImage = None

    def _showSaturationOverlay(self):
        tooMuch = np.ones(self.imageDisp.shape, dtype=np.ubyte) * 127
        if self._wantsSaturationOverlay:
            tooMuch[self.imageDisp > self._maxSaturation] = 255
            tooMuch[self.imageDisp < self._minSaturation] = 0
            if not np.array_equal(tooMuch, self._saturationOverlayImage):
                self._saturationOverlayImageItem.setImage(
                    tooMuch, levels=[0, 255])
                self._saturationOverlayImage = tooMuch
        else:
            if self._saturationOverlayImage is not None:
                self._saturationOverlayImageItem.clear()
                self._saturationOverlayImage = None

    def setImage(self,
                 img,
                 autoRange=True,
                 useAutoLevels=None,
                 levels=None,
                 axes=None,
                 pos=None,
                 scale=None,
                 transform=None,
                 ):
        """
        Set the image to be displayed in the widget.

        ================== ===========================================================================
        **Arguments:**
        img                (numpy array) the image to be displayed. See :func:`ImageItem.setImage` and
                           *notes* below.
        xvals              (numpy array) 1D array of z-axis values corresponding to the third axis
                           in a 3D image. For video, this array should contain the time of each frame.
        autoRange          (bool) whether to scale/pan the view to fit the image.
        useAutoLevels      (bool) whether to update the white/black levels to fit the image.
        levels             (min, max); the white and black level values to use.
        axes               Dictionary indicating the interpretation for each axis.
                           This is only needed to override the default guess. Format is::

                               {'t':0, 'x':1, 'y':2, 'c':3};

        pos                Change the position of the displayed image
        scale              Change the scale of the displayed image
        transform          Set the transform of the displayed image. This option overrides *pos*
                           and *scale*.
        autoHistogramRange If True, the histogram y-range is automatically scaled to fit the
                           image data.
        ================== ===========================================================================

        **Notes:**

        For backward compatibility, image data is assumed to be in column-major order (column, row).
        However, most image data is stored in row-major order (row, column) and will need to be
        transposed before calling setImage()::

            imageview.setImage(imagedata.T)

        This requirement can be changed by the ``imageAxisOrder``
        :ref:`global configuration option <apiref_config>`.

        """

        if hasattr(img, 'implements') and img.implements('MetaArray'):
            img = img.asarray()

        if not isinstance(img, np.ndarray):
            required = ['dtype', 'max', 'min', 'ndim', 'shape', 'size']
            if not all([hasattr(img, attr) for attr in required]):
                raise TypeError("Image must be NumPy array or any object "
                                "that provides compatible attributes/methods:\n"
                                "  %s" % str(required))

        self.image = img
        self.imageDisp = None

        if axes is None:
            x, y = (0, 1) if self.imageItem.axisOrder == 'col-major' else (1, 0)

            if img.ndim == 2:
                self.axes = {'t': None, 'x': x, 'y': y, 'c': None}
            elif img.ndim == 3:
                # Ambiguous case; make a guess
                if img.shape[2] <= 4:
                    self.axes = {'t': None, 'x': x, 'y': y, 'c': 2}
                else:
                    self.axes = {'t': 0, 'x': x + 1, 'y': y + 1, 'c': None}
            elif img.ndim == 4:
                # Even more ambiguous; just assume the default
                self.axes = {'t': 0, 'x': x + 1, 'y': y + 1, 'c': 3}
            else:
                raise Exception(
                    "Can not interpret image with dimensions %s" %
                    (str(img.shape)))
        elif isinstance(axes, dict):
            self.axes = axes.copy()
        elif isinstance(axes, list) or isinstance(axes, tuple):
            self.axes = {}
            for i in range(len(axes)):
                self.axes[axes[i]] = i
        else:
            raise Exception(
                "Can not interpret axis specification %s. "
                "Must be like {'t': 2, 'x': 0, 'y': 1} or "
                "('t', 'x', 'y', 'c')" % (str(axes)))

        for x in ['t', 'x', 'y', 'c']:
            self.axes[x] = self.axes.get(x, None)
        axes = self.axes

        self.currentIndex = 0

        if levels is None and useAutoLevels:
            self._useAutoLevels = useAutoLevels
        # this does nothing since getProcessedImage sets these values again.
        if levels is not None:
            self.setLevels(*levels)

        self._updateImage()
        self._updateLabelInfo()

        self.imageItem.resetTransform()
        if scale is not None:
            self.imageItem.scale(*scale)
        if pos is not None:
            self.imageItem.setPos(*pos)
        if transform is not None:
            self.imageItem.setTransform(transform)

    def setLevels(self, min, max):
        """Set the min/max (bright and dark) levels."""
        self.imageItem.setLevels([min, max])

    def _updateImage(self):
        # Redraw image on screen
        if self.image is None:
            return

        image = self._getProcessedImage()

        # Transpose image into order expected by ImageItem
        if self.imageItem.axisOrder == 'col-major':
            axorder = ['t', 'x', 'y', 'c']
        else:
            axorder = ['t', 'y', 'x', 'c']
        axorder = [self.axes[ax]
                   for ax in axorder if self.axes[ax] is not None]
        image = image.transpose(axorder)

        self.imageItem.setImage(image,
                                autoLevels=self._useAutoLevels)
        self._showSaturationOverlay()
        self._showCrossHair()

    def _getProcessedImage(self):
        """Returns the image data after it has been processed by any normalization options in use.
        This method also sets the attributes self.levelMin and self.levelMax 
        to indicate the range of data in the image."""
        if self.imageDisp is None:
            self.imageDisp = self.image
            self.levelMin, self.levelMax = self._quickLevels(
                self.imageDisp)
            #list( map(float, self._quickLevels(self.imageDisp)))
        return self.imageDisp

    def _quickLevels(self, data):
        """
        Estimate the min/max values of *data* by subsampling.
        """
        while data.size > 1e6:
            ax = np.argmax(data.shape)
            sl = [slice(None)] * data.ndim
            sl[ax] = slice(None, None, 2)
            data = data[sl]
        return self._levelsFromMedianAndStd(data)

    def _levelsFromMinMax(self, data):
        return nanmin(data), nanmax(data)

    def _levelsFrom2And98Percentile(self, data):
        a = np.percentile(data, [3, 97], interpolation='lower')
        return a[0], a[1]

    def _levelsFromMedianAndStd(self, data):
        std = np.std(data)
        median = np.median(data)
        vmin = median - 3 * std
        vmax = median + 3 * std + 1
        return vmin, vmax

    def getView(self):
        """Return the ViewBox (or other compatible object) which displays the ImageItem"""
        return self.view

    def getImageItem(self):
        """Return the ImageItem for this ImageShowWidget."""
        return self.imageItem

    def close(self):
        """Closes the widget nicely, making sure to clear the graphics scene and release memory."""
        self.ui.graphicsView.close()
        self.scene.clear()
        del self.image
        del self.imageDisp
        super(ImageShowBasicWidget, self).close()
        self.setParent(None)
