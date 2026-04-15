# 🎓 VoiceAI Developer Reference

Quick reference for developers working with this codebase.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser (Customer)               │
│                     Text/Voice Chat                     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────────┐
│                   Django Web Server                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Views      │  │  Templates   │  │   URLs       │   │
│  └──────┬──────┘  └──────────────┘  └──────────────┘   │
│         │                                                │
│  ┌──────▼──────────────────────────────────────────┐   │
│  │            Django ORM Models                    │   │
│  │ ┌────────────────┬──────────────┬────────────┐ │   │
│  │ │ KnowledgeBase  │ BotConfig    │ Conversations   │   │
│  │ └────────────────┴──────────────┴────────────┘ │   │
│  └──────────────────────────────────────────────────┘   │
│         │                                                │
└─────────┼────────────────────────────────────────────────┘
          │
          ↓ TCP Connection
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL + pgvector                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │   knowledge_base (id, company, content, embed)  │  │
│  │   bot_configuration (company, name, prompt)     │  │
│  │   conversation_history (company, msg, resp)     │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  External AI Services                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Groq Whisper │  │  Groq Llama  │  │ HuggingFace  │  │
│  │ Speech→Text  │  │   LLM Chat   │  │ Embeddings   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 📋 File Reference

### Models (`chatbot/models.py`)

```python
class KnowledgeBase:
    company (User FK)
    content (TextField)           # Original text
    embedding (VectorField)       # AI embedding
    source_type (choice)          # 'text' or 'pdf'
    source_filename (str)         # Original filename
    created_at (DateTimeField)    # Auto-set
    updated_at (DateTimeField)    # Auto-update

class BotConfiguration:
    company (User OneToOne)
    bot_name (str)
    welcome_message (TextField)
    system_prompt (TextField)
    color_scheme (choice)
    is_active (bool)

class ConversationHistory:
    company (User FK)
    customer_name (str)
    customer_message (TextField)
    bot_response (TextField)
    created_at (DateTimeField)
```

### Views (`chatbot/views.py`) - 12 Main Views

| View                     | Purpose            | Auth | Method   |
| ------------------------ | ------------------ | ---- | -------- |
| `landing_page`           | Home page          | No   | GET      |
| `signup`                 | Create account     | No   | GET/POST |
| `login_view`             | User login         | No   | GET/POST |
| `logout_view`            | User logout        | Yes  | GET      |
| `dashboard`              | Admin panel        | Yes  | GET/POST |
| `chat_page`              | Bot tester         | Yes  | GET      |
| `voice_chat_view`        | Internal voice API | Yes  | POST     |
| `text_chat_view`         | Internal text API  | Yes  | POST     |
| `public_chat_page`       | Customer chat page | No   | GET      |
| `public_voice_chat`      | Public voice API   | No   | POST     |
| `public_text_chat`       | Public text API    | No   | POST     |
| `process_and_save_chunk` | Helper function    | -    | -        |

### URLs (`chatbot/urls.py`) - Route Map

```python
# Public
GET  /                          → landing_page
GET  /signup/                   → signup
GET  /login/                    → login_view
GET  /logout/                   → logout_view

# Company (Protected)
GET  /dashboard/                → dashboard
POST /dashboard/                → dashboard (post handler)
GET  /bot/                      → chat_page
POST /voice-chat/               → voice_chat_view
POST /text-chat/                → text_chat_view

# Customer (Public)
GET  /chat/<company_name>/      → public_chat_page
POST /chat/<company_name>/voice/→ public_voice_chat
POST /chat/<company_name>/text/ → public_text_chat
```

### Utils (`chatbot/utils.py`) - AI Functions

```python
def get_embedding(text: str) -> list:
    """Convert text to vector using HuggingFace"""

def transcribe_audio(audio_file) -> str:
    """Convert audio to text using Groq Whisper"""

def get_llm_answer(query: str, context: str, bot_config=None) -> str:
    """Generate AI response using Groq Llama 3"""
```

## 🔄 Data Flow Examples

### Text Chat Flow

```
Customer Input
    ↓
POST /chat/tesla/text/
{message: "What's your return policy?"}
    ↓
Django View (public_text_chat)
    ↓
1. Load company 'tesla'
2. Get embedding for message
    ↓
    Groq API ← sends text
              → returns embedding vector
    ↓
3. Search PostgreSQL with pgvector
    SELECT * FROM chatbot_knowledgebase
    WHERE company_id = tesla.id
    ORDER BY embedding <-> [message_vector]
    LIMIT 3
    ↓
4. Get top 3 matching documents
5. Combine as context: "Policy... Terms... Returns..."
    ↓
6. Call Groq LLM with context
    LLM receives:
    - System: "You are support bot for Tesla..."
    - Context: "Policy... Terms..."
    - User: "What's return policy?"
    ↓
    LLM returns: "Tesla offers 7-day returns..."
    ↓
7. Save to ConversationHistory
8. Return JSON response
    ↓
JavaScript in Browser
    ↓
Display response to customer
```

### Voice Chat Flow

```
Customer speaks into microphone
    ↓
Browser records audio
    ↓
POST /chat/tesla/voice/
    ↓
1. Transcribe audio
    ↓
    Groq Whisper API
    ↓ "Hello, can you help me?"
    ↓
2. Process transcribed text (same as text chat above)
    ↓
3. Return both transcript and response
    JSON: {
        "transcript": "Hello, can you help me?",
        "answer": "Of course! How can I assist?"
    }
    ↓
JavaScript in Browser
    ↓
- Display transcript
- Display response
- (Optional) Text-to-speech
```

