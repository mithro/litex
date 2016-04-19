import os
from litex.gen import *
from litex.soc.cores.jtag import interface
from litex.soc.cores.jtag.wrapper.gpio import core

class JTAG(core.JTAG):
    def __init__(self, platform):
        core.JTAG.__init__(self, platform, pads=platform.request("jtag"))

        # add C++ sources
        cppdir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "software")
        platform.add_source(os.path.join(cppdir, "jtagServer.h"), language="cpp")
        platform.add_source(os.path.join(cppdir, "jtagServer.cpp"), language="cpp")
