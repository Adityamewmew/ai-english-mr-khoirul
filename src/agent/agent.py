from src.agent.state import AgentState
from src.agent.memory import Memory
from src.agent.executor import execute
from src.models.llm_client import chat
from src.prompts.system_prompts import SYSTEM_PROMPT
from src.utils.helpers import extract_json
import json
class Agent:
    def __init__(self):
        self.state=AgentState()
        self.memory=Memory()
    def run(self, prompt: str, max_steps=4) -> str:
        msgs=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt}]
        msgs+=self.memory.all()
        for _ in range(max_steps):
            try:
                out=chat(msgs)
            except Exception as e:
                out=f"[stub] Hello! I am Mr Khoirul AI agent. (LLM offline: {e}) — set LLM_API_KEY for live chat."
            # tool call via JSON?
            if '"tool"' in out:
                try:
                    j=json.loads(out) if out.strip().startswith("{") else extract_json(out)
                    tool, args = j["tool"], j.get("args",{})
                    res=execute(tool, args)
                    msgs.append({"role":"assistant","content":out})
                    msgs.append({"role":"user","content":f"[tool:{tool} result] {res}"})
                    continue
                except Exception: pass
            self.memory.add("user", prompt); self.memory.add("assistant", out)
            return out
        return out
    def reset(self): self.memory.clear(); self.state=AgentState()
