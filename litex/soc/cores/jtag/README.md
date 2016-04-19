This directory contains code for integrating with the
[JTAG protocol](https://en.wikipedia.org/wiki/Joint_Test_Action_Group).

 * wrappers
   - These wrappers allow access to internal JTAG interfaces inside FPGA
     devices.

 * wrappers/xilinx - Support for Xilinx FPGAs
   - Xilinx part is called something like `BSCAN_XXXXX`
   - Spartan 2/3/3A/6
   - Virtex 1/3/4/5
   - No support for Series 7 yet (watch https://github.com/xfguo/adv_debug_sys/tree/wip2)

 * wrappers/altera - Support for Altera FPGAs
   - Alter part is called something like `sld_virtual_jtag`

 * wrappers/icarus
   - Support for using Icarus Verilog simulator

 * wrappers/verilator
   - Support for using Verilator Verilog simulator
   - https://github.com/rdiez/jtag_dpi

 * wrappers/gpio
   - Support for providing a JTAG interface on GPIO pins.

 * adv_debug_sys
   - Support for the Advanced Debug System which can be connected via JTAG.
   - Provides support for debugging OpenRISC 1200 processor and wishbone bus.
