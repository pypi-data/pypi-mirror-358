import abc
from six import with_metaclass
from plico.utils.decorator import returnsNone, returns
from pysilico.types.camera_frame import CameraFrame


class AbstractCalibrationManager(with_metaclass(abc.ABCMeta, object)):


    @abc.abstractmethod
    @returnsNone
    def saveDarkFrame(self, tag, darkCameraFrame):
        assert False


    @abc.abstractmethod
    @returns(CameraFrame)
    def loadDarkFrame(self, tag):
        assert False
