import os

from litex.gen import *

from litex.soc.interconnect import wishbone

import enum


class MOR1KX(Module):
    """Wrapped mor1kx CPU.

    We used the 'Cappuccino' version which has;
     * A 6 stage pipeline. (address, fetch, decode, execute, control/memory and
       writeback)
     * Caches supported (optional).
     * MMUs supported (optional).
     * A delay slot on jump and branch instructions.
     * Features the EVBAR.

    Parameters
    ----------
    platform : MiSoC platform object
        The platform to use this module on.

    reset_pc: int
        Address to start executing from after reset.

    mmu : bool or int
        If false disables the MMU. If true the MMUs are enabled using the
        default size. If an int is provided it indicates the number of bytes to
        use for the MMUs.

    cache : bool or int
        If false disables the data and instruction cache.
        If true the data and instruction caches are enabled.
        If an int is provided it indicates the number of bytes to use for the
        caches, a split between the data and instruction cache sizes is
        automatically chosen.

    icache : bool or int
        Size in bytes to use for the instruction cache.
        *Must* not be used at the same time as cache parameter.

    dcache : bool or int
        Size in bytes to use for the data cache.
        *Must* not be used at the same time as cache parameter.

    store_buffer : bool or int
        Size in bytes to use for the output store buffer.
        Enabling means that stores are going through a FIFO and the pipeline is
        not stalled until a load is encountered.

    multiplier : MOR1KX.Multiplier
        Multiplier configuration.

    divider : MOR1KX.Divider
        Divider configuration.

    shifter : MOR1KX.Shifter
        Shifter configuration.

    instructions : tuple of MOR1KX.Instructions
        Optional instructions to enable.


    Attributes
    ----------
    ibus : wishbone.Interface()
        Instruction wishbone bus.

    dbus : wishbone.Interface()
        Data wishbone bus.

    interrupt : Signal(32)
        Interrupt signals.
        FIXME: Why is this 32 bits and not 1 bit?

    """

    class Multiplier(enum.IntEnum):
        """mor1kx Multiplier configuration.

         * Three stage, three cycle, full 32-bit parallel multiplier -- PARALLEL?
         * Pipelined, ??? - multiplier in sync with cpu pipeline
         * Serial, 32-cycle serial multiplication implementation
         * Simulation, single cycle multiplication, not advisable for synthesis
         * None
        """
        NONE = 0
        # Sorted in order of speed
        SERIAL = 1
        PIPELINED = 2
        THREESTAGE = 3
        # Only use in simulation
        SIMULATION = -1

        def compiler_flags(self, compiler):
            """Get compiler flags for this feature."""
            if self != MOR1KX.Multiplier.NONE:
                return ["-mhard-mul"]
            else:
                return ["-msoft-mul"]


    class Divider(enum.IntEnum):
        """mor1kx Divider configuration.

         * Serial, 32-cycle serial division implementation
         * Simulation, single cycle division, not synthesisable
         * None
        """
        NONE = 0
        # Sorted in order of speed
        SERIAL = 1
        # Only use in simulation
        SIMULATION = -1

        def compiler_flags(self, compiler):
            if self != MOR1KX.Divider.NONE:
                return ["-mhard-div"]
            else:
                return ["-msoft-div"]


    class Shifter(enum.IntEnum):
        """mor1kx Divider configuration.

        The shift instructions, logical shift left and right, and shift right
        arithmetic and rotate right can be chosen to be implemented in a
        single-cycle barrel shifter implementation or done serially to save
        implementation area.

         * Barrel, single cycle barrel shifter.
         * Serial, XXX cycle serial shifter.
        """
        # No NONE option - shift instructions are required
        # Sorted in order of speed
        SERIAL = 1
        BARREL = 2
        # In simulation just use BARREL version
        SIMULATION = BARREL

        def compiler_flags(self, compiler):
            """Get compiler flags for this feature."""
            return []


    class Instructions(enum.Enum):
        """
        Optional instructions to enable.
         * ADDC     - Add carry???
         * SRA      - Shift-right-arithmetic
         * ROR      - Rotate right
         * CMOV     - Conditional move
         * FFL1     - Find First/Last '1' -- Can be "REGISTERED" ?
         * EXT      - Zero and sign extension instruction
        """
        ADDC = 'Add carry'
        CMOV = 'Conditional move'
        EXT = 'Zero and sign extension'
        FFL1 = 'Find First/Last \'1\''
        ROR = 'Rotate right'
        SRA = 'Shift-right-arithmetic'

        def compiler_flags(self, compiler):
            """Get compiler flags for this feature."""
            # Which optional instructions are supported by given compilers.
            _compiler_support = {
                "gcc": (ROR, EXT),
                "clang": (ROR, FFL1, ADDC),
            }

            # Check this instruction can be generated by the given compiler.
            if compiler in compiler_support:
                if self not in compiler_support[compiler]:
                    return ""
            else:
                raise TypeError("Unknown compiler {}".format(compiler))

            # For some reason mor1kx uses EXT but everything else use SEXT.
            if self == Instance.EXT:
                flag = "SEXT"
            else:
                flag = self.name.lower()
            return ["-m{}".format(flag)]

