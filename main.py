import argparse
import json
import os

from src import memory
from src.evaluator import evaluate
from src.generator import generate, inject_error, summarize_change


def run(topic, inject, max_retries):
    mem = memory.load()
    rules = mem["learned_rules"]
    print(f"Topic: {topic} | learned rules loaded: {len(rules)}")

    log, real_failures = [], []
    feedback = draft = None
    best = (10**9, None)
    status = "FAILED_AFTER_RETRIES"

    for attempt in range(1, max_retries + 2):
        print(f"\n--- Attempt {attempt}: generating ...")
        new = generate(topic, rules, feedback, draft)
        if attempt > 1:
            log[-1]["what_changed_on_retry"] = summarize_change(feedback, draft, new)
        draft, injected = new, False
        if inject and attempt == 1:
            draft, injected = inject_error(draft), True
            print("   (deliberate error injected)")

        results = evaluate(draft)
        fails = [r for r in results if not r["pass"]]
        print(f"   evaluator: {len(results) - len(fails)}/{len(results)} checks passed")
        for f in fails:
            print(f"   FAIL [{f['id']}] {f['reason'][:150]}")

        log.append({"attempt": attempt, "injected_error": injected,
                    "passed": len(results) - len(fails), "total": len(results),
                    "failed_checks": fails})
        if not injected:
            real_failures += fails
        if len(fails) < best[0]:
            best = (len(fails), draft)
        if not fails:
            status = "PASSED"
            break
        feedback = fails

    final = draft if status == "PASSED" else best[1]
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/final_lesson.md", "w") as f:
        f.write(final)
    with open("outputs/rejection_log.json", "w") as f:
        json.dump({"topic": topic, "status": status, "attempts": log}, f, indent=2)
    with open("outputs/rejection_log.md", "w") as f:
        f.write(f"# Rejection log: {topic}\nFinal status: **{status}**\n")
        for e in log:
            f.write(f"\n## Attempt {e['attempt']} ({e['passed']}/{e['total']} passed)"
                    f"{' [deliberate error injected]' if e['injected_error'] else ''}\n")
            if not e["failed_checks"]:
                f.write("All checks passed.\n")
            for c in e["failed_checks"]:
                f.write(f"- **FAILED `{c['id']}`**: {c['reason']}\n")
            if e.get("what_changed_on_retry"):
                f.write(f"\n**What changed on retry:**\n{e['what_changed_on_retry']}\n")

    new_rules = memory.update(mem, topic, status, len(log), real_failures)
    for cid, rule in new_rules:
        print(f"\n[SELF-EVOLVING] '{cid}' kept failing -> new permanent rule added: {rule}")
    print(f"\nDone: {status}. See outputs/final_lesson.md and outputs/rejection_log.md")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--topic", default="Introduction to RAG (Retrieval-Augmented Generation)")
    p.add_argument("--inject-error", action="store_true")
    p.add_argument("--max-retries", type=int, default=2)
    a = p.parse_args()
    run(a.topic, a.inject_error, a.max_retries)
