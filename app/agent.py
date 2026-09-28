import json, re
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from app import prompts
from app.tools import TOOLS

class S(TypedDict, total=False):
    question: str
    plan: list
    results: str
    answer: str

def parse_plan(raw):
    """Extract JSON from the model output and keep only valid, allow-listed steps."""
    m = re.search(r"\{.*\}", raw, re.S)
    try:
        steps = json.loads(m.group())["steps"]
    except Exception:
        return []
    return [s for s in steps if isinstance(s, dict) and s.get("tool") in TOOLS and isinstance(s.get("args"), dict)][:3]

def build(llm, memory, version="v2"):
    def plan(s):
        raw = llm.complete(prompts.PLANNER[version], f"MEMORY: {memory.context()}\nQUESTION: {s['question']}")
        return {"plan": parse_plan(raw)}
    def execute(s):
        out = []
        for st in s["plan"]:
            try:
                out.append(f"{st['tool']}={TOOLS[st['tool']](**st['args'])}")
            except Exception as e:
                out.append(f"{st['tool']} error: {e}")
        return {"results": "; ".join(out)}
    def respond(s):
        a = llm.complete(prompts.ANSWER, f"MEMORY: {memory.context()}\nQUESTION: {s['question']}\nRESULTS: {s['results']}")
        memory.add(s["question"], a)
        return {"answer": a}
    g = StateGraph(S)
    g.add_node("plan", plan); g.add_node("execute", execute); g.add_node("respond", respond)
    g.add_edge(START, "plan"); g.add_edge("plan", "execute"); g.add_edge("execute", "respond"); g.add_edge("respond", END)
    return g.compile()
