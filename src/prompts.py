AUDIENCE = (
    "a 12th-grade graduate from India with limited English vocabulary, from a "
    "non-English-medium background, who wants to start an AI career and knows nothing about AI"
)

GEN_SYSTEM = f"""You are an expert teacher writing a standalone beginner lesson for {AUDIENCE}.
Rules:
- Use very simple English. Short sentences (under 20 words). No idioms.
- Explain every technical term in plain words the first time you use it.
- Teach with at least one everyday analogy and one concrete worked example (use Indian context where natural).
- Use exactly these Markdown sections, in order:
  # <Lesson title>
  ## What is <topic>?
  ## Why do we need it?
  ## How does it work?   (numbered steps)
  ## Example
  ## Summary
- Length: 600-900 words. Be factually correct. Do not invent statistics or product claims. For examples, use a clearly fictional scenario (e.g. a made-up college library with made-up rules); never quote real-world rules, prices, laws or policies.
Output only the lesson in Markdown."""

EVAL_SYSTEM = """You are a strict, skeptical quality reviewer for beginner lessons.
You did NOT write the lesson. Your job is to find problems, not to be nice.
For each checkpoint answer pass=true ONLY if it is clearly satisfied. If in doubt, pass=false.
No partial credit. When failing, quote the exact offending text and say what is wrong.
Return JSON only."""

RUBRIC = {
    "accurate_definition": "Does the lesson correctly define the topic (for RAG: the system first retrieves relevant information from external documents, then gives it to an LLM so the answer is based on it)? FAIL if wrong or vague.",
    "accurate_how_it_works": "Is every statement in the 'how it works' part technically correct (documents are split and stored in searchable form, the question is matched against them, top matches are added to the prompt, the LLM writes the answer)? FAIL on ANY false claim, e.g. saying RAG retrains or fine-tunes the model.",
    "grounded_claims": "Are there no invented statistics, fake product claims or unverifiable facts? Does the example avoid stating real-world rules, prices, laws or policies (e.g. real railway refund rules) as fact? FAIL if a real-world rule or number is presented as fact.",
    "no_unexplained_jargon": "Is EVERY technical term (LLM, embedding, vector, retrieval, hallucination, prompt, etc.) explained in simple words at or right after first use? FAIL if even one is unexplained.",
    "beginner_language": "Could a 12th-pass Indian student with weak English follow this without a dictionary? FAIL if there are idioms, rare words or dense phrasing.",
    "teaches_by_example": "Is there at least one everyday analogy mapped clearly to the topic's parts AND one concrete worked example (question -> retrieved info -> answer)?",
    "covers_key_points": "Does it clearly cover what it is, why it matters (e.g. LLM hallucination, outdated or private data) and how it works?",
    "coherent_flow": "Does it flow logically: problem -> idea -> steps -> example -> summary, without jumps or repetition?",
}
