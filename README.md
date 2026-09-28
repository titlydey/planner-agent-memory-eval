# Planner-Executor LLM Agent with Memory and Prompt Evaluation

A LangGraph agent with three steps: **plan** (LLM returns a JSON tool plan) -> **execute** (allow-listed tools) -> **respond** (LLM answers only from tool results and memory).

- **Planning:** the plan is parsed defensively; unknown tools and malformed JSON are dropped, and at most 3 steps run.
- **Memory:** sliding window of recent turns plus extracted facts, kept per session (`/chat` takes a `session_id`).
- **Safe tools:** `calculate` parses the AST (no `eval`), `convert`, `define`.
- **Prompt versions:** `app/prompts.py` holds planner prompts v1 and v2; `python -m evals.run_eval v1 v2` scores each on `evals/cases.json`.
- **LLM:** set `ANTHROPIC_API_KEY` (and `pip install anthropic`) to use a real model. Without a key a deterministic **mock** runs, so tests work offline. With the mock, v1 and v2 score the same; compare prompts only with a real model.
- **CI:** GitHub Actions runs pytest on every push. **Docker:** `Dockerfile` included.

## Run
```
pip install -r requirements.txt
python -m pytest -q
python -m evals.run_eval v1 v2
uvicorn app.main:api --reload      # POST /chat {"session_id":"a","question":"convert 5 km to miles"}
docker build -t planner-agent . && docker run -p 8000:8000 planner-agent
```

## Limitations
The mock is rule-based, memory is in-process (lost on restart), and the eval set is small.
