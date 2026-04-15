from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from .models import KnowledgeBase, BotConfiguration, ConversationHistory
from .utils import get_embedding, transcribe_audio, get_llm_answer, process_voice_command, voice_assistant
from pgvector.django import CosineDistance
from pypdf import PdfReader
import json
import base64
import tempfile
import os
from django.utils import timezone

def landing_page(request):
    """Home page showing features and call-to-action"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')

def signup(request):
    """Company signup with custom form"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create default bot configuration for new company
            BotConfiguration.objects.create(company=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_view(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'registration/login.html', {'error': 'Invalid credentials'})
    return render(request, 'registration/login.html')

def logout_view(request):
    """Custom logout view"""
    if request.method == 'POST':
        logout(request)
        return redirect('landing')
    logout(request)
    return redirect('landing')

@login_required(login_url='login')
def dashboard(request):
    COLOR_SCHEMES = ['blue', 'green', 'purple', 'red']

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'upload_text':
            content = request.POST.get('content', '').strip()
            if not content:
                return JsonResponse({'status': 'error', 'message': 'Empty text'}, status=400)
            process_and_save_chunk(request.user, content, 'text', None)
            return JsonResponse({'status': 'success', 'message': 'Text uploaded successfully'})
        elif action == 'upload_file':
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return JsonResponse({'status': 'error', 'message': 'No file uploaded'}, status=400)
            filename = uploaded_file.name
            file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
            content_type = uploaded_file.content_type
            try:
                if file_extension == 'pdf' or content_type == 'application/pdf':
                    return handle_pdf_upload(request.user, uploaded_file)
                elif file_extension in ['jpg','jpeg','png','gif','bmp','webp'] or content_type.startswith('image/'):
                    return handle_image_upload(request.user, uploaded_file)
                elif file_extension in ['txt'] or content_type == 'text/plain':
                    return handle_text_file_upload(request.user, uploaded_file)
                elif file_extension in ['docx']:
                    return handle_word_document_upload(request.user, uploaded_file)
                else:
                    return JsonResponse({'status': 'error', 'message': f'Unsupported file type: {file_extension}'}, status=400)
            except Exception as e:
                print("Upload Error:", e)
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        elif action == 'update_config':
            try:
                bot_config, _ = BotConfiguration.objects.get_or_create(company=request.user)
                bot_config.bot_name = request.POST.get('bot_name') or bot_config.bot_name
                bot_config.welcome_message = request.POST.get('welcome_message') or bot_config.welcome_message
                bot_config.system_prompt = request.POST.get('system_prompt') or bot_config.system_prompt
                selected_color = request.POST.get('color_scheme')
                if selected_color in COLOR_SCHEMES:
                    bot_config.color_scheme = selected_color
                bot_config.is_active = request.POST.get('is_active') == 'on'
                bot_config.save()
                return JsonResponse({'status': 'success', 'message': 'Bot configuration updated'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        elif action == 'delete_knowledge':
            knowledge_id = request.POST.get('knowledge_id')
            try:
                knowledge = KnowledgeBase.objects.get(id=int(knowledge_id), company=request.user)
                knowledge.delete()
                return JsonResponse({'status': 'success', 'message': 'Knowledge deleted'})
            except KnowledgeBase.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)
    knowledge = KnowledgeBase.objects.filter(company=request.user).order_by('-created_at')
    bot_config, _ = BotConfiguration.objects.get_or_create(company=request.user)
    recent_conversations = ConversationHistory.objects.filter(
        company=request.user
    ).order_by('-created_at')[:20]
    chatbot_conversations = ConversationHistory.objects.filter(
        company=request.user, conversation_type='chatbot'
    ).count()
    voicebot_conversations = ConversationHistory.objects.filter(
        company=request.user, conversation_type='voicebot'
    ).count()
    voicecall_conversations = ConversationHistory.objects.filter(
        company=request.user, conversation_type='voicecall'
    ).count()
    total_conversations = chatbot_conversations + voicebot_conversations + voicecall_conversations
    total_voice_conversations = voicebot_conversations + voicecall_conversations
    today = timezone.now().date()
    today_conversations = ConversationHistory.objects.filter(
        company=request.user,
        created_at__date=today
    ).count()
    voicecalls = ConversationHistory.objects.filter(
        company=request.user, 
        conversation_type='voicecall',
        call_duration__isnull=False
    )
    if voicecalls.exists():
        avg_duration = voicecalls.values_list('call_duration', flat=True)
        avg_call_duration = str(sum(avg_duration) // len(avg_duration)) + 's'
    else:
        avg_call_duration = '0s'
    context = {
        'knowledge_count': knowledge.count(),
        'knowledge': knowledge,
        'bot_config': bot_config,
        'recent_conversations': recent_conversations,
        'color_schemes': COLOR_SCHEMES,
        'chatbot_conversations': chatbot_conversations,
        'voicebot_conversations': voicebot_conversations,
        'voicecall_conversations': voicecall_conversations,
        'total_conversations': total_conversations,
        'total_voice_conversations': total_voice_conversations,
        'today_conversations': today_conversations,
        'avg_call_duration': avg_call_duration,
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def dashboard_stats_api(request):
    user = request.user
    chatbot_conversations = ConversationHistory.objects.filter(company=user, conversation_type='chatbot').count()
    voicebot_conversations = ConversationHistory.objects.filter(company=user, conversation_type='voicebot').count()
    voicecall_conversations = ConversationHistory.objects.filter(company=user, conversation_type='voicecall').count()
    today_conversations = ConversationHistory.objects.filter(
        company=user, created_at__date=timezone.now().date()
    ).count()
    voicecalls = ConversationHistory.objects.filter(company=user, conversation_type='voicecall', call_duration__isnull=False)
    if voicecalls.exists():
        avg_duration = voicecalls.values_list('call_duration', flat=True)
        avg_call_duration = str(sum(avg_duration) // len(avg_duration)) + 's'
    else:
        avg_call_duration = '0s'
    return JsonResponse({
        'chatbot_conversations': chatbot_conversations,
        'voicebot_conversations': voicebot_conversations,
        'voicecall_conversations': voicecall_conversations,
        'total_conversations': chatbot_conversations + voicebot_conversations + voicecall_conversations,
        'total_voice_conversations': voicebot_conversations + voicecall_conversations,
        'today_conversations': today_conversations,
        'avg_call_duration': avg_call_duration,
    })

def handle_pdf_upload(user, pdf_file):
    """Handle PDF file upload and extract text"""
    try:
        from pypdf import PdfReader
        pdf_file.seek(0)
        header = pdf_file.read(4)
        pdf_file.seek(0)
        if not header.startswith(b'%PDF'):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid PDF file format.'
            }, status=400)
        reader = PdfReader(pdf_file)
        all_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                all_text += page_text + " "
        if not all_text.strip():
            return JsonResponse({'status': 'error', 'message': 'No text found in PDF'}, status=400)
        chunks = [all_text[i:i+1000] for i in range(0, len(all_text), 1000)]
        for chunk in chunks:
            if chunk.strip():
                process_and_save_chunk(user, chunk, 'pdf', pdf_file.name)
        return JsonResponse({
            'status': 'success',
            'message': f'PDF uploaded successfully! Added {len(chunks)} chunks.'
        })
    except ImportError:
        return JsonResponse({
            'status': 'error',
            'message': 'PDF processing library not available'
        }, status=500)
    except Exception as e:
        raise e

def handle_image_upload(user, image_file):

    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np

    pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract-OCR\tesseract.exe"
    img = Image.open(image_file)
    if img.mode != "RGB":
        img = img.convert("RGB")
    img_np = np.array(img)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(thresh, config='--psm 6')
    print("OCR OUTPUT:", repr(text))
    if not text.strip():
        return JsonResponse({
            'status': 'error',
            'message': 'No text detected. Try a clearer image.'
        }, status=400)
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    for chunk in chunks:
        process_and_save_chunk(user, chunk, 'image', image_file.name)
    return JsonResponse({
        'status': 'success',
        'message': f'Extracted {len(chunks)} chunks from image'
    })
    
def handle_text_file_upload(user, text_file):
    """Handle plain text file upload"""
    try:
        content = text_file.read().decode('utf-8')
        if not content.strip():
            return JsonResponse({
                'status': 'error',
                'message': 'Text file is empty'
            }, status=400)
        chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
        for chunk in chunks:
            if chunk.strip():
                process_and_save_chunk(user, chunk, 'text', text_file.name)
        return JsonResponse({
            'status': 'success',
            'message': f'Text file uploaded successfully! Added {len(chunks)} chunks.'
        })
    except UnicodeDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Could not decode text file. Please ensure it\'s UTF-8 encoded.'
        }, status=400)
    except Exception as e:
        raise e

def handle_word_document_upload(user, doc_file):
    """Handle Word document upload"""
    try:
        import docx2txt
        text = docx2txt.process(doc_file)
        if not text.strip():
            return JsonResponse({
                'status': 'error',
                'message': 'No text found in Word document'
            }, status=400)
        chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
        for chunk in chunks:
            if chunk.strip():
                process_and_save_chunk(user, chunk, 'word', doc_file.name)
        return JsonResponse({
            'status': 'success',
            'message': f'Word document uploaded successfully! Added {len(chunks)} chunks.'
        })
    except ImportError:
        return JsonResponse({
            'status': 'error',
            'message': 'Word document processing library (docx2txt) not available'
        }, status=500)
    except Exception as e:
        raise e
    
def process_and_save_chunk(user, text, source_type='text', filename=None):
    """Process text and save to knowledge base with embedding"""
    try:
        if not text.strip():
            return
        vector = get_embedding(text)
        KnowledgeBase.objects.create(
            company=user,
            content=text,
            embedding=vector,
            source_type=source_type,
            source_filename=filename
        )
    except Exception as e:
        print(f"Error processing chunk: {e}")
        raise

def public_chat_page(request, company_name):
    """Customer page to chat with a specific company's bot"""
    company = get_object_or_404(User, username=company_name)
    bot_config, _ = BotConfiguration.objects.get_or_create(company=company)
    if not bot_config.is_active:
        return render(request, 'public_chat.html', {
            'error': 'This chatbot is currently offline.',
            'company': company
        })
    return render(request, 'public_chat.html', {
        'company': company,
        'bot_config': bot_config
    })

@csrf_exempt
@require_http_methods(["POST"])
def public_voice_chat(request, company_name):
    """API endpoint for customers to chat with a company's bot via voice"""
    try:
        company = get_object_or_404(User, username=company_name)
        try:
            bot_config = company.bot_config
            if not bot_config.is_active:
                return JsonResponse({
                    'error': 'This chatbot is currently offline'
                }, status=503)
        except BotConfiguration.DoesNotExist:
            return JsonResponse({
                'error': 'Chatbot not configured'
            }, status=503)
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return JsonResponse({'error': 'No audio file received'}, status=400)
        source = request.POST.get('source', 'voicebot')
        user_text = transcribe_audio(audio_file)
        try:
            query_vector = get_embedding(user_text)
        except Exception as e:
            print(f"Embedding error: {e}")
            return JsonResponse({
                'transcript': user_text,
                'answer': "I'm sorry, I'm having trouble processing your request. Please try again."
            })
        context_chunks = KnowledgeBase.objects.filter(company=company).order_by(
            CosineDistance('embedding', query_vector)
        )[:3]
        context_text = " ".join([c.content for c in context_chunks])
        ai_answer = get_llm_answer(user_text, context_text, bot_config)
        ConversationHistory.objects.create(
            company=company,
            customer_message=user_text,
            bot_response=ai_answer,
            customer_name='Customer',
            conversation_type=source
        )
        return JsonResponse({
            'transcript': user_text,
            'answer': ai_answer
        })
    except Exception as e:
        print(f"Public API Error: {e}")
        return JsonResponse({
            'error': 'Internal server error. Please try again.'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def public_text_chat(request, company_name):
    """API endpoint for text-based chat"""
    try:
        company = get_object_or_404(User, username=company_name)
        try:
            bot_config = company.bot_config
            if not bot_config.is_active:
                return JsonResponse({'error': 'This chatbot is currently offline'}, status=503)
        except BotConfiguration.DoesNotExist:
            return JsonResponse({'error': 'Chatbot not configured'}, status=503)
        data = json.loads(request.body)
        user_text = data.get('message', '').strip()
        if not user_text:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        source = data.get('source', 'chatbot')
        try:
            query_vector = get_embedding(user_text)
        except Exception as e:
            print(f"Embedding error: {e}")
            return JsonResponse({
                'answer': "I'm having trouble processing your question. Please try again."
            })
        context_chunks = KnowledgeBase.objects.filter(company=company).order_by(
            CosineDistance('embedding', query_vector)
        )[:3]
        context_text = " ".join([c.content for c in context_chunks])
        ai_answer = get_llm_answer(user_text, context_text, bot_config)
        ConversationHistory.objects.create(
            company=company,
            customer_message=user_text,
            bot_response=ai_answer,
            customer_name='Customer',
            conversation_type=source
        )
        return JsonResponse({'answer': ai_answer})
    except Exception as e:
        print(f"Text chat error: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@login_required(login_url='login')
def chat_page(request):
    """Internal chat page for company to test their bot"""
    bot_config, _ = BotConfiguration.objects.get_or_create(company=request.user)
    return render(request, 'chat.html', {'bot_config': bot_config})


@csrf_exempt
@login_required(login_url='login')
@require_http_methods(["POST"])
def voice_chat_view(request):
    """Internal voice API for company to test bot with full AI capabilities"""
    try:
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return JsonResponse({'error': 'No audio file received'}, status=400)
        user_text = transcribe_audio(audio_file)
        try:
            query_vector = get_embedding(user_text)
        except Exception as e:
            print(f"Embedding error: {e}")
            return JsonResponse({
                'transcript': user_text,
                'answer': "I'm having trouble processing that. Please try again."
            })
        context_chunks = KnowledgeBase.objects.filter(company=request.user).order_by(
            CosineDistance('embedding', query_vector)
        )[:3]
        context_text = " ".join([c.content for c in context_chunks])
        bot_config, _ = BotConfiguration.objects.get_or_create(company=request.user)
        ai_answer = get_llm_answer(user_text, context_text, bot_config)
        voice_assistant.speak(ai_answer)
        return JsonResponse({
            'transcript': user_text,
            'answer': ai_answer
        })
    except Exception as e:
        print(f"Voice chat error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required(login_url='login')
@require_http_methods(["POST"])
def text_chat_view(request):
    """Internal text API for company to test bot"""
    try:
        data = json.loads(request.body)
        user_text = data.get('message', '').strip()
        if not user_text:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        try:
            query_vector = get_embedding(user_text)
        except Exception as e:
            print(f"Embedding error: {e}")
            return JsonResponse({
                'answer': "I'm having trouble processing that. Please try again."
            })
        context_chunks = KnowledgeBase.objects.filter(company=request.user).order_by(
            CosineDistance('embedding', query_vector)
        )[:3]
        context_text = " ".join([c.content for c in context_chunks])
        bot_config, _ = BotConfiguration.objects.get_or_create(company=request.user)
        ai_answer = get_llm_answer(user_text, context_text, bot_config)
        return JsonResponse({'answer': ai_answer})
    except Exception as e:
        print(f"Text chat error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def voice_assistant_interface(request):
    """Voice-enabled chat interface for authenticated users to test the bot"""
    return render(request, 'chat.html', {'voice_mode': True, 'company_name': request.user.username})

@csrf_exempt
@require_http_methods(["POST"])
def process_voice_input(request):
    """API endpoint to process text-based voice input (simpler version)"""
    try:
        data = json.loads(request.body) if request.body else {}
        if 'text' in data:
            user_text = data['text']
        else:
            success, user_text = voice_assistant.listen(timeout=5)
            if not success:
                return JsonResponse({'success': False, 'error': user_text}, status=400)
        response_text = process_voice_command(user_text)
        voice_assistant.speak(response_text)
        return JsonResponse({
            'success': True,
            'user_text': user_text,
            'bot_response': response_text
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def public_voice_chat_api(request, company_name):
    """API endpoint for customers to chat with a company's bot via voice"""
    try:
        company = get_object_or_404(User, username=company_name)
        try:
            bot_config = company.bot_config
            if not bot_config.is_active:
                return JsonResponse({
                    'error': 'This chatbot is currently offline'
                }, status=503)
        except BotConfiguration.DoesNotExist:
            return JsonResponse({
                'error': 'Chatbot not configured'
            }, status=503)
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return JsonResponse({'error': 'No audio file received'}, status=400)
        user_text = transcribe_audio(audio_file)
        try:
            query_vector = get_embedding(user_text)
        except Exception as e:
            print(f"Embedding error: {e}")
            return JsonResponse({
                'transcript': user_text,
                'answer': "I'm sorry, I'm having trouble processing your request. Please try again."
            })
        context_chunks = KnowledgeBase.objects.filter(company=company).order_by(
            CosineDistance('embedding', query_vector)
        )[:3]
        context_text = " ".join([c.content for c in context_chunks])
        ai_answer = get_llm_answer(user_text, context_text, bot_config)
        ConversationHistory.objects.create(
            company=company,
            customer_message=user_text,
            bot_response=ai_answer,
            customer_name='Voice Customer'
        )
        return JsonResponse({
            'transcript': user_text,
            'answer': ai_answer
        })
    except Exception as e:
        print(f"Public API Error: {e}")
        return JsonResponse({
            'error': 'Internal server error. Please try again.'
        }, status=500)

def public_voice_chat_interface(request, company_name):
    """Public voice chat interface for customers"""
    return render(request, 'public_chat.html', {
        'voice_mode': True,
        'company_name': company_name
    })

@csrf_exempt
@require_http_methods(["POST"])
def process_text_input(request):
    """API endpoint to process text input (for typing interface)"""
    try:
        data = json.loads(request.body)
        user_text = data.get('text', '')
        if not user_text:
            return JsonResponse({'error': 'No text provided'}, status=400)
        if request.user.is_authenticated:
            try:
                query_vector = get_embedding(user_text)
                context_chunks = KnowledgeBase.objects.filter(company=request.user).order_by(
                    CosineDistance('embedding', query_vector)
                )[:3]
                context_text = " ".join([c.content for c in context_chunks])
                bot_config, _ = BotConfiguration.objects.get_or_create(company=request.user)
                ai_answer = get_llm_answer(user_text, context_text, bot_config)
            except Exception as e:
                print(f"Error processing with AI: {e}")
                ai_answer = process_voice_command(user_text)
        else:
            ai_answer = process_voice_command(user_text)
        
        return JsonResponse({
            'success': True,
            'response': ai_answer
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def voice_call_interface(request):
    """Voice calling interface for admins (company testing)"""
    return render(request, 'voice_call_modal.html', {
        'company_name': request.user.username,
        'bot_config': BotConfiguration.objects.get_or_create(company=request.user)[0],
        'is_admin': True
    })

def customer_voice_call(request, company_name):
    """Voice calling interface for customers"""
    try:
        company = get_object_or_404(User, username=company_name)
        bot_config = BotConfiguration.objects.get(company=company)
        return render(request, 'voice_call_modal.html', {
            'company_name': company_name,
            'bot_config': bot_config,
            'company': company,
            'is_admin': False
        })
    except BotConfiguration.DoesNotExist:
        return render(request, 'public_chat.html', {
            'error': 'Chatbot not configured',
            'company': {'username': company_name}
        })

@csrf_exempt
@require_http_methods(["POST"])
def process_voice_stream(request):
    """Process streaming voice data for authenticated users"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        data = json.loads(request.body)
        user_text = data.get('text', '').strip()
        source = data.get('source', 'voicecall')
        if not user_text:
            return JsonResponse({'error': 'No text data'}, status=400)
        company = request.user
        bot_config, _ = BotConfiguration.objects.get_or_create(company=company)
        try:
            query_vector = get_embedding(user_text)
            context_chunks = KnowledgeBase.objects.filter(company=company).order_by(
                CosineDistance('embedding', query_vector)
            )[:3]
            context_text = " ".join([c.content for c in context_chunks])
        except Exception as e:
            print(f"Embedding error: {e}")
            context_text = ""
        ai_text_response = get_llm_answer(user_text, context_text, bot_config)
        audio_response = text_to_speech_bytes(ai_text_response)
        ConversationHistory.objects.create(
            company=company,
            customer_message=user_text,
            bot_response=ai_text_response,
            customer_name='Admin Tester',
            conversation_type=source
        )
        return JsonResponse({
            'success': True,
            'user_text': user_text,
            'bot_response': ai_text_response,
            'audio_response': base64.b64encode(audio_response).decode('utf-8') if audio_response else ''
        })
    except Exception as e:
        print(f"Voice stream error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def process_customer_voice_stream(request, company_name):
    """Process voice input and return voice response"""
    try:
        company = get_object_or_404(User, username=company_name)
        bot_config = BotConfiguration.objects.get(company=company)
        data = json.loads(request.body)
        user_text = data.get('text', '').strip()
        source = data.get('source', 'voicecall')
        if not user_text:
            return JsonResponse({'error': 'No text provided'}, status=400)
        print(f"📝 Processing question: {user_text}")
        context_text = ""
        try:
            user_words = set(user_text.lower().split())
            relevant_items = []
            for item in KnowledgeBase.objects.filter(company=company):
                content_lower = item.content.lower()
                score = sum(1 for word in user_words if word in content_lower)
                if score > 0:
                    relevant_items.append((score, item.content))
            relevant_items.sort(reverse=True)
            if relevant_items:
                context_text = " ".join([item[1][:500] for item in relevant_items[:3]])
                print(f"📚 Found context: {context_text[:100]}...")
            else:
                print("📚 No context found")
        except Exception as e:
            print(f"Knowledge base error: {e}")
        ai_response = get_llm_answer(user_text, context_text, bot_config)
        print(f"🤖 AI Response: {ai_response}")
        audio_bytes = text_to_speech_bytes(ai_response)
        ConversationHistory.objects.create(
            company=company,
            customer_message=user_text,
            bot_response=ai_response,
            customer_name='Voice Customer',
            conversation_type=source
        )
        return JsonResponse({
            'success': True,
            'user_text': user_text,
            'bot_response': ai_response,
            'audio_response': base64.b64encode(audio_bytes).decode('utf-8') if audio_bytes else ''
        })
    except BotConfiguration.DoesNotExist:
        return JsonResponse({'error': 'Bot not configured'}, status=404)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

def text_to_speech_bytes(text):
    """Convert text to audio bytes using gTTS"""
    from gtts import gTTS
    import io
    
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes.read()
    except Exception as e:
        print(f"TTS bytes error: {e}")
        return b''