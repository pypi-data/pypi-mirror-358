import abc
from six import with_metaclass
import numpy as np
from plico.utils.decorator import returnsNone, returns, returnsForExample
from pysilico.types.camera_frame import CameraFrame
from pysilico.types.camera_status import CameraStatus


class SnapshotEntry(object):
    EXPOSURE_TIME_MS= "EXPOSURE_TIME_MS"
    FRAME_WIDTH_PX= "WIDTH_PX"
    FRAME_HEIGHT_PX= "HEIGHT_PX"
    CAMERA_NAME= 'NAME'
    BINNING= "BINNING"
    PARAMETERS="PARAMETERS"


class MultipleFrameRetriever():

    @classmethod
    def _getAveragedFutureFrames(cls, nFramesToAverage, frameRetriever):
        a= []
        for _ in range(nFramesToAverage):
            frame= frameRetriever()
            a.append(frame.toNumpyArray())

        arr=np.dstack([x for x in a])
        lastCounter= frame.counter()
        return np.mean(arr, axis=2), lastCounter


    @classmethod
    def _getCube(cls, nFrames, nFramesToAverage, frameRetriever):
        a= []
        for _ in range(nFrames):
            frame, lastCounter= cls._getAveragedFutureFrames(nFramesToAverage,
                                                             frameRetriever)
            a.append(frame)

        arr=np.dstack([x for x in a])
        return arr, lastCounter

    @classmethod
    def getFrames(cls,
                  numberOfReturnedImages,
                  numberOfFramesToAverageForEachImage,
                  frameRetriever):
        cube, lastCounter= cls._getCube(
            numberOfReturnedImages,
            numberOfFramesToAverageForEachImage,
            frameRetriever)
        frame = CameraFrame.fromNumpyArray(cube.squeeze())
        frame.setCounter(lastCounter)
        return frame


class AbstractCameraClient(with_metaclass(abc.ABCMeta, object)):

    @abc.abstractmethod
    @returns(CameraFrame)
    def getFrameForDisplay(self):
        assert False


    @abc.abstractmethod
    @returns(CameraFrame)
    def getFutureFrames(self,
                        numberOfReturnedImages,
                        numberOfFramesToAverageForEachImage):
        assert False


    @abc.abstractmethod
    @returnsNone
    def setExposureTime(self, exposureTimeInMilliSeconds):
        assert False


    @abc.abstractmethod
    @returns(float)
    def exposureTime(self):
        assert False


    @abc.abstractmethod
    @returnsForExample((1024, 1024))
    def shape(self):
        assert False


    @abc.abstractmethod
    @returnsForExample({'WFS_CAMERA.EXPOSURE_TIME_MS': 10})
    def getSnapshot(self, prefix):
        assert False


    @abc.abstractmethod
    @returnsNone
    def setBinning(self, binning):
        assert False


    @abc.abstractmethod
    @returns(int)
    def getBinning(self):
        assert False


    @abc.abstractmethod
    @returns(CameraStatus)
    def getStatus(self):
        assert False


    @abc.abstractmethod
    @returnsNone
    def setFrameRate(self, frameRate):
        assert False


    @abc.abstractmethod
    @returns(float)
    def getFrameRate(self):
        assert False


    @abc.abstractmethod
    @returns(CameraFrame)
    def getDarkFrame(self):
        assert False


    @abc.abstractmethod
    def setDarkFrame(self, darkFrame):
        assert False

    @abc.abstractmethod
    def setParameter(self, name, value):
        '''Device-specific parameters'''
        assert False

