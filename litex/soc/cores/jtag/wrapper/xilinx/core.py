import os
from litex.gen import *
from litex.soc.cores.jtag import interface

class JTAG(Module):
    def __init__(self, platform):
        clk = ClockSignal()

        self.tap = tap = interface.TAP()
        self.specials += Instance(
            "xilinx_internal_jtag",
            o_tck_o=tap.tck,
            i_debug_tdo_i=tap.tdo,
            o_tdi_o=tap.tdi,
            o_test_logic_reset_o=tap.reset,
            o_run_test_idle_o=tap.idle,
            o_shift_dr_o=tap.shift,
            o_capture_dr_o=tap.capture,
            o_pause_dr_o=tap.pause,
            o_update_dr_o=tap.update,
            o_debug_select_o=tap.select,
        )

        # add Verilog sources
        vdir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "..", "..", "adv_debug_sys",
            "verilog", "Hardware", "xilinx_internal_jtag",
            "rtl", "verilog",
            )
        platform.add_source_dir(vdir)
