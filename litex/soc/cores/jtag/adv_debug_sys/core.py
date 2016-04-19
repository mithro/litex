import os

from litex.gen import *

from litex.soc.interconnect import wishbone
from litex.soc.cores.jtag import interface


class AdvancedDebugSystem(Module):
    def __init__(self, platform, cpu):
        # Currently we only support the mor1kx processor

        # Enable the debug interface on the processor
        clk = ClockSignal()
        rst = ResetSignal()

        # The adb is a wishbone master
        self.wb = wb = wishbone.Interface()
        wb_adr_o = Signal(32)
        self.comb += [
            wb.adr.eq(wb_adr_o[2:]),
        ]

        # JTAG interface
        self.jtag = j = interface.Extended()

        self.specials += Instance(
            "adbg_top",
            i_cpu0_clk_i=clk,
            o_cpu0_rst_o=cpu.debug.rst,
            o_cpu0_addr_o=cpu.debug.adr,
            o_cpu0_data_o=cpu.debug.dat,
            o_cpu0_stb_o=cpu.debug.stb,
            o_cpu0_we_o=cpu.debug.we,
            i_cpu0_data_i=cpu.debug.dat,
            i_cpu0_ack_i=cpu.debug.ack,
            o_cpu0_stall_o=cpu.debug.stall,
            i_cpu0_bp_i=cpu.debug.bp,

            # TAP interface
            i_tck_i=j.tck,
            i_tdi_i=j.tdi,
            o_tdo_o=j.tdo,
            i_rst_i=j.trst,
            i_capture_dr_i=j.capture,
            i_shift_dr_i=j.shift,
            i_pause_dr_i=j.pause,
            i_update_dr_i=j.update,
            i_debug_select_i=j.tms,

            # Wishbone debug master
            i_wb_clk_i=clk,
            i_wb_dat_i=wb.dat_r,
            i_wb_ack_i=wb.ack,
            i_wb_err_i=wb.err,

            o_wb_adr_o=wb_adr_o,
            o_wb_dat_o=wb.dat_w,
            o_wb_sel_o=wb.sel,
            o_wb_cyc_o=wb.cyc,
            o_wb_stb_o=wb.stb,
            o_wb_we_o=wb.we,
            o_wb_cti_o=wb.cti,
            o_wb_bte_o=wb.bte,
        )

        self.specials += Instance(
            "xilinx_internal_jtag",
            o_tck_o=j.tck,
            i_debug_tdo_i=j.tdo,
            o_tdi_o=j.tdi,
            o_test_logic_reset_o=j.trst,
            o_run_test_idle_o=j.idle,
            o_shift_dr_o=j.shift,
            o_capture_dr_o=j.capture,
            o_pause_dr_o=j.pause,
            o_update_dr_o=j.update,
            o_debug_select_o=j.tms,
        )

        vdir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "verilog", "Hardware", "adv_dbg_if",
            "rtl", "verilog")
        platform.add_source_dir(vdir)

        vdir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "verilog", "Hardware", "xilinx_internal_jtag",
            "rtl", "verilog")
        platform.add_source_dir(vdir)
