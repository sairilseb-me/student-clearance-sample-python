from django.db import models


class DocumentChunk(models.Model):
    """A retrievable chunk of a mock policy document, plus the embedding
    Ollama's `all-minilm` model produced for it.

    This model + the brute-force cosine-similarity scan in assistant/rag.py
    stand in for a real vector database. Fine at this demo's scale (a few
    dozen chunks) — see core/ollama_client.py's docstring for what a
    production version of this feature would use instead.
    """

    document_slug = models.SlugField()
    document_title = models.CharField(max_length=255)
    chunk_index = models.PositiveIntegerField()
    content = models.TextField()
    embedding = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["document_slug", "chunk_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["document_slug", "chunk_index"], name="unique_chunk_per_document"
            ),
        ]

    def __str__(self):
        return f"{self.document_title} #{self.chunk_index}"
