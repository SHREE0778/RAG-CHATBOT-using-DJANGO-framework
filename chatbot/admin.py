

# Register your models here.
from django.contrib import admin
from .models import Document, ChatMessage, EmbeddingMetadata

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'user', 'uploaded_at', 'processed']
    list_filter = ['processed', 'uploaded_at']
    search_fields = ['filename', 'user__username']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'message_preview', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['user__username', 'message', 'response']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'

@admin.register(EmbeddingMetadata)
class EmbeddingMetadataAdmin(admin.ModelAdmin):
    list_display = ['user', 'document', 'chunk_id', 'created_at']
    list_filter = ['created_at']