"""
Thin HTTP client for Ollama's local REST API (embeddings + generation).

Production note: a real-world version of this feature would replace this
module — plus assistant/rag.py's brute-force cosine similarity and the
DocumentChunk model — with LangChain (orchestration) + ChromaDB (a proper
ANN-indexed vector store) in front of the same Ollama server. Both are
skipped here to keep this demo's dependency footprint at zero extra pip
packages and the whole RAG pipeline readable end-to-end.
"""

import json
import urllib.error
import urllib.request

from django.conf import settings


class OllamaError(RuntimeError):
    """Raised when Ollama is unreachable or returns an unusable response."""


def _post(path, payload, timeout):
    request = urllib.request.Request(
        f"{settings.OLLAMA_BASE_URL}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        raise OllamaError(f"Ollama request to {path} failed: {exc}") from exc


def embed(text, model=None):
    model = model or settings.OLLAMA_EMBEDDING_MODEL
    result = _post("/api/embeddings", {"model": model, "prompt": text}, timeout=30)
    embedding = result.get("embedding")
    if not embedding:
        raise OllamaError(f"Ollama returned no embedding for model {model!r}")
    return embedding


def generate(prompt, model=None):
    model = model or settings.OLLAMA_GENERATION_MODEL
    result = _post("/api/generate", {"model": model, "prompt": prompt, "stream": False}, timeout=120)
    answer = result.get("response")
    if answer is None:
        raise OllamaError(f"Ollama returned no response for model {model!r}")
    return answer.strip()


def is_available():
    """Cheap reachability check (hits /api/tags, no model load) for the chat
    widget to disable itself against instead of failing on the first send."""
    request = urllib.request.Request(f"{settings.OLLAMA_BASE_URL}/api/tags")
    try:
        with urllib.request.urlopen(request, timeout=3):
            return True
    except (urllib.error.URLError, TimeoutError, OSError):
        return False
