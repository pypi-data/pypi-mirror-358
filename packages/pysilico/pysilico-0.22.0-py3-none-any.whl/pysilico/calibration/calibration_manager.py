
import os
import astropy.io.fits as pyfits
import numpy as np

from plico.utils.decorator import override, returnsNone, returns, cacheResult
from pysilico.calibration.abstract_calibration_manager import \
    AbstractCalibrationManager
from pysilico.types.camera_frame import CameraFrame
from plico.utils.snapshotable import Snapshotable
from plico.utils.fits_file_based_calibration_manager import \
    FitsFileBasedCalibrationManager


class CalibrationManagerException(Exception):
    pass


class CalibrationManager(AbstractCalibrationManager,
                         FitsFileBasedCalibrationManager):

    def __init__(self, calibrationRootDir):
        self._calibRootDir = calibrationRootDir

    def _checkTag(self, tag, tagPurpose="unspecified"):
        if tag is None:
            raise CalibrationManagerException(
                "A tag (%s) must be given but is None" % tagPurpose)
        if len(tag) == 0:
            raise CalibrationManagerException(
                "A tag name (%s) must be valid but it is '%s'" % (
                    tagPurpose, tag))

    def getDarkFrameFileName(self, tag):
        return os.path.join(self._calibRootDir,
                            "dark_frame", "%s.fits" % tag)

    @override
    @returnsNone
    def saveDarkFrame(
            self, tag, darkCameraFrame, fitsHeader=None):
        self._checkTag(tag, "DarkCameraFrame")
        assert isinstance(darkCameraFrame, CameraFrame)

        fileName = self.getDarkFrameFileName(tag)
        self._createFoldersIfMissing(fileName)
        pyfits.writeto(fileName, darkCameraFrame.toNumpyArray(),
                       fitsHeader,
                       overwrite=False)
        pyfits.append(fileName, np.array([darkCameraFrame.counter()]))

    @override
    @returns(CameraFrame)
    @cacheResult
    def loadDarkFrame(self, tag):
        self._checkTag(tag, "DarkCameraFrame")
        fileName = self.getDarkFrameFileName(tag)
        hdr = pyfits.getheader(fileName)
        hduList = pyfits.open(fileName)
        rawArray = hduList[0].data
        counter = hduList[1].data[0]
        try:
            snapshot = Snapshotable.fromFITSHeader(hdr)
        except Exception:
            snapshot = dict()
        darkCameraFrame = CameraFrame(rawArray, counter)
        return darkCameraFrame
