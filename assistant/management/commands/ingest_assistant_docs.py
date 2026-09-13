"""
Chunks and embeds the mock policy documents in assistant/documents/ into
DocumentChunk rows via Ollama's embeddings API.

Production note: see core/ollama_client.py's docstring — a real ingestion
pipeline would use LangChain's document loaders/text splitters and write
into ChromaDB instead of hand-splitting paragraphs into ORM rows.

Idempotent: safe to re-run after editing a document.
"""

import re
from pathlib import Path

from django.core.management.base import BaseCommand

from assistant.models import DocumentChunk
from core.ollama_client import embed

DOCUMENTS_DIR = Path(__file__).resolve().parent.parent.parent / "documents"


def chunk_text(text, min_length=40):
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text)]
    return [p for p in paragraphs if len(p) >= min_length]


class Command(BaseCommand):
    help = "Chunk and embed the mock policy documents into DocumentChunk rows."

    def handle(self, *args, **options):
        total = 0
        for doc_path in sorted(DOCUMENTS_DIR.glob("*.md")):
            slug = doc_path.stem
            title = slug.replace("-", " ").title()
            chunks = chunk_text(doc_path.read_text())

            for index, content in enumerate(chunks):
                DocumentChunk.objects.update_or_create(
                    document_slug=slug,
                    chunk_index=index,
                    defaults={"document_title": title, "content": content, "embedding": embed(content)},
                )
            DocumentChunk.objects.filter(document_slug=slug, chunk_index__gte=len(chunks)).delete()

            total += len(chunks)
            self.stdout.write(f"  {doc_path.name}: {len(chunks)} chunks")

        self.stdout.write(self.style.SUCCESS(f"Ingested {total} chunks total."))
