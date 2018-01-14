from litex.gen import *


class Identifier(Module):
    def __init__(self, ident):
        contents = list(ident.encode())
        l = len(contents)
        if l > 255:
            raise ValueError("Identifier string must be 255 characters or less")
        contents.insert(0, l)
        contents.append(0)
        self.mem = Memory(8, len(contents), init=contents)

    def get_memories(self):
        return [(True, self.mem)]
