# 🚀 Quick Start Guide - VoiceAI Support Bot

## 5-Minute Setup

### Step 1: Get API Keys (Free)

1. **Groq API** (Free tier available)
   - Go to https://console.groq.com
   - Sign up with email
   - Get your API key

2. **HuggingFace Token** (Free tier available)
   - Go to https://huggingface.co/settings/tokens
   - Create new token with "read" access
   - Copy the token

### Step 2: Setup Environment

Create `.env` file in project root:

```env
# For local Supabase PostgreSQL (or any PostgreSQL)
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# API Keys from above
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_token_here
```

### Step 3: Install & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Create admin account
python manage.py createsuperuser
# Username: admin
# Password: (enter anything)

# Start server
python manage.py runserver
```

Visit: **http://localhost:8000**

## Usage Flow

### For Company Admin

```
1. Sign Up at /signup/
   ↓
2. Go to Dashboard
   ↓
3. Upload PDF or text about your company
   ↓
4. Edit bot name/settings (optional)
   ↓
5. Click "Test Bot" to verify
   ↓
6. Share the public link: /chat/yourcompanyname/
```

### For Customers

```
1. Open shared bot link
   ↓
2. Choose Text or Voice mode
   ↓
3. Ask a question
   ↓
4. Get instant AI response based on company knowledge
```

## Example: Create Support Bot for "TechCorp"

### Admin Setup (5 minutes)

```
1. Sign up with username: techcorp
2. Upload PDF: "techcorp_faq.pdf" (troubleshooting guide)
3. Add text: "Returns: 30-day money-back guarantee"
4. Set Bot Name: "TechCorp Support"
5. Set Welcome: "Hi! I'm here to help with your question"
6. Turn on bot → DONE!
```

### Customer Uses It

```
Customer goes to: http://yoursite.com/chat/techcorp/
Customer asks: "What's your return policy?"
Bot responds: "Returns: 30-day money-back guarantee" ✓
```

## Command Reference

```bash
# Start server
python manage.py runserver

# Create admin user
python manage.py createsuperuser

# Apply migrations
python manage.py migrate

# Make new migrations
python manage.py makemigrations

# Access Django admin
http://localhost:8000/admin

# Access app
http://localhost:8000
```

## Folder Structure

```
voicebot/
├── chatbot/              # Main app
│   ├── models.py        # Database schema
│   ├── views.py         # All logic
│   ├── utils.py         # AI functions
│   └── urls.py          # Routes
├── templates/           # HTML pages
├── core/                # Django config
├── manage.py           # Django CLI
└── requirements.txt    # Dependencies
```

## Key URLs

| URL                  | Purpose        | Auth? |
| -------------------- | -------------- | ----- |
| `/`                  | Home page      | No    |
| `/signup/`           | Create account | No    |
| `/login/`            | Login          | No    |
| `/dashboard/`        | Manage bot     | Yes   |
| `/bot/`              | Test bot       | Yes   |
| `/chat/companyname/` | Customer chat  | No    |

## Troubleshooting

**Error: Database connection failed**

- Check `.env` has correct credentials
- Verify PostgreSQL is running

**Error: API key invalid**

- Double-check `GROQ_API_KEY` and `HF_TOKEN` in `.env`

**Voice not working**

- Check browser microphone permissions
- Use HTTPS or localhost (https required for some browsers)

**Bot says "I don't know"**

- Upload more knowledge base content
- Verify content is relevant to question

## Next Steps

1. ✅ Deploy to Heroku/Railway/AWS
2. ✅ Add custom domain
3. ✅ Integrate with Slack/Teams
4. ✅ Add more AI models
5. ✅ Build mobile app

---

**Need help?** Check `README.md` for complete documentation
