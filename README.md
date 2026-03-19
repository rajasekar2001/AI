# VoiceAI - Private Voice-Enabled Customer Support Bot

A Django-based platform for companies to create and deploy voice-enabled customer support bots powered by AI. Companies upload their knowledge base (PDFs, documents, FAQs), and customers can interact with the bot via voice or text.

## Features

✅ **Voice Support** - Customers talk naturally to the bot  
✅ **PDF & Text Upload** - Feed company knowledge base  
✅ **Bot Customization** - Custom bot name, welcome message, system behavior  
✅ **Privacy First** - All data stays private, no third-party access  
✅ **Analytics** - Track conversations and bot performance  
✅ **Easy Sharing** - Unique public URL for each company's bot  
✅ **Admin Dashboard** - Complete control for company admins

## Tech Stack

- **Backend**: Django 6.0
- **Database**: PostgreSQL with pgvector support
- **AI/ML**:
  - Embeddings: HuggingFace (sentence-transformers)
  - LLM: Groq (Llama 3)
  - Speech-to-Text: Groq Whisper
- **Frontend**: Tailwind CSS

## Installation & Setup

### 1. Clone and Install Dependencies

```bash
cd voicebot
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
# Database
DB_NAME=your_supabase_db_name
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=your-supabase-host.postgres.supabase.co
DB_PORT=5432

# API Keys
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token
```

**Get API Keys:**

- **Groq API**: https://console.groq.com (Free tier available)
- **HuggingFace Token**: https://huggingface.co/settings/tokens (Free tier available)

### 3. Database Setup

Enable pgvector in PostgreSQL:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Then apply Django migrations:

```bash
python manage.py migrate
```

### 4. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000

## Usage

### For Companies

1. **Sign Up** - Create account at `/signup/`
2. **Add Knowledge** - Upload PDFs or paste text at Dashboard
3. **Customize Bot** - Set name, welcome message, behavior
4. **Test Bot** - Test with voice/text in the bot tester
5. **Share Link** - Get unique public URL at `/chat/yourcompanyname/`

### For Customers

1. Visit the company's unique bot link (e.g., `/chat/tesla/`)
2. Choose **Text** or **Voice** mode
3. Ask questions - bot responds based on company knowledge
4. Voice mode: Auto speech-to-text → AI response → Text to speech

## Project Structure

```
voicebot/
├── chatbot/
│   ├── models.py          # Database models
│   ├── views.py           # All view functions
│   ├── urls.py            # URL routing
│   ├── utils.py           # AI/ML functions
│   └── migrations/        # Database migrations
├── core/
│   ├── settings.py        # Django configuration
│   ├── urls.py            # Main URL config
│   └── wsgi.py            # WSGI config
├── templates/
│   ├── landing.html       # Home page
│   ├── chat.html          # Company bot tester
│   ├── dashboard.html     # Admin dashboard
│   ├── public_chat.html   # Customer chat interface
│   └── registration/
│       ├── login.html
│       └── signup.html
├── requirements.txt       # Dependencies
└── manage.py             # Django management

```

## Key Features Explained

### Knowledge Base Management

- Upload PDFs (automatically split into 1000-char chunks)
- Add text content directly
- Embeddings stored in PostgreSQL with pgvector
- Semantic search using cosine distance

### Bot Configuration

- **Bot Name**: Display name customers see
- **Welcome Message**: Initial greeting
- **System Prompt**: Control bot behavior & tone
- **Color Scheme**: Customize UI theme
- **Active Status**: Turn bot on/off

### Conversation Logging

- All conversations tracked
- Customer name, message, bot response logged
- Analytics dashboard shows recent chats

### Security & Privacy

- Company-specific data filtering
- No cross-company data leakage
- Login required for admin features
- CSRF protection on all POST requests

## API Endpoints

### Public (No Auth Required)

- `GET /` - Landing page
- `GET /chat/<company_name>/` - Public chat interface
- `POST /chat/<company_name>/voice/` - Voice chat API
- `POST /chat/<company_name>/text/` - Text chat API

### Authentication

- `GET /login/` - Login page
- `POST /login/` - Login
- `GET /signup/` - Signup page
- `POST /signup/` - Create account
- `GET /logout/` - Logout

### Company Dashboard (Login Required)

- `GET /dashboard/` - Main dashboard
- `POST /dashboard/` - Upload content, update settings
- `GET /bot/` - Bot tester
- `POST /voice-chat/` - Internal voice API
- `POST /text-chat/` - Internal text API

## Database Models

### KnowledgeBase

- `company` (ForeignKey to User)
- `content` (TextField) - Knowledge text
- `embedding` (VectorField) - AI embedding
- `source_type` - 'text' or 'pdf'
- `source_filename` - Original filename

### BotConfiguration

- `company` (OneToOneField to User)
- `bot_name`, `welcome_message`, `system_prompt`
- `color_scheme` - UI theme
- `is_active` - Enable/disable bot

### ConversationHistory

- `company` (ForeignKey to User)
- `customer_message`, `bot_response`
- `customer_name`, `created_at`

## Testing

### Test Text Chat

1. Login to dashboard
2. Click "Test Bot" → Text mode
3. Type a question
4. Bot responds based on uploaded knowledge

### Test Voice Chat

1. Click "Voice" mode
2. Click "Start Recording"
3. Speak your question
4. Click "Stop Recording"
5. Bot responds with text

### Test Public Chat

1. Navigate to `/chat/yourcompanyname/`
2. Try both text and voice modes
3. Verify responses match your knowledge base

## Troubleshooting

### Issue: Embeddings failing

**Solution**: Wait a minute - HuggingFace model may be loading. It retries 3 times.

### Issue: Audio not recording

**Solution**: Check browser permissions (Chrome → Settings → Privacy → Microphone)

### Issue: Bot returns "I don't know"

**Solution**: Upload more relevant knowledge to the knowledge base

### Issue: Database connection error

**Solution**: Verify `.env` credentials and pgvector extension installed

## Deployment

### Using Gunicorn & Nginx

```bash
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

### Docker Deployment

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Future Enhancements

- [ ] Multi-language support
- [ ] Advanced analytics with charts
- [ ] Email notifications for conversations
- [ ] Integration with support tickets
- [ ] Custom domain support
- [ ] Rate limiting
- [ ] Advanced bot personalization

## Support

For issues or questions:

1. Check logs: `python manage.py runserver` will show detailed errors
2. Verify API keys are correct
3. Ensure database is connected
4. Check network/firewall settings

## License

MIT License - Use freely for personal and commercial projects.

---

**Built with ❤️ using Django, AI, and privacy-first principles**
