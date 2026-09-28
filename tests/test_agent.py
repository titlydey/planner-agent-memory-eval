import pytest
from fastapi.testclient import TestClient
from app import tools
from app.agent import build, parse_plan
from app.llm import MockLLM
from app.memory import Memory
from app.main import api
from evals.run_eval import run

def test_calculator_is_safe():
    assert tools.calculate("2+3*4") == 14
    for bad in ("__import__('os').system('x')", "9**9**9", "a+1"):
        with pytest.raises(ValueError):
            tools.calculate(bad)

def test_convert():
    assert tools.convert(5, **{"from": "km", "to": "miles"}) == pytest.approx(3.1069, abs=1e-3)
    assert tools.convert(100, **{"from": "c", "to": "f"}) == 212

def test_parse_plan_filters_unknown_tools_and_bad_json():
    raw = 'Sure! {"steps":[{"tool":"os_system","args":{}},{"tool":"define","args":{"term":"rag"}}]}'
    assert [s["tool"] for s in parse_plan(raw)] == ["define"]
    assert parse_plan("not json") == []

def test_end_to_end_and_memory():
    mem = Memory()
    out = build(MockLLM(), mem).invoke({"question": "my name is Asha. What is 12*(3+4)?"})
    assert "84" in out["answer"] and mem.facts["name"] == "Asha"

def test_memory_window():
    m = Memory(window=2)
    for i in range(4):
        m.add(f"q{i}", "a")
    assert len(m.turns) == 2

def test_eval_accuracy_offline():
    assert run("v2", MockLLM()) >= 0.9

def test_api():
    c = TestClient(api)
    assert c.get("/health").json() == {"status": "ok"}
    r = c.post("/chat", json={"session_id": "s1", "question": "convert 5 km to miles"}).json()
    assert r["plan"][0]["tool"] == "convert"
    assert c.post("/chat", json={"session_id": "s1", "question": ""}).status_code == 422
