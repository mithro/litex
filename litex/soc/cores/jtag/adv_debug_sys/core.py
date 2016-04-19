import os

from litex.gen import *

from litex.soc.interconnect import wishbone
from litex.soc.cores.jtag import interface


class AdvancedDebugSystem(Module):
    def __init__(self, platform, cpu, jtag):
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

        # JTAG TAP interface
        self.specials += Instance(
            "adbg_top",
            # CPU Interface
            i_cpu0_clk_i=clk,
            i_cpu0_ack_i=cpu.debug.ack,
            i_cpu0_bp_i=cpu.debug.bp,
            i_cpu0_data_i=cpu.debug.dat_ctod,
            o_cpu0_addr_o=cpu.debug.adr,
            o_cpu0_data_o=cpu.debug.dat_dtoc,
            o_cpu0_rst_o=cpu.debug.rst,
            o_cpu0_stall_o=cpu.debug.stall,
            o_cpu0_stb_o=cpu.debug.stb,
            o_cpu0_we_o=cpu.debug.we,

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

            # JTAG TAP
            i_tck_i=jtag.tap.tck,
            i_tdi_i=jtag.tap.tdi,
            o_tdo_o=jtag.tap.tdo,
            i_rst_i=jtag.tap.reset,
            i_capture_dr_i=jtag.tap.capture,
            i_shift_dr_i=jtag.tap.shift,
            i_pause_dr_i=jtag.tap.pause,
            i_update_dr_i=jtag.tap.update,
            i_debug_select_i=jtag.tap.select,
        )

        vdir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "verilog", "Hardware", "adv_dbg_if",
            "rtl", "verilog")
        platform.add_source_dir(vdir)
