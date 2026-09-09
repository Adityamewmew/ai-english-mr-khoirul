from dataclasses import dataclass, field
from typing import List, Dict
@dataclass
class AgentState:
    messages: List[Dict] = field(default_factory=list)
    tool_calls: List[Dict] = field(default_factory=list)
    done: bool = False
    def add(self, role, content): self.messages.append({"role":role,"content":content})
