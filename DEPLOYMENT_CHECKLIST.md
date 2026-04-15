# 📋 VoiceAI Setup Checklist

## Pre-Deployment Verification

Use this checklist to ensure everything is properly configured before going live.

### 🔐 Environment & Secrets

- [ ] `.env` file created with all required variables
- [ ] `GROQ_API_KEY` is set and valid
- [ ] `HF_TOKEN` is set and valid
- [ ] Database credentials are correct
- [ ] `.env` is in `.gitignore` (never commit secrets!)

### 📊 Database

- [ ] PostgreSQL running and accessible
- [ ] pgvector extension installed: `CREATE EXTENSION IF NOT EXISTS vector;`
- [ ] Migrations applied: `python manage.py migrate`
- [ ] Database tables created successfully
- [ ] Test database connection

### 🐍 Python Environment

- [ ] Virtual environment created and activated
- [ ] All requirements installed: `pip install -r requirements.txt`
- [ ] Python 3.9+ installed
- [ ] Django version is 6.0
- [ ] All imports working (test: `python manage.py check`)

### 🏗️ Django Configuration

- [ ] `ALLOWED_HOSTS` configured for your domain
- [ ] `SECRET_KEY` is set (production should be random, not default)
- [ ] `DEBUG=False` for production
- [ ] CSRF settings correct
- [ ] CORS headers configured if needed
- [ ] Static files configured

### 🎨 Templates & Static Files

- [ ] All HTML templates present in `/templates/`
  - [ ] `landing.html`
  - [ ] `chat.html`
  - [ ] `dashboard.html`
  - [ ] `public_chat.html`
  - [ ] `registration/login.html`
  - [ ] `registration/signup.html`
- [ ] Tailwind CSS CDN links working
- [ ] No 404 errors on page load

### 🤖 AI/ML Features

- [ ] Groq Whisper (speech-to-text) endpoint working
- [ ] Groq Llama 3 (LLM) endpoint working
- [ ] HuggingFace embeddings endpoint working
- [ ] Test embedding generation with sample text
- [ ] Test LLM response generation with sample prompt

### 🧪 Testing

**Test Admin Panel:**

- [ ] Admin can sign up
- [ ] Admin can login
- [ ] Admin can access dashboard
- [ ] Admin can upload PDF (try sample PDF)
- [ ] Admin can upload text content
- [ ] Admin can edit bot settings
- [ ] Admin can delete knowledge items

**Test Company Chat:**

- [ ] Customer can access public chat URL
- [ ] Customer can send text message
- [ ] Bot responds with relevant answer
- [ ] Bot says "I don't know" for unknown topics

**Test Voice Features:**

- [ ] Microphone permissions working
- [ ] Audio recording works
- [ ] Audio transcription works
- [ ] Bot responds to voice input
- [ ] Voice quality is acceptable

### 📱 UI/UX Verification

- [ ] Landing page displays correctly
- [ ] All buttons functional
- [ ] Forms validate input
- [ ] Error messages display properly
- [ ] Mobile responsive design works
- [ ] Dark theme renders correctly

### 🔒 Security

- [ ] CSRF tokens present on all POST forms
- [ ] Login required for admin functions
- [ ] Company data isolated (no cross-company leakage)
- [ ] Session timeout configured
- [ ] Password hashing enabled
- [ ] Sensitive data not in logs

### ⚡ Performance

- [ ] Page load time < 3 seconds
- [ ] Database queries optimized
- [ ] No N+1 query problems
- [ ] Knowledge base search is fast
- [ ] API response time < 2 seconds

### 📝 Logging & Monitoring

- [ ] Error logging configured
- [ ] Request logging enabled
- [ ] Bot response logging working
- [ ] Conversation history being saved
- [ ] Errors visible in console/logs

### 🚀 Deployment Ready

- [ ] All tests passing
- [ ] No migration warnings
- [ ] Static files collected: `python manage.py collectstatic`
- [ ] Gunicorn/uWSGI configured
- [ ] Environment variables set in production
- [ ] Database backup configured
- [ ] Health check endpoint working
- [ ] Monitoring/alerting set up

### 📚 Documentation

- [ ] README.md complete and accurate
- [ ] QUICKSTART.md has clear instructions
- [ ] API endpoints documented
- [ ] Environment variables documented
- [ ] Troubleshooting guide included

### 🎯 Post-Deployment

- [ ] Monitor error logs
- [ ] Track conversation metrics
- [ ] Gather user feedback
- [ ] Plan feature improvements
- [ ] Schedule regular backups

## Verification Commands

Run these commands to verify your setup:

```bash
# Check Django setup
python manage.py check

# Run tests (if available)
python manage.py test

# Check migrations
python manage.py showmigrations

# Test database connection
python manage.py dbshell

# Run development server
python manage.py runserver

# Create test admin
python manage.py createsuperuser --username testadmin
```

## Quick Validation Requests

Use curl or Postman to test APIs:

```bash
# Test embeddings endpoint
curl -X POST "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2" \
  -H "Authorization: Bearer YOUR_HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "test text"}'

# Test Groq API
curl -X POST "https://api.groq.com/openai/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3-8b-8192",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Deployment Platforms

Recommended for different scales:

- **Hobby/Testing**: Heroku, Railway, Render
- **Small Production**: Digital Ocean, Linode
- **Medium/Large**: AWS, Google Cloud, Azure
- **Enterprise**: Kubernetes, self-hosted

## Final Notes

✅ **Before Going Live:**

1. Change Django `SECRET_KEY` to a random value
2. Set `DEBUG=False`
3. Configure `ALLOWED_HOSTS` with your domain
4. Set up HTTPS/SSL
5. Configure email for password resets
6. Set up database backups
7. Monitor error logs

✅ **Performance Tips:**

- Use CDN for static files
- Enable database connection pooling
- Cache embeddings if possible
- Use pagination for large datasets
- Monitor API rate limits

---

**Last Updated**: January 2026  
**Status**: ✅ Ready for Production
