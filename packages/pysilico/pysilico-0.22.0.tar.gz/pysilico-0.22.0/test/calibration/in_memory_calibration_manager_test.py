#!/usr/bin/env python

import unittest
import numpy as np
from pysilico.calibration.in_memory_calibration_manager \
    import InMemoryCalibrationManager
from pysilico.types.camera_frame import CameraFrame


__version__= "$Id: in_memory_calibration_manager_test.py 233 2017-01-22 23:38:47Z lbusoni $"


class InMemoryCalibrationManagerTest(unittest.TestCase):

    def setUp(self):
        self.calibMgr= InMemoryCalibrationManager()


    def test_dark_frame_storage(self):
        darkCameraFrameArray=np.arange(100).reshape((10, 10))
        darkCameraFrame= CameraFrame(darkCameraFrameArray)
        self.calibMgr.saveDarkFrame('tagDarkFrame', darkCameraFrame)

        loaded= self.calibMgr.loadDarkFrame("tagDarkFrame")
        self.assertTrue(np.array_equal(
            darkCameraFrame.toNumpyArray(),
            loaded.toNumpyArray()))


if __name__ == "__main__":
    unittest.main()
