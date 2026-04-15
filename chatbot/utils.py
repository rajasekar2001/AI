import requests
from groq import Groq
from django.conf import settings
from sentence_transformers import SentenceTransformer
import speech_recognition as sr
import pyttsx3
import threading
import tempfile
import os
from gtts import gTTS
from playsound import playsound
import logging

logger = logging.getLogger(__name__)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str):
    if not text:
        return []
    embedding = embedding_model.encode(text)
    return embedding.tolist()

def transcribe_audio(audio_file):
    if not settings.GROQ_API_KEY:
        raise Exception("GROQ_API_KEY missing in settings")
    client = Groq(api_key=settings.GROQ_API_KEY)
    transcription = client.audio.transcriptions.create(
        file=("audio.wav", audio_file.read()),
        model="whisper-large-v3",
    )
    return transcription.text

def get_llm_answer(query, context, bot_config=None):
    if not settings.GROQ_API_KEY:
        raise Exception("GROQ_API_KEY missing in settings")
    client = Groq(api_key=settings.GROQ_API_KEY)
    if bot_config:
        system_prompt = bot_config.system_prompt.replace(
            "{company_name}", bot_config.company.username
        )
    else:
        system_prompt = (
            "You are an intelligent invoice assistant. "
            "Answer ONLY using the provided context. "
            "Do NOT say 'context is missing' or 'cut short'. "
            "If the answer is not available, say: "
            "'Sorry, I couldn't find that information in the invoice.' "
            "Give clear, direct, and short answers."
        )

    user_message = f"""
Context:
{context}

Question:
{query}

Instructions:
- Answer only from context
- Be specific
- If question is about 'Sr' or 'Serial Number', explain it as item number
"""

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        model="llama-3.1-8b-instant",
        temperature=0.3
    )
    return chat_completion.choices[0].message.content

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = None
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
        except Exception as e:
            logger.warning(f"TTS engine init failed: {e}")
    
    def listen(self, timeout=5):
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio)
                return True, text
        except Exception as e:
            return False, str(e)
    
    def speak(self, text):
        if not text:
            return
        try:
            if self.tts_engine:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                    tts = gTTS(text=text, lang='en')
                    tts.save(fp.name)
                    playsound(fp.name)
                    os.unlink(fp.name)
        except Exception as e:
            logger.error(f"TTS error: {e}")
voice_assistant = VoiceAssistant()

def process_voice_command(text):
    """Process voice commands and return response"""
    text_lower = text.lower()
    commands = {
        'help': "I can help with customer support, answer questions, or navigate the website.",
        'time': f"The time is {__import__('datetime').datetime.now().strftime('%I:%M %p')}",
        'date': f"Today is {__import__('datetime').datetime.now().strftime('%B %d, %Y')}",
        'hello': "Hello! How can I assist you?",
        'thanks': "You're welcome!",
        'goodbye': "Goodbye! Have a great day!",
        'product': "Check our products page for detailed information.",
        'price': "For pricing, please contact our sales team.",
        'contact': "Contact support at support@example.com or call 1-800-123-4567."
    }
    for cmd, response in commands.items():
        if cmd in text_lower:
            return response
    return f"I heard: '{text}'. How can I help?"
