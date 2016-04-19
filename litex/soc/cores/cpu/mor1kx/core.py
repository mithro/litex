import os

from litex.gen import *

from litex.soc.interconnect import wishbone

_mor1k_dbg_layout = [
    ('ack', 1),
    ('adr', 32),
    ('bp', 1),
    ('dat_ctod', 32),
    ('dat_dtoc', 32),
    ('rst', 1),
    ('stall', 1),
    ('stb', 1),
    ('we', 1),
]

class MOR1KX(Module):
    def __init__(self, platform, reset_pc, debug=False):
        self.ibus = i = wishbone.Interface()
        self.dbus = d = wishbone.Interface()
        self.interrupt = Signal(32)

        ###
        clk = ClockSignal()
        rst = ResetSignal()
        cpu_rst = Signal()

        i_adr_o = Signal(32)
        d_adr_o = Signal(32)

        extra_kw = {}
        if not debug:
            self.comb += cpu_rst.eq(rst)
        else:
            self.debug = debug = Record(_mor1k_dbg_layout)

            self.comb += [
               cpu_rst.eq(rst | debug.rst),
            ]

            extra_kw.update(
                p_FEATURE_DEBUGUNIT="ENABLED",
                i_du_addr_i=debug.adr[:16],
                i_du_dat_i=debug.dat_dtoc,
                i_du_stall_i=debug.stall,
                i_du_stb_i=debug.stb,
                i_du_we_i=debug.we,
                o_du_ack_o=debug.ack,
                o_du_dat_o=debug.dat_ctod,
                o_du_stall_o=debug.bp,
                )

        self.specials += Instance("mor1kx",
                                  p_FEATURE_INSTRUCTIONCACHE="ENABLED",
                                  p_OPTION_ICACHE_BLOCK_WIDTH=4,
                                  p_OPTION_ICACHE_SET_WIDTH=8,
                                  p_OPTION_ICACHE_WAYS=1,
                                  p_OPTION_ICACHE_LIMIT_WIDTH=31,
                                  p_FEATURE_DATACACHE="ENABLED",
                                  p_OPTION_DCACHE_BLOCK_WIDTH=4,
                                  p_OPTION_DCACHE_SET_WIDTH=8,
                                  p_OPTION_DCACHE_WAYS=1,
                                  p_OPTION_DCACHE_LIMIT_WIDTH=31,
                                  p_FEATURE_TIMER="NONE",
                                  p_OPTION_PIC_TRIGGER="LEVEL",
                                  p_FEATURE_SYSCALL="NONE",
                                  p_FEATURE_TRAP="NONE",
                                  p_FEATURE_RANGE="NONE",
                                  p_FEATURE_OVERFLOW="NONE",
                                  p_FEATURE_ADDC="ENABLED",
                                  p_FEATURE_CMOV="ENABLED",
                                  p_FEATURE_FFL1="ENABLED",
                                  p_OPTION_CPU0="CAPPUCCINO",
                                  p_OPTION_RESET_PC=reset_pc,
                                  p_IBUS_WB_TYPE="B3_REGISTERED_FEEDBACK",
                                  p_DBUS_WB_TYPE="B3_REGISTERED_FEEDBACK",
                                  p_OPTION_RF_NUM_SHADOW_GPR=1,

                                  i_clk=clk,
                                  i_rst=cpu_rst,

                                  i_irq_i=self.interrupt,

                                  o_iwbm_adr_o=i_adr_o,
                                  o_iwbm_dat_o=i.dat_w,
                                  o_iwbm_sel_o=i.sel,
                                  o_iwbm_cyc_o=i.cyc,
                                  o_iwbm_stb_o=i.stb,
                                  o_iwbm_we_o=i.we,
                                  o_iwbm_cti_o=i.cti,
                                  o_iwbm_bte_o=i.bte,
                                  i_iwbm_dat_i=i.dat_r,
                                  i_iwbm_ack_i=i.ack,
                                  i_iwbm_err_i=i.err,
                                  i_iwbm_rty_i=0,

                                  o_dwbm_adr_o=d_adr_o,
                                  o_dwbm_dat_o=d.dat_w,
                                  o_dwbm_sel_o=d.sel,
                                  o_dwbm_cyc_o=d.cyc,
                                  o_dwbm_stb_o=d.stb,
                                  o_dwbm_we_o=d.we,
                                  o_dwbm_cti_o=d.cti,
                                  o_dwbm_bte_o=d.bte,
                                  i_dwbm_dat_i=d.dat_r,
                                  i_dwbm_ack_i=d.ack,
                                  i_dwbm_err_i=d.err,
                                  i_dwbm_rty_i=0,

                                  **extra_kw)

        self.comb += [
            self.ibus.adr.eq(i_adr_o[2:]),
            self.dbus.adr.eq(d_adr_o[2:])
        ]

        # add Verilog sources
        vdir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "verilog", "rtl", "verilog")
        platform.add_source_dir(vdir)
