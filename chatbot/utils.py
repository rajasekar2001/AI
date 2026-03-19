import requests
from groq import Groq
from django.conf import settings
from sentence_transformers import SentenceTransformer

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
            "You are a professional support assistant. "
            "Use ONLY the provided context to answer customer questions. "
            "If the answer is not in the context, politely say you don't know. "
            "Be brief, helpful, and professional."
        )
    user_message = f"Context:\n{context}\n\nQuestion:\n{query}"
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        model="llama-3.1-8b-instant",
    )
    return chat_completion.choices[0].message.content

# import requests
# from groq import Groq
# from django.conf import settings


# # ==========================================
# # EMBEDDING FUNCTION (HuggingFace 2026 API)
# # ==========================================

# def get_embedding(text: str):

#     hf_token = settings.HF_TOKEN

#     if not hf_token:
#         raise Exception("HF_TOKEN missing in Django settings")

#     model_id = "sentence-transformers/all-MiniLM-L6-v2"

#     api_url = f"https://router.huggingface.co/hf-inference/models/{model_id}"

#     headers = {
#         "Authorization": f"Bearer {hf_token}",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "inputs": text,
#         "options": {"wait_for_model": True}
#     }

#     response = requests.post(
#         api_url,
#         headers=headers,
#         json=payload,
#         timeout=60,
#     )

#     if response.status_code != 200:
#         raise Exception(f"HuggingFace API Error {response.status_code}: {response.text}")

#     result = response.json()

#     # The router returns nested lists
#     if isinstance(result, list):
#         return result[0]

#     raise Exception(f"Unexpected response format: {result}")

# # def get_embedding(text: str):
# #     """
# #     Generate embedding using HuggingFace Inference Router
# #     """

# #     hf_token = settings.HF_TOKEN

# #     if not hf_token:
# #         raise Exception("HF_TOKEN missing in Django settings")

# #     model_id = "sentence-transformers/all-MiniLM-L6-v2"
# #     api_url = f"https://router.huggingface.co/hf-inference/models/{model_id}"

# #     headers = {
# #         "Authorization": f"Bearer {hf_token}",
# #         "Content-Type": "application/json",
# #     }

# #     payload = {
# #         "inputs": text
# #     }

# #     try:
# #         response = requests.post(
# #             api_url,
# #             headers=headers,
# #             json=payload,
# #             timeout=30,
# #         )
# #     except requests.exceptions.RequestException as e:
# #         raise Exception(f"Network error contacting HuggingFace: {str(e)}")

# #     # Handle HTTP errors properly
# #     if response.status_code == 401:
# #         raise Exception("HuggingFace Authentication Failed (Invalid HF_TOKEN)")

# #     if response.status_code != 200:
# #         raise Exception(f"HuggingFace API Error {response.status_code}: {response.text}")

# #     result = response.json()

# #     # Normal embedding response format
# #     if isinstance(result, list):
# #         if isinstance(result[0], list):
# #             return result[0]
# #         return result

# #     raise Exception(f"Unexpected HuggingFace response format: {result}")


# # ==========================================
# # AUDIO TRANSCRIPTION (Groq Whisper)
# # ==========================================

# def transcribe_audio(audio_file):
#     """
#     Convert audio file to text using Groq Whisper
#     """

#     if not settings.GROQ_API_KEY:
#         raise Exception("GROQ_API_KEY missing in settings")

#     client = Groq(api_key=settings.GROQ_API_KEY)

#     transcription = client.audio.transcriptions.create(
#         file=("audio.wav", audio_file.read()),
#         model="whisper-large-v3",
#     )

#     return transcription.text


# # ==========================================
# # LLM RESPONSE (Groq Llama)
# # ==========================================

# def get_llm_answer(query, context, bot_config=None):
#     """
#     Generate LLM response using Groq Llama 3.1
#     """

#     if not settings.GROQ_API_KEY:
#         raise Exception("GROQ_API_KEY missing in settings")

#     client = Groq(api_key=settings.GROQ_API_KEY)

#     # Custom system prompt
#     if bot_config:
#         system_prompt = bot_config.system_prompt.replace(
#             "{company_name}", bot_config.company.username
#         )
#     else:
#         system_prompt = (
#             "You are a professional support assistant. "
#             "Use ONLY the provided context to answer customer questions. "
#             "If the answer is not in the context, politely say you don't know. "
#             "Be brief, helpful, and professional."
#         )

