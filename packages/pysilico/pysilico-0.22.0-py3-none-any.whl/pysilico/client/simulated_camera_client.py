from pysilico.client.abstract_camera_client import AbstractCameraClient,\
    MultipleFrameRetriever, SnapshotEntry
from plico.utils.decorator import override, returns
from pysilico.types.camera_frame import CameraFrame
from plico.utils.snapshotable import Snapshotable
from pysilico.types.camera_status import CameraStatus
from pysilico_server.devices.simulated_auxiliary_camera import \
    SimulatedAuxiliaryCamera



class SimulatedCameraClient(AbstractCameraClient):

    def __init__(self):
        self._name= 'mySimulatedCamera'
        self._cameraDevice= SimulatedAuxiliaryCamera(self._name)
        self._frameToReturn= None
        self._darkFrame= None


    def deinitialize(self):
        self._cameraDevice.stopAcquisition()
        self._cameraDevice.deinitialize()


    def frameCounter(self):
        return self._cameraDevice.frameCounter()


    def simulateCameraFrame(self, cameraFrameToReturn):
        self._frameToReturn= cameraFrameToReturn


    @override
    @returns(CameraFrame)
    def getFrameForDisplay(self):
        return CameraFrame(self._cameraDevice.readFrame())


    def _getCorrectedFrame(self):
        return CameraFrame(self._cameraDevice.readFrame())


    @override
    @returns(CameraFrame)
    def getFutureFrames(self,
                        numberOfReturnedImages,
                        numberOfFramesToAverageForEachImage=1):
        if self._frameToReturn is not None:
            return self._frameToReturn
        else:
            return MultipleFrameRetriever.getFrames(
                numberOfReturnedImages,
                numberOfFramesToAverageForEachImage,
                self._getCorrectedFrame)


    @override
    def setExposureTime(self, exposureTimeInMilliSeconds):
        self._cameraDevice.setExposureTime(exposureTimeInMilliSeconds)


    @override
    def exposureTime(self):
        return self._cameraDevice.exposureTime()


    @override
    def shape(self):
        return (self._cameraDevice.rows(), self._cameraDevice.cols())


    @override
    def getSnapshot(self, prefix):
        snapshot= {}
        snapshot[SnapshotEntry.EXPOSURE_TIME_MS]= self.exposureTime()
        snapshot[SnapshotEntry.FRAME_WIDTH_PX]= self._cameraDevice.cols()
        snapshot[SnapshotEntry.FRAME_HEIGHT_PX]= self._cameraDevice.rows()
        return Snapshotable.prepend(prefix, snapshot)



    @override
    def setBinning(self, binning):
        self._cameraDevice.setBinning(binning)


    @override
    def getBinning(self):
        return self._cameraDevice.getBinning()


    def simulatePupilCenterInUnbinnedPixels(self, center):
        self._cameraDevice.setPupilsCenterInUnbinnedPixels(center)


    def simulatePupilsRadiusInUnbinnedPixels(self, radius):
        self._cameraDevice.setPupilsRadiusInUnbinnedPixels(radius)


    def simulateNoiseInCount(self, noise):
        self._cameraDevice.setNoiseInCount(noise)


    def simulateTilt(self, z2and3Coefficients):
        self._cameraDevice.setTilt(z2and3Coefficients)


    @override
    @returns(CameraStatus)
    def getStatus(self):
        status= CameraStatus(self._name,
                             self._cameraDevice.cols(),
                             self._cameraDevice.rows(),
                             self._cameraDevice.dtype(),
                             self.getBinning(),
                             self.exposureTime())
        return status

    @override
    def setParameter(self, name, value):
        '''We don't have any'''
        raise Exception('Parameter %s is not valid' % str(name))


    @override
    def setFrameRate(self, frameRate):
        self._cameraDevice.setFrameRate(frameRate)


    @override
    def getFrameRate(self):
        return self._cameraDevice.getFrameRate()

    @override
    @returns(CameraFrame)
    def getDarkFrame(self):
        return self._darkFrame

    @override
    def setDarkFrame(self, darkFrame):
        self._darkFrame= darkFrame