### Admin Dashboard Flow

```
Company admin at /dashboard/

Upload PDF:
    1. Read PDF file
    2. Extract text page by page
    3. Split into 1000-char chunks
    4. For each chunk:
        - Generate embedding (HuggingFace)
        - Save to KnowledgeBase table
    5. Show confirmation

Update Bot Settings:
    1. Get or create BotConfiguration
    2. Update fields
    3. Save to database
    4. Show success message

View Knowledge:
    1. Query all KnowledgeBase.objects.filter(company=user)
    2. Display as list
    3. Allow delete

Delete Knowledge:
    1. Get KnowledgeBase item
    2. Verify it belongs to user
    3. Delete from database
```

## 🧠 AI Integration Details

### Embeddings (HuggingFace)

```python
# Model: sentence-transformers/all-MiniLM-L6-v2
# Input: Any text (up to ~512 tokens)
# Output: Vector of 384 dimensions
# Cost: Free

Example:
"Our refund policy is 30 days"
    ↓
HuggingFace API
    ↓
[0.234, -0.123, 0.456, ..., -0.321]  # 384 numbers
    ↓
Stored in PostgreSQL as vector type
```

### Semantic Search (pgvector)

```sql
-- Find similar documents
SELECT content FROM chatbot_knowledgebase
WHERE company_id = ?
ORDER BY embedding <-> ? LIMIT 3

-- <-> is cosine distance operator in pgvector
-- Finds 3 most similar documents to query vector
```

### LLM Chat (Groq)

```python
# Model: llama3-8b-8192
# Speed: ~80 tokens/second
# Context: 8K tokens max
# Cost: Free tier available

messages = [
    {
        "role": "system",
        "content": "You are a support bot for Tesla..."
    },
    {
        "role": "user",
        "content": "What's your return policy?"
    }
]

response = client.chat.completions.create(
    messages=messages,
    model="llama3-8b-8192"
)
```

### Speech-to-Text (Groq Whisper)

```python
# Model: whisper-large-v3
# Languages: 99+ languages
# Speed: Real-time
# Cost: Free

transcription = client.audio.transcriptions.create(
    file=("audio.wav", audio_file.read()),
    model="whisper-large-v3"
)
# Returns: {"text": "Hello, how can I help?"}
```

## 🔧 Common Tasks

### Add New View

```python
@login_required(login_url='login')
def my_new_view(request):
    if request.method == 'POST':
        # Handle form submission
        return JsonResponse({'status': 'success'})

    # Get data
    data = MyModel.objects.filter(user=request.user)

    # Render template
    return render(request, 'my_template.html', {'data': data})
```

### Add New URL

```python
# In chatbot/urls.py
path('my-path/', views.my_new_view, name='my_view'),
```

### Query Knowledge Base

```python
# Get all knowledge for a company
docs = KnowledgeBase.objects.filter(company=user)

# Search semantically
from pgvector.django import CosineDistance
query_vector = get_embedding("What's the policy?")
similar = KnowledgeBase.objects.filter(
    company=company
).order_by(CosineDistance('embedding', query_vector))[:3]
```

### Add to Bot Configuration

```python
# In models.py - add new field
bot_config = BotConfiguration.objects.get(company=user)
bot_config.new_field = value
bot_config.save()

# In views.py - update from form
bot_config.new_field = request.POST.get('new_field')
bot_config.save()

# In template - display
{{ bot_config.new_field }}
```

## 📊 Performance Tips

1. **Database Queries**
   - Use `.select_related()` for ForeignKey
   - Use `.prefetch_related()` for reverse relations
   - Add `.only('field1', 'field2')` to limit columns

2. **Embeddings**
   - Cache embeddings to avoid recomputation
   - Batch requests when possible
   - Consider limiting knowledge base size

3. **API Calls**
   - Implement retry logic (already done)
   - Monitor rate limits
   - Cache LLM responses when appropriate

4. **Frontend**
   - Lazy load JavaScript
   - Minimize CSS/JS
   - Use CDN for Tailwind

## 🐛 Debugging

### Check Logs

```bash
python manage.py runserver
# Errors and stack traces displayed in console
```

### Django Shell

```bash
python manage.py shell

# Test embeddings
from chatbot.utils import get_embedding
vec = get_embedding("test text")

# Test database
from chatbot.models import KnowledgeBase
docs = KnowledgeBase.objects.all()

# Test LLM
from chatbot.utils import get_llm_answer
ans = get_llm_answer("Hi", "My context")
```

### Check Database

```bash
python manage.py dbshell

SELECT * FROM chatbot_knowledgebase;
SELECT * FROM chatbot_botconfiguration;
SELECT COUNT(*) FROM chatbot_conversationhistory;
```

## 🚀 Deployment Checklist

- [ ] Change SECRET_KEY in settings.py
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS with domain
- [ ] Set up HTTPS/SSL
- [ ] Configure static files with WhiteNoise or S3
- [ ] Set up database backups
- [ ] Configure email backend
- [ ] Set up error logging (Sentry)
- [ ] Configure monitoring (New Relic)
- [ ] Test all APIs with production keys

## 📚 Learn More

- Django Docs: https://docs.djangoproject.com/
- PostgreSQL pgvector: https://github.com/pgvector/pgvector
- Groq API: https://console.groq.com/docs
- HuggingFace: https://huggingface.co/docs

---

**Last Updated**: January 18, 2026