#     user_message = f"Context:\n{context}\n\nQuestion:\n{query}"

#     chat_completion = client.chat.completions.create(
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_message}
#         ],
#         model="llama-3.1-8b-instant",
#     )

#     return chat_completion.choices[0].message.content

# import time
# import requests
# from groq import Groq
# from django.conf import settings


# # ==============================
# # EMBEDDING FUNCTION (UPDATED 2026)
# # ==============================

# def get_embedding(text: str):

#     if not settings.HF_TOKEN:
#         raise Exception("HF_TOKEN not set in settings")

#     model_id = "sentence-transformers/all-MiniLM-L6-v2"

#     # ✅ Correct URL with f-string
#     api_url = f"https://router.huggingface.co/hf-inference/models/{model_id}"

#     headers = {
#         "Authorization": f"Bearer {settings.HF_TOKEN}",
#         "Content-Type": "application/json",
#     }

#     response = requests.post(
#         api_url,
#         headers=headers,
#         json={"inputs": text},
#         timeout=30,
#     )

#     if response.status_code != 200:
#         raise Exception(f"HuggingFace Error: {response.text}")

#     result = response.json()

#     if isinstance(result, list):
#         return result[0] if isinstance(result[0], list) else result

#     raise Exception(f"Unexpected response: {result}")

# def transcribe_audio(audio_file):
#     """Convert audio file to text using Groq Whisper API"""
#     client = Groq(api_key=settings.GROQ_API_KEY)
#     transcription = client.audio.transcriptions.create(
#         file=("sample.wav", audio_file.read()),
#         model="whisper-large-v3",
#     )
#     return transcription.text


# def get_llm_answer(query, context, bot_config=None):
#     """Generate AI response based on query and context using Groq Llama"""
#     client = Groq(api_key=settings.GROQ_API_KEY)
    
#     # Use custom system prompt from bot config if available
#     if bot_config:
#         system_prompt = bot_config.system_prompt.replace(
#             '{company_name}', bot_config.company.username
#         )
#     else:
#         system_prompt = "You are a professional support assistant. Use ONLY the provided context to answer customer questions. If the answer is not in the context, politely say you don't know. Be brief, helpful, and professional."
    
#     # Create user message with context
#     user_message = f"Context: {context}\n\nQuestion: {query}"
    
#     chat_completion = client.chat.completions.create(
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_message}
#         ],
#         model="llama-3.1-8b-instant",
#     )
#     return chat_completion.choices[0].message.content

# def get_embedding(text: str):
#     """
#     Convert text to vector embedding using HuggingFace Router API
#     """

#     if not text:
#         raise ValueError("Text for embedding cannot be empty.")

#     hf_token = getattr(settings, "HF_TOKEN", None)

#     if not hf_token:
#         raise Exception("HF_TOKEN is not configured in Django settings.")

#     model_id = "sentence-transformers/all-MiniLM-L6-v2"

#     # ✅ Correct Router Endpoint
#     api_url = f"https://router.huggingface.co/hf-inference/models/{model_id}"

#     headers = {
#         "Authorization": f"Bearer {hf_token}",
#         "Content-Type": "application/json",
#     }

#     for attempt in range(3):
#         try:
#             print(f"[Embedding] Attempt {attempt + 1}")

#             response = requests.post(
#                 api_url,
#                 headers=headers,
#                 json={"inputs": text},
#                 timeout=30,
#             )

#             # Model waking up
#             if response.status_code == 503:
#                 print("[Embedding] Model loading... retrying in 5 seconds")
#                 time.sleep(5)
#                 continue

#             if response.status_code != 200:
#                 raise Exception(
#                     f"HuggingFace Error {response.status_code}: {response.text}"
#                 )

#             result = response.json()

#             # Handle API error
#             if isinstance(result, dict) and "error" in result:
#                 raise Exception(f"HuggingFace API Error: {result['error']}")

#             # Feature extraction returns list of lists
#             if isinstance(result, list):
#                 embedding = result[0] if isinstance(result[0], list) else result
#                 print(f"[Embedding] Success. Dimension: {len(embedding)}")
#                 return embedding

