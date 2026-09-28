import re

class Memory:
    """Sliding window of recent turns plus simple extracted facts."""
    def __init__(self, window=6):
        self.window, self.turns, self.facts = window, [], {}
    def add(self, question, answer):
        self.turns = (self.turns + [(question, answer)])[-self.window:]
        m = re.search(r"my name is (\w+)", question, re.I)
        if m:
            self.facts["name"] = m[1]
    def context(self):
        facts = "; ".join(f"{k}={v}" for k, v in self.facts.items()) or "none"
        recent = " | ".join(f"Q:{q} A:{a}" for q, a in self.turns) or "none"
        return f"facts: {facts}. recent: {recent}"
