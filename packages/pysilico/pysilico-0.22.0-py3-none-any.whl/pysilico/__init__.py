from plico.client.discovery import plico_list, plico_get, plico_client
from pysilico.client.client_map import client_map
from pysilico.client.camera_client import CameraClient
from pysilico.utils.constants import Constants


def _getDefaultConfigFilePath():
    from plico.utils.config_file_manager import ConfigFileManager
    cfgFileMgr= ConfigFileManager(Constants.APP_NAME,
                                  Constants.APP_AUTHOR,
                                  Constants.THIS_PACKAGE)
    return cfgFileMgr.getConfigFilePath()


defaultConfigFilePath= _getDefaultConfigFilePath()


def camera(hostname, port):
    '''Generic CameraClient, kept for backward compatibility'''
    return plico_client(CameraClient, hostname, port)


def list_cameras(timeout_in_seconds=2):
    '''List all available pysilico servers'''
    return plico_list(server_type='pysilico', timeout_in_seconds=timeout_in_seconds)


def get(dm_name, timeout_in_seconds=2):
    '''Get a client for a specific pysilico server'''
    return plico_get(server_type='pysilico', name=dm_name, default_class=CameraClient,
               timeout_in_seconds=timeout_in_seconds, client_map=client_map)
