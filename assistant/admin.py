from django.contrib import admin

from assistant.models import DocumentChunk


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ["document_title", "chunk_index", "content_preview"]
    list_filter = ["document_slug"]
    readonly_fields = ["embedding"]

    def content_preview(self, obj):
        return obj.content[:80]
