from collections import deque
class Memory:
    def __init__(self, max_turns=20): self.buf=deque(maxlen=max_turns*2)
    def add(self, role, content): self.buf.append({"role":role,"content":content})
    def all(self): return list(self.buf)
    def clear(self): self.buf.clear()
