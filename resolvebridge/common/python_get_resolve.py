#!/usr/bin/env python

"""
This file serves to return a DaVinci Resolve object
"""
import sys

def get_resolve():
    """ Get the DaVinci Resolve API endpoint
    """
    ext = ".so"
    if sys.platform.startswith("darwin"):
        path = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/"
    elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
        path = "C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\"
        ext = ".dll"
    elif sys.platform.startswith("linux"):
        path = "/opt/resolve/libs/Fusion/"
    else:
        raise Exception("Unsupported system! " + sys.platform)

    import imp

    bmd = imp.load_dynamic("fusionscript", path + "fusionscript" + ext)
    resolve = bmd.scriptapp("Resolve")

    if resolve:
        sys.modules[__name__] = resolve
    else:
        raise ImportError("Could not locate module dependencies")

    return bmd.scriptapp("Resolve")