"""Shared loader for results/corpus_run.json (finding text is interned to keep the file small)."""
import json
import os

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "corpus_run.json")


def load_captures():
    data = json.load(open(PATH))
    texts = data.get("texts", [])
    for c in data["captures"]:
        for f in c.get("findings", []):
            for k in ("title", "conclusion", "explanation"):
                if isinstance(f.get(k), int):
                    f[k] = texts[f[k]]
    return data["captures"]
