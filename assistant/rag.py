"""
Retrieval logic for the Clearance Assistant: brute-force cosine similarity
over every DocumentChunk row. A production version would replace this
module with a ChromaDB similarity query behind a LangChain retriever —
skipped here; see core/ollama_client.py.
"""

import math

from assistant.models import DocumentChunk

TOP_K = 3


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def rank_chunks(question_embedding, top_k=TOP_K):
    scored = [
        (cosine_similarity(question_embedding, chunk.embedding), chunk)
        for chunk in DocumentChunk.objects.all()
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[:top_k]


def build_prompt(question, ranked_chunks):
    context = "\n\n".join(
        f"[Source: {chunk.document_title}]\n{chunk.content}" for _, chunk in ranked_chunks
    )
    return (
        "You are the Clearance Assistant for a college clearance-signing system. "
        "Answer the student's question using ONLY the context below. If the answer "
        "isn't in the context, say you don't have that information and suggest they "
        "contact the relevant office.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    )