#         except requests.exceptions.RequestException as e:
#             print(f"[Embedding] Network error (attempt {attempt + 1}): {str(e)}")
#             time.sleep(3)

#     raise Exception("Failed to get embedding after 3 attempts.")

# import time
# import requests
# from groq import Groq
# from django.conf import settings


# def get_embedding(text):
#     """Convert text to vector embedding using HuggingFace"""
#     model_id = "sentence-transformers/all-MiniLM-L6-v2"
#     api_url = f"https://router.huggingface.co/hf-inference/models/{model_id}/pipeline/feature-extraction"
    
#     headers = {"Authorization": f"Bearer {settings.HF_TOKEN}"}
    
#     # Try up to 3 times in case the model is "waking up"
#     for attempt in range(3):
#         try:
#             # Add debug info
#             print(f"Attempt {attempt + 1}: Calling HuggingFace API...")
#             print(f"URL: {api_url}")
#             print(f"Token present: {'Yes' if settings.HF_TOKEN else 'No'}")
            
#             response = requests.post(
#                 api_url, 
#                 headers=headers, 
#                 json={"inputs": text}, 
#                 timeout=30
#             )
            
#             # Check if response is successful
#             if response.status_code != 200:
#                 error_detail = response.text[:200] if response.text else "No details"
#                 print(f"HuggingFace API Error (Status {response.status_code}): {error_detail}")
#                 if attempt < 2:
#                     time.sleep(3)
#                     continue
#                 raise Exception(f"HuggingFace API returned status {response.status_code}: {error_detail}")
            
#             # Try to parse JSON
#             try:
#                 result = response.json()
#             except ValueError as e:
#                 print(f"JSON Parse Error: {response.text[:200]}")
#                 if attempt < 2:
#                     time.sleep(3)
#                     continue
#                 raise Exception(f"Failed to parse HuggingFace response: {str(e)}")
            
#             # Case 1: Model is loading
#             if isinstance(result, dict) and "estimated_time" in result:
#                 wait_time = result.get("estimated_time", 5)
#                 print(f"Model loading, waiting {wait_time} seconds...")
#                 time.sleep(wait_time)
#                 continue
                
#             # Case 2: Error in API (like wrong token)
#             if isinstance(result, dict) and "error" in result:
#                 error_msg = result['error']
#                 print(f"API Error: {error_msg}")
#                 raise Exception(f"HuggingFace Error: {error_msg}")

#             # Case 3: Success! 
#             # HuggingFace usually returns a list of lists for feature extraction [[val, val]]
#             if isinstance(result, list):
#                 print(f"Success! Got embedding with {len(result)} dimensions")
#                 if len(result) > 0 and isinstance(result[0], list):
#                     return result[0]  # Take the inner list
#                 return result
                
#         except requests.exceptions.RequestException as e:
#             print(f"Request Exception (attempt {attempt + 1}): {str(e)}")
#             if attempt < 2:
#                 time.sleep(3)
#                 continue
#             raise Exception(f"Network error calling HuggingFace: {str(e)}")
            
#     raise Exception("HuggingFace model failed to load after multiple retries.")


# def transcribe_audio(audio_file):
#     """Convert audio file to text using Groq Whisper API"""
#     client = Groq(api_key=settings.GROQ_API_KEY)
#     transcription = client.audio.transcriptions.create(
#         file=("sample.wav", audio_file.read()),
#         model="whisper-large-v3",
#     )
#     return transcription.text


# def get_llm_answer(query, context, bot_config=None):
#     """Generate AI response based on query and context using Groq Llama"""
#     client = Groq(api_key=settings.GROQ_API_KEY)
    
#     # Use custom system prompt from bot config if available
#     if bot_config:
#         system_prompt = bot_config.system_prompt.replace(
#             '{company_name}', bot_config.company.username
#         )
#     else:
#         system_prompt = "You are a professional support assistant. Use ONLY the provided context to answer customer questions. If the answer is not in the context, politely say you don't know. Be brief, helpful, and professional."
    
#     # Create user message with context
#     user_message = f"Context: {context}\n\nQuestion: {query}"
    
#     chat_completion = client.chat.completions.create(
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_message}
#         ],
#         model="llama-3.1-8b-instant",
#     )
#     return chat_completion.choices[0].message.content