from . import llm
from .prompts import GEN_SYSTEM


def generate(topic, learned_rules, feedback=None, previous=None):
    rules = ""
    if learned_rules:
        rules = "\nExtra rules learned from past failures (follow strictly):\n" + \
                "\n".join(f"- {r}" for r in learned_rules)
    if feedback is None:
        prompt = f"Write the lesson on: {topic}{rules}"
    else:
        fb = "\n".join(f"- [{f['id']}] {f['reason']}" for f in feedback)
        prompt = (f"Topic: {topic}{rules}\n\nYour previous draft was REJECTED by the reviewer.\n"
                  f"Reasons:\n{fb}\n\nPREVIOUS DRAFT:\n{previous}\n\n"
                  "Rewrite the full lesson and fix every reason above without breaking anything else.")
    return llm.call(prompt, GEN_SYSTEM, llm.GEN_MODEL, temperature=0.7)


def summarize_change(failures, old, new):
    fb = "\n".join(f"- [{f['id']}] {f['reason']}" for f in failures)
    prompt = (f"A lesson was rejected for:\n{fb}\n\nOLD:\n{old}\n\nNEW:\n{new}\n\n"
              "In 2-3 short bullet points, say what was changed in the NEW version to address the rejection.")
    return llm.call(prompt, "You summarise edits concisely.", llm.GEN_MODEL, temperature=0)


def inject_error(lesson):
    bad = ("\n\nRAG works by retraining the whole AI model on your documents every time you ask a question. "
           "It uses cosine similarity over a high-dimensional vector manifold to do this.\n")
    lines = lesson.splitlines()
    for i, l in enumerate(lines):
        if l.strip() and not l.lstrip().startswith("#"):
            lines.insert(i + 1, bad)
            break
    return "\n".join(lines)
