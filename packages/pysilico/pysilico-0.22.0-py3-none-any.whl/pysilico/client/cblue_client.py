#!/usr/bin/env python

from pysilico.client.camera_client import CameraClient
from pysilico.utils.timeout import Timeout


class CBlueClient(CameraClient):

    def __init__(self, rpcHandler, sockets):
        super().__init__(rpcHandler, sockets)

    def set_pixel_format(self, pixel_format, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'set_pixel_format', [pixel_format],
            timeout=timeoutInSec)

    def get_pixel_format(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'get_pixel_format', [],
            timeout=timeoutInSec)
    
    def set_rows(self, rows, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'set_rows', [rows],
            timeout=timeoutInSec)
    
    def get_rows(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'rows', [],
            timeout=timeoutInSec)
    
    def get_rows_max(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'get_rows_max', [],
            timeout=timeoutInSec)

    def set_cols(self, cols, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'set_cols', [cols],
            timeout=timeoutInSec)
    
    def get_cols(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'cols', [],
            timeout=timeoutInSec)
    
    def get_cols_max(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'get_cols_max', [],
            timeout=timeoutInSec)

    def set_cooling_setpoint(self, set_point, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'set_device_cooling_setpoint', [set_point],
            timeout=timeoutInSec)
    
    def get_cooling_setpoint(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'get_device_cooling_setpoint', [],
            timeout=timeoutInSec)
    
    def set_conversion_efficiency(self, conv_eff, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'set_conversion_efficiency', [conv_eff],
            timeout=timeoutInSec)
    
    def get_conversion_efficiency(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'get_conversion_efficiency', [],
            timeout=timeoutInSec)

    def set_gain(self, gain, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'set_gain', [gain],
            timeout=timeoutInSec)
    
    def get_gain(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'get_gain', [],
            timeout=timeoutInSec)

    def set_framerate(self, framerate, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'setFrameRate', [framerate],
            timeout=timeoutInSec)
    
    def get_framerate(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'getFrameRate', [],
            timeout=timeoutInSec)
    
    def get_framerate_min(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'getFrameRateMin', [],
            timeout=timeoutInSec)
    
    def get_framerate_max(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self._requestSocket,
            'getFrameRateMax', [],
            timeout=timeoutInSec)