# FPU
# -msoft-float
# -mhard-float

#    Flags
#        FEATURE_OVERFLOW
#        FEATURE_CARRY_FLAG
#
#
#
#     * Debug unit
#         `OR1K_SPR_DU_BASE:
#           spr_access[`OR1K_SPR_DU_BASE] = (FEATURE_DEBUGUNIT!="NONE");
#     * Performance counters
#         `OR1K_SPR_PC_BASE:
#           spr_access[`OR1K_SPR_PC_BASE] = (FEATURE_PERFCOUNTERS!="NONE");
#
#    OPTION_TCM_FETCHER -- Only seems to be prontoespresso?

    def __init__(self, platform, reset_pc,
                 ## Memory using features.
                 #mmu=True,
                 #cache=None, icache=None, dcache=None,
                 #store_buffer=True,
                 ## Instructions
                 #multiplier=Multiplier.THREESTAGE,
                 #divider=Divider.SERIAL,
                 #shifter=Shifter.BARREL,
                 #instructions=(Instructions.ADDC, Instructions.CMOV, Instructions.FFL1),

                 # Memory using features.
                 mmu=True,
                 cache=None, icache=None, dcache=None,
                 store_buffer=False,
                 # Instructions
                 multiplier=Multiplier.SERIAL,
                 divider=Divider.SERIAL,
                 shifter=Shifter.SERIAL,
                 instructions=tuple(),
                 ):
        self.ibus = i = wishbone.Interface()
        self.dbus = d = wishbone.Interface()
        self.interrupt = Signal(32)

        ###
        kw = {}

        # Are the MMUs enabled?
        if mmu:
            kw.update(dict(
                    # Instruction MMU
                    p_FEATURE_IMMU                  ="ENABLED",
                    # p_FEATURE_IMMU_HW_TLB_RELOAD  = "NONE",
                    # p_OPTION_IMMU_SET_WIDTH       = 6,
                    # p_OPTION_IMMU_WAYS            = 1,
                    # Data MMU
                    p_FEATURE_DMMU                  = "ENABLED",
                    #p_FEATURE_DMMU_HW_TLB_RELOAD   = "NONE",
                    #p_OPTION_DMMU_SET_WIDTH        = 6,
                    #p_OPTION_DMMU_WAYS             = 1,
                ))
        else:
            kw.update(dict(
                    p_FEATURE_IMMU = "NONE",
                    p_FEATURE_DMMU = "NONE",
                ))

        if cache is not None:
            assert icache is None, "Can not provide both cache and icache args"
            assert dcache is None, "Can not provide both cache and dcache args"

            if cache is True:
                icache = True
                dcache = True
            else:
                # FIXME: Check cache size is valid
                icache = int(cache*0.5) # FIXME: Is 50% split good?
                dcache = cache - icache

        # Is the instruction cache enabled?
        if not icache:
            kw.update(dict(
                    p_FEATURE_INSTRUCTIONCACHE="NONE",
                ))
        else:
            # .OPTION_ICACHE_BLOCK_WIDTH	(4), // 16 insn flop-cache
            kw.update(dict(
                    p_FEATURE_INSTRUCTIONCACHE  = "ENABLED",
                    p_OPTION_ICACHE_BLOCK_WIDTH = 4,
                    p_OPTION_ICACHE_SET_WIDTH   = 8,
                    p_OPTION_ICACHE_WAYS        = 1,
                    p_OPTION_ICACHE_LIMIT_WIDTH = 31,
                ))

        # Is the data cache enabled?
        if not dcache:
            kw.update(dict(
                    p_FEATURE_DATACACHE="NONE",
                ))
        else:
            kw.update(dict(
                    p_FEATURE_DATACACHE         = "ENABLED",
                    p_OPTION_DCACHE_BLOCK_WIDTH = 4,
                    p_OPTION_DCACHE_SET_WIDTH   = 8,
                    p_OPTION_DCACHE_WAYS        = 1,
                    p_OPTION_DCACHE_LIMIT_WIDTH = 31,
                    # p_OPTION_DCACHE_SNOOP     = "NONE",
                ))

        # Stores are going through a fifo and pipeline is not stalled until a
        # load is encountered.
        if store_buffer:
            if store_buffer is True:
                # 4 * 32bit words buffer
                store_buffer = 4 * 4
            assert store_buffer % 4 == 0, "store_buffer must be a multiple of 4 (not %r)" % store_buffer
            kw.update(dict(
                    p_FEATURE_STORE_BUFFER              = "ENABLED",
                    p_OPTION_STORE_BUFFER_DEPTH_WIDTH   = int(store_buffer / 4),
                ))
        else:
            kw.update(dict(
                    p_FEATURE_STORE_BUFFER              = "NONE",
                    p_OPTION_STORE_BUFFER_DEPTH_WIDTH   = 0,
                ))


        # Fast context switching
        #    parameter FEATURE_FASTCONTEXTS	= "NONE",
        #    parameter OPTION_RF_CLEAR_ON_INIT	= 0,
        #    parameter OPTION_RF_NUM_SHADOW_GPR	= 0,
        #    parameter OPTION_RF_ADDR_WIDTH	= 5,
        #    parameter OPTION_RF_WORDS		= 32,

        # Flags and exceptions
        #    parameter FEATURE_SYSCALL		= "ENABLED",
        #    parameter FEATURE_TRAP		= "ENABLED",
        #    parameter FEATURE_RANGE		= "ENABLED",
        #    parameter FEATURE_DSX		= "ENABLED", - Delay-slot exception bit ?
        #    parameter FEATURE_OVERFLOW		= "ENABLED",
        #    parameter FEATURE_CARRY_FLAG	= "ENABLED",

        # Multiple / divide / shifter
        #    parameter FEATURE_MULTIPLIER	= "THREESTAGE",
        #    parameter FEATURE_DIVIDER		= "SERIAL",
        assert isinstance(multiplier, self.Multiplier)
        assert isinstance(divider, self.Divider)
        assert isinstance(shifter, self.Shifter)
        kw.update(dict(
                p_FEATURE_MULTIPLIER    = multiplier.name,
                p_FEATURE_DIVIDER       = divider.name,
                p_OPTION_SHIFTER        = shifter.name,
            ))
        self._multipler = multiplier
        self._divider = divider
        self._shifter = shifter

        # Optional instructions / opcodes
        #    parameter FEATURE_ADDC		= "ENABLED",

        # Shifting instructions
        # * SRA      - Shift-right-arithmetic
        #    parameter FEATURE_SRA		= "ENABLED",

        # * ROR      - Rotate right
        #    parameter FEATURE_ROR		= "NONE",

        # * CMOV     - Conditional move
        #    parameter FEATURE_CMOV		= "ENABLED",

        # * Atomic instructions?
        #    parameter FEATURE_ATOMIC		= "ENABLED",

        # * FFL1     - Find First/Last '1'
        #    parameter FEATURE_FFL1		= "ENABLED",

        # * EXT      - Zero and sign extension instruction
        #    parameter FEATURE_EXT		= "NONE",
        for ins in instructions:
            assert isinstance(ins, MOR1KX.Instructions)
        self._instructions = instructions

        for ins in MOR1KX.Instructions:
            if ins in self._instructions:
                kw["p_FEATURE_{}".format(ins.name)] = "ENABLED"
            else:
                kw["p_FEATURE_{}".format(ins.name)] = "NONE"

        #    parameter FEATURE_CUST1		= "NONE",
        #    parameter FEATURE_CUST2		= "NONE",
        #    parameter FEATURE_CUST3		= "NONE",
        #    parameter FEATURE_CUST4		= "NONE",
        #    parameter FEATURE_CUST5		= "NONE",
        #    parameter FEATURE_CUST6		= "NONE",
        #    parameter FEATURE_CUST7		= "NONE",
        #    parameter FEATURE_CUST8		= "NONE",

        #    parameter FEATURE_STORE_BUFFER	= "ENABLED",
        #    parameter OPTION_STORE_BUFFER_DEPTH_WIDTH = 8,

        # Floating point unit
        #    parameter FEATURE_FPU     = "NONE", // ENABLED|NONE: actual for cappuccino pipeline only

        print("-"*80)
        print("mor1kx config")
        print("-"*80)
        print(kw)
        print("-"*80)

        i_adr_o = Signal(32)
        d_adr_o = Signal(32)
        self.specials += Instance(
            "mor1kx",
            #p_FEATURE_TIMER="NONE",
            p_FEATURE_TIMER="ENABLED",
            p_OPTION_PIC_TRIGGER="LEVEL",

            p_FEATURE_SYSCALL="NONE",
            p_FEATURE_TRAP="NONE",
            p_FEATURE_RANGE="NONE",
            p_FEATURE_OVERFLOW="NONE",

            p_OPTION_CPU0="CAPPUCCINO",
            p_OPTION_RESET_PC=reset_pc,

            i_clk=ClockSignal(),
            i_rst=ResetSignal(),

            i_irq_i=self.interrupt,

            # Instruction wishbone bus
            p_IBUS_WB_TYPE="B3_REGISTERED_FEEDBACK",
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

            # Data wishbone bus
            p_DBUS_WB_TYPE="B3_REGISTERED_FEEDBACK",
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

            **kw)

        self.comb += [
            self.ibus.adr.eq(i_adr_o[2:]),
            self.dbus.adr.eq(d_adr_o[2:])
        ]

        # add Verilog sources
        vdir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "verilog", "rtl", "verilog")
        platform.add_source_dir(vdir)

    @property
    def cpu_type(self):
        return "or1k"

    @property
    def endianness(self):
        return "big"

    def compiler_flags(self, compiler):
        """Compiler flags needed for this CPU core."""
        compiler_flags = []
        compiler_flags += self._multipler.compiler_flags(compiler)
        compiler_flags += self._divider.compiler_flags(compiler)
        compiler_flags += self._shifter.compiler_flags(compiler)

        for ins in self._instructions:
            compiler_flags += ins.compiler_flags(compiler)

        return compiler_flags

    def triple(self, compiler, firmware):
        """Triple for this CPU core with given firmware."""
        if compiler == "clang":
            return "or1k-linux"
        elif compiler == "gcc":
            if firmware == "linux":
                return "or1k-linux"
            return "or1k-elf"

    def linker_output_format(self):
        """Linker output format for this CPU core."""
        return "elf32-or1k"
