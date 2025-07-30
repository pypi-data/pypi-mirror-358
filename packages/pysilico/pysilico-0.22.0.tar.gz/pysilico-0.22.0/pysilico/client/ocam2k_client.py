#!/usr/bin/env python

from pysilico.client.camera_client import CameraClient
from pysilico.utils.timeout import Timeout


class Ocam2kClient(CameraClient):

    def __init__(self, rpcHandler, sockets):
        super().__init__(rpcHandler, sockets)

    def get_emgain(self, timeoutInSec=Timeout.GENERIC_COMMAND):
        return self._rpcHandler.sendRequest(
            self.request_socket,
            'get_emgain', [],
            timeout=timeoutInSec)

