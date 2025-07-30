
from plico.utils.decorator import override, returns, returnsNone
from pysilico.calibration.abstract_calibration_manager import \
    AbstractCalibrationManager
from pysilico.types.camera_frame import CameraFrame



class InMemoryCalibrationManager(AbstractCalibrationManager):

    def __init__(self):
        self._darkFrameDict= {}


    @override
    @returnsNone
    def saveDarkFrame(
            self, tag, darkCameraFrame):
        assert isinstance(darkCameraFrame, CameraFrame)
        self._darkFrameDict[tag]= darkCameraFrame


    @override
    @returns(CameraFrame)
    def loadDarkFrame(self, tag):
        return self._darkFrameDict[str(tag)]
