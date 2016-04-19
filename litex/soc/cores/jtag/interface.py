
from litex.gen.genlib.record import Record

_base_layout = [
  ('tck', 1),     # Output - tck_o
  ('tdo', 1),     # Input  - debug_tdo_i
  ('tdi', 1),     # Output - tdi_o
  ('tms', 1),     # Output - debug_select_o
  ('trst', 1),    # Output - test_logic_reset_o
]
def Base():
  return Record(_base_layout)

_dr_layout = [
  ('idle', 1),    # Output - run_test_idle_o

  # dr == Data Register
  ('shift', 1),   # Output - shift_dr_o
  ('capture', 1), # Output - capture_dr_o
  ('pause',  1),  # Output - pause_dr_o
  ('update', 1),  # Output - update_dr_o
]
def DataRegister():
    return Record(_dr_layout)

def Extended():
    return Record(_base_layout + _dr_layout)
 
