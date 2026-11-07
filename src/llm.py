import json
import os
import time

from google import genai
from google.genai import types

_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
GEN_MODEL = "auto"
EVAL_MODEL = "auto"
_dead = set()
_cache = []


def _models():
    if _cache:
        return _cache
    names = []
    for m in _client.models.list():
        n = m.name.replace("models/", "")
        acts = getattr(m, "supported_actions", None) or []
        if "flash" in n and "generateContent" in acts and not any(
                x in n for x in ["image", "tts", "live", "audio", "embedding"]):
            names.append(n)
    names.sort(key=lambda n: ("lite" in n, n))  # normal flash first, lite as backup
    _cache.extend(names)
    return _cache


def call(prompt, system, model="auto", as_json=False, temperature=0.7):
    cfg = types.GenerateContentConfig(
        system_instruction=system,
        temperature=temperature,
        response_mime_type="application/json" if as_json else "text/plain",
    )
    candidates = ([model] if model != "auto" else []) + \
                 [m for m in _models() if m != model]
    last = None
    for m in candidates:
        if m in _dead:
            continue
        for attempt in range(2):
            try:
                text = _client.models.generate_content(
                    model=m, contents=prompt, config=cfg).text
                result = json.loads(text) if as_json else text
                print(f"   [model: {m}]")
                return result
            except Exception as e:
                last = e
                code = getattr(e, "code", None)
                if code in (429, 404):
                    _dead.add(m)  # quota over or model unavailable -> try next model
                    break
                if code in (400, 401, 403):
                    raise
                time.sleep(2)
    raise RuntimeError(f"All models failed. Last error: {last}")
