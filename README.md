# Self-Evaluating Lesson Content Generator (Agentic Workflow)

Generates a beginner lesson (default: Introduction to RAG) for a 12th-pass Indian learner with
limited English, judges it against a hard pass/fail rubric, and regenerates until it passes
(max 2 retries, so the loop always terminates).
Output: the passing lesson + a rejection log (what failed, why, what changed on retry).

## Setup and run

    pip install -r requirements.txt
    export GEMINI_API_KEY=your_key
    python main.py
    python main.py --inject-error
    python main.py --topic "What is an API?"

Outputs: outputs/final_lesson.md, outputs/rejection_log.md (+ .json), memory.json

## Architecture

    Topic -> Generator -> Evaluator (3 code checks + 8 LLM checks, hard PASS/FAIL)
                ^              |-- all pass --> final_lesson.md
                |              |-- any fail --> reasons back to Generator (max 2 retries)
                |              |-- every attempt --> rejection_log
          memory.json <-- real failures; a check failing 2+ times -> prompt improver
          (learned rules)     writes a permanent rule added to the Generator prompt

Files: main.py (loop), src/generator.py, src/evaluator.py, src/checks.py,
src/prompts.py (prompts + rubric), src/memory.py (memory + self-evolving), src/llm.py (model wrapper).

## Design choices and trade-offs

- Plain Python loop, no framework: easy to explain and debug. Trade-off: no graph tooling.
- Separate evaluator (own prompt, temperature 0, skeptical reviewer): a generator grading itself is lenient. Trade-off: extra cost.
- Hard pass/fail, no scores: binary checks give actionable reasons. Trade-off: less nuance.
- Hybrid checks: code checks measurable things (sentence length, word count, sections); the LLM checks meaning (accuracy, jargon, flow).
- Missing evaluator verdict counts as FAIL: never ship unverified content.
- Max 2 retries, then the best attempt is saved and flagged FAILED_AFTER_RETRIES.
- Failures go back to the generator as exact reasons plus the previous draft.
- llm.py picks an available Gemini flash model automatically and falls back to the next one on quota or 404 errors.

## Memory and self-evolving

memory.json stores run history, failure count per checkpoint and learned rules.
If a checkpoint fails 2+ times, a prompt-improver call writes one rule that is injected into every
future generator prompt. Deliberately injected errors are excluded from memory.

## Real issue found and fixed

An early run passed all checks, but the example quoted real railway refund rules as fact. The LLM judge
has no fact source, so it missed this. Fix: the generator prompt now requires fictional examples, and the
grounded_claims rubric check fails on real-world rules or numbers stated as fact.

## Limitations

- The LLM judge can be wrong; there is no external fact source. A human spot-check is advised.
- The rubric is fixed; a next step is letting the system propose rubric changes.
- Accuracy checkpoints are written for RAG-like topics.
