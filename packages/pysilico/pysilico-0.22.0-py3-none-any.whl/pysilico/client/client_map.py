'''
Mapping from camera type string to a module/class
that can act as a specialized client for that DM type
'''
from plico.client.discovery import ClientMapType


client_map = {
   'Ocam2k': ClientMapType(modulename='pysilico.client.ocam2k_client', classname='Ocam2kClient'),
   'CblueOneCamera': ClientMapType(modulename='pysilico.client.cblue_client', classname='CBlueClient'),
}
