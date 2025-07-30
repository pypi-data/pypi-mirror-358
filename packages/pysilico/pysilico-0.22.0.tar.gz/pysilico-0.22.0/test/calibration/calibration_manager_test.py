#!/usr/bin/env python
import os
import unittest
import shutil

import numpy as np
import astropy.io.fits as pyfits
from pysilico.calibration.calibration_manager import CalibrationManager
from pysilico.types.camera_frame import CameraFrame


class CalibrationManagerTest(unittest.TestCase):

    CALIB_DIR = "./calib_tmp"

    def _removeCalibrationDir(self):
        if os.path.exists(self.CALIB_DIR):
            shutil.rmtree(self.CALIB_DIR)

    def setUp(self):
        self._removeCalibrationDir()
        self.calibMgr = CalibrationManager(self.CALIB_DIR)

    def tearDown(self):
        self._removeCalibrationDir()

    def test_storage_of_dark_frame(self):
        hdr = pyfits.Header()
        hdr.update({"zzz": 42})

        darkCameraFrameArray = np.arange(100).reshape((10, 10))
        darkCameraFrame = CameraFrame(darkCameraFrameArray)
        self.calibMgr.saveDarkFrame('tagDarkFrame', darkCameraFrame, hdr)
        self.assertTrue(os.path.exists(
            os.path.join(self.CALIB_DIR, "dark_frame",
                         "tagDarkFrame.fits")))

        loaded = self.calibMgr.loadDarkFrame("tagDarkFrame")
        self.assertTrue(np.array_equal(
            darkCameraFrame.toNumpyArray(),
            loaded.toNumpyArray()))


if __name__ == "__main__":
    unittest.main()
