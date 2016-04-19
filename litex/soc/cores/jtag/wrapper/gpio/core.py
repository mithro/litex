import os
from litex.gen import *
from litex.soc.cores.jtag import interface

class JTAG(Module):
    def __init__(self, platform, pads=interface.Port()):
        clk = ClockSignal()

        self.pad = pads
        self.tap = tap = interface.TAP()

        if not hasattr(pads, 'trst'):
            trst = Signal(1, reset=0)
        else:
            trst = pads.trst

        self.specials += Instance(
            "tap_top",
            # Port
	    i_tms_pad_i=pads.tms,
	    i_tck_pad_i=pads.tck,
	    i_trstn_pad_i=trst,
	    i_tdi_pad_i=pads.tdi,
	    o_tdo_pad_o=pads.tdo,
	    #o_tdo_padoe_o=,
 
	    # TAP states
	    o_test_logic_reset_o=tap.reset,
	    o_run_test_idle_o=tap.idle,
	    o_shift_dr_o=tap.shift,
	    o_pause_dr_o=tap.pause, 
	    o_update_dr_o=tap.update,
	    o_capture_dr_o=tap.capture,
 
	    # Select signals for boundary scan or mbist
	    #i_extest_select_o=,
	    #i_sample_preload_select_o=,
	    #i_mbist_select_o=,
	    o_debug_select_o=tap.select,
 
	    # TDO signal that is connected to TDI of sub-modules
	    o_tdi_o=tap.tdi,
 
	    # TDI signals from sub-modules
	    i_debug_tdo_i=tap.tdo,    # from debug module
	    i_bs_chain_tdo_i=0,       # from Boundary Scan Chain
	    i_mbist_tdo_i=0,          # from Mbist Chain
        )

        # add Verilog sources
        vdir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "..", "..", "adv_debug_sys", "verilog", "Hardware", "jtag", "tap", "rtl", "verilog")
        platform.add_source_dir(vdir)
