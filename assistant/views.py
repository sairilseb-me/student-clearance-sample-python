from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from assistant.rag import build_prompt, rank_chunks
from core.http import inertia_data
from core.ollama_client import OllamaError, embed, generate, is_available


@login_required
@require_http_methods(["GET"])
def status(request):
    return JsonResponse({"connected": is_available()})


@login_required
@require_http_methods(["POST"])
def chat(request):
    # inertia_data() is generic JSON-body parsing despite the name — this
    # isn't an Inertia request, just the same "Django's request.POST doesn't
    # understand JSON bodies" problem it already solves.
    question = (inertia_data(request).get("message") or "").strip()
    if not question:
        return JsonResponse({"error": "message is required"}, status=400)

    try:
        ranked = rank_chunks(embed(question))
        answer = generate(build_prompt(question, ranked))
    except OllamaError:
        return JsonResponse(
            {"error": "The Clearance Assistant is unavailable right now. Please try again shortly."},
            status=503,
        )

    return JsonResponse({
        "answer": answer,
        "sources": [
            {"title": chunk.document_title, "snippet": chunk.content[:240], "score": round(score, 3)}
            for score, chunk in ranked
        ],
    })
