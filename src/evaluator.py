from . import llm
from .checks import run_code_checks
from .prompts import EVAL_SYSTEM, RUBRIC


def evaluate(lesson):
    results = run_code_checks(lesson)

    checklist = "\n".join(f"- {k}: {v}" for k, v in RUBRIC.items())
    prompt = f"""Checkpoints:
{checklist}

Return JSON: {{"results": [{{"id": "<checkpoint id>", "pass": true/false, "reason": "<short reason, quote offending text if failing>"}}]}}
Include every checkpoint id exactly once.

LESSON:
\"\"\"
{lesson}
\"\"\""""
    out = llm.call(prompt, EVAL_SYSTEM, llm.EVAL_MODEL, as_json=True, temperature=0)
    got = {r.get("id"): r for r in out.get("results", [])}
    for cid in RUBRIC:
        r = got.get(cid)
        if r is None:
            results.append({"id": cid, "pass": False, "reason": "Evaluator returned no verdict."})
        else:
            results.append({"id": cid, "pass": bool(r.get("pass")), "reason": r.get("reason", "")})
    return results
