# -*- coding: utf-8 -*-

def classFactory(iface):

    from .IVGA import IVGA
    return IVGA(iface)
