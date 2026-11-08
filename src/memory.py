import json
import os

from . import llm

PATH = "memory.json"
EVOLVE_AFTER = 2


def load():
    if os.path.exists(PATH):
        with open(PATH) as f:
            return json.load(f)
    return {"runs": [], "fail_counts": {}, "last_reasons": {}, "learned_rules": [], "ruled": []}


def save(mem):
    with open(PATH, "w") as f:
        json.dump(mem, f, indent=2)


def update(mem, topic, status, attempts, failures_from_real_attempts):
    mem["runs"].append({"topic": topic, "status": status, "attempts": attempts})
    for f in failures_from_real_attempts:
        mem["fail_counts"][f["id"]] = mem["fail_counts"].get(f["id"], 0) + 1
        mem["last_reasons"][f["id"]] = f["reason"]

    new_rules = []
    for cid, n in mem["fail_counts"].items():
        if n >= EVOLVE_AFTER and cid not in mem["ruled"]:
            rule = llm.call(
                f"A lesson generator keeps failing the checkpoint '{cid}' (failed {n} times). "
                f"Latest reason: {mem['last_reasons'][cid]}\n"
                "Write ONE short, concrete instruction to add to the generator's prompt that prevents this. "
                "Output only the instruction.",
                "You improve prompts.", llm.GEN_MODEL, temperature=0).strip()
            mem["learned_rules"].append(rule)
            mem["ruled"].append(cid)
            new_rules.append((cid, rule))
    save(mem)
    return new_rules
