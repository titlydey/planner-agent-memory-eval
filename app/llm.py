import os, re, json

class MockLLM:
    """Deterministic stand-in so tests run offline. NOT a real model."""
    def complete(self, system, user):
        if "PLANNER" in system:
            q = user.split("QUESTION:")[-1].strip().lower()
            m = re.search(r"convert ([\d.]+) (\w+) to (\w+)", q)
            if m:
                return json.dumps({"steps": [{"tool": "convert", "args": {"value": float(m[1]), "from": m[2], "to": m[3]}}]})
            m = re.search(r"(\d[\d\s.()]*[+\-*/][\d\s.+\-*/()]*[\d)])", q)
            if m:
                return json.dumps({"steps": [{"tool": "calculate", "args": {"expression": m[1].strip()}}]})
            m = re.search(r"define (\w+)", q)
            if m:
                return json.dumps({"steps": [{"tool": "define", "args": {"term": m[1]}}]})
            return json.dumps({"steps": []})
        return user.split("RESULTS:")[-1].strip() or "No tool result."

class AnthropicLLM:
    def __init__(self):
        import anthropic
        self.client = anthropic.Anthropic()
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
    def complete(self, system, user):
        r = self.client.messages.create(model=self.model, max_tokens=500, system=system,
                                        messages=[{"role": "user", "content": user}])
        return r.content[0].text

def get_llm():
    return AnthropicLLM() if os.getenv("ANTHROPIC_API_KEY") else MockLLM()
