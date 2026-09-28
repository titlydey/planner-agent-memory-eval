import json, sys
from app.agent import build
from app.llm import get_llm
from app.memory import Memory

def run(version="v2", llm=None):
    """Fraction of cases where the planner picks exactly the expected tools."""
    llm, cases, ok = llm or get_llm(), json.load(open("evals/cases.json")), 0
    for q, expected in cases:
        plan = build(llm, Memory(), version).invoke({"question": q})["plan"]
        ok += [s["tool"] for s in plan] == expected
    return ok / len(cases)

if __name__ == "__main__":
    for v in sys.argv[1:] or ["v1", "v2"]:
        print(f"prompt {v}: {run(v):.0%}")
