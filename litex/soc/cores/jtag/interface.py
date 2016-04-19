
from litex.gen.genlib.record import Record

_port_layout = [
  ('tck', 1),     # Output
  ('tdo', 1),     # Input
  ('tdi', 1),     # Output
  ('tms', 1),     # Output
  ('trst', 1),    # Output
]
def Port():
  return Record(_port_layout)

_tap_layout = [
  ('tck', 1),     # Output - tck_o
  ('tdo', 1),     # Input  - debug_tdo_i
  ('tdi', 1),     # Output - debug_tdo_o
  ('reset', 1),   # Output - test_logic_reset_0
  ('idle', 1),    # Output - run_test_idle_o

  # dr == Data Register
  ('shift', 1),   # Output - shift_dr_o
  ('capture', 1), # Output - capture_dr_o
  ('pause',  1),  # Output - pause_dr_o
  ('update', 1),  # Output - update_dr_o
  ('select', 1),  # Output - debug_select_o
]
def TAP():
    return Record(_tap_layout)
