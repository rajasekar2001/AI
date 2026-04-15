from django.db import models
from django.contrib.auth.models import User
from pgvector.django import VectorField
from django.utils import timezone

class KnowledgeBase(models.Model):
    """Stores company's knowledge base documents (from text or PDF uploads)"""
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name='knowledge_base')
    content = models.TextField()
    embedding = VectorField(dimensions=384)
    # source_type = models.CharField(
    #     max_length=10, 
    #     choices=[('text', 'Text'), ('pdf', 'PDF')],
    #     default='text'
    # )
    SOURCE_TYPES = [
        ('text', 'Text'),
        ('pdf', 'PDF'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('file', 'File'),
    ]

    source_type = models.CharField(
        max_length=10,
        choices=SOURCE_TYPES,
        default='text'
    )
    source_filename = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file = models.FileField(
        upload_to='knowledge_files/',
        null=True,
        blank=True
    )
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company.username} - {self.source_type} - {self.source_filename} - {self.content[:50]}"


class BotConfiguration(models.Model):
    """Stores bot customization settings for each company"""
    company = models.OneToOneField(User, on_delete=models.CASCADE, related_name='bot_config')
    bot_name = models.CharField(max_length=100, default='Support Bot')
    welcome_message = models.TextField(default='Hello! How can I help you today?')
    system_prompt = models.TextField(
        default='You are a professional support assistant for {company_name}. Use ONLY the provided context to answer customer questions. If the answer is not in the context, politely say you do not know. Be brief, helpful, and professional.'
    )
    color_scheme = models.CharField(
        max_length=20,
        default='blue',
        choices=[('blue', 'Blue'), ('green', 'Green'), ('purple', 'Purple'), ('red', 'Red')]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.username}'s Bot - {self.bot_name}"


class ConversationHistory(models.Model):
    """Logs conversations for analytics and support"""
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    customer_name = models.CharField(max_length=100, default='Anonymous')
    customer_message = models.TextField()
    bot_response = models.TextField()
    conversation_duration = models.IntegerField(default=0, help_text="Duration in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    conversation_type = models.CharField(max_length=20, default='chatbot', choices=[
    ('chatbot', 'Chatbot'),
    ('voicebot', 'Voicebot'),
    ('voicecall', 'Voice Call')
])
    call_duration = models.IntegerField(null=True, blank=True, help_text="Duration in seconds")
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company.username} - {self.customer_name} - {self.created_at}"