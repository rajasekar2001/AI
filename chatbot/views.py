from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from .models import KnowledgeBase, BotConfiguration, ConversationHistory
from .utils import get_embedding, transcribe_audio, get_llm_answer
from pgvector.django import CosineDistance
from pypdf import PdfReader
import json
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract-OCR\tesseract.exe"

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
    # Allow GET requests too
    logout(request)
    return redirect('landing')


# ============ DASHBOARD VIEWS (Company Backend) ============

# @login_required(login_url='login')
# def dashboard(request):
#     """Company dashboard to manage knowledge base and bot settings"""

#     COLOR_SCHEMES = ['blue', 'green', 'purple', 'red']

#     if request.method == 'POST':
#         action = request.POST.get('action')

#         # Text Upload
#         if action == 'upload_text':
#             content = request.POST.get('content', '').strip()
#             if content:
#                 process_and_save_chunk(request.user, content, 'text', None)
#                 return JsonResponse({'status': 'success', 'message': 'Text uploaded successfully'})

#         # File Upload (supports multiple formats)
#         elif action == 'upload_file':
#             uploaded_file = request.FILES.get('file')
#             if not uploaded_file:
#                 return JsonResponse({'status': 'error', 'message': 'No file uploaded'}, status=400)
            
#             file_extension = uploaded_file.name.split('.')[-1].lower()
#             file_content_type = uploaded_file.content_type
            
#             try:
#                 # Handle different file types
#                 if file_extension == 'pdf' or file_content_type == 'application/pdf':
#                     return handle_pdf_upload(request.user, uploaded_file)
                
#                 elif file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp'] or file_content_type.startswith('image/'):
#                     return handle_image_upload(request.user, uploaded_file)
                
#                 elif file_extension in ['txt', 'text'] or file_content_type == 'text/plain':
#                     return handle_text_file_upload(request.user, uploaded_file)
                
#                 elif file_extension in ['doc', 'docx'] or file_content_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
#                     return handle_word_document_upload(request.user, uploaded_file)
                
#                 else:
#                     return JsonResponse({
#                         'status': 'error',
#                         'message': f'Unsupported file type: {file_extension}. Supported formats: PDF, Images (JPG, PNG, GIF, etc.), Text files, Word documents'
#                     }, status=400)
                    
#             except Exception as e:
#                 print(f"File upload error: {e}")
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': f'Error processing file: {str(e)}'
#                 }, status=400)

#         elif action == 'update_config':
#             try:
#                 bot_config, _ = BotConfiguration.objects.get_or_create(company=request.user)
#                 bot_config.bot_name = request.POST.get('bot_name', bot_config.bot_name)
#                 bot_config.welcome_message = request.POST.get('welcome_message', bot_config.welcome_message)
#                 bot_config.system_prompt = request.POST.get('system_prompt', bot_config.system_prompt)
#                 selected_color = request.POST.get('color_scheme')
#                 if selected_color in COLOR_SCHEMES:
#                     bot_config.color_scheme = selected_color
#                 bot_config.is_active = request.POST.get('is_active') == 'on'
#                 bot_config.save()
#                 return JsonResponse({
#                     'status': 'success',
#                     'message': 'Bot configuration updated'
#                 })
#             except Exception as e:
#                 return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
#         elif action == 'delete_knowledge':
#             knowledge_id = request.POST.get('knowledge_id')
#             try:
#                 knowledge = KnowledgeBase.objects.get(
#                     id=int(knowledge_id),
#                     company=request.user
#                 )
#                 knowledge.delete()
#                 return JsonResponse({
#                     'status': 'success',
#                     'message': 'Knowledge deleted'
#                 })
#             except KnowledgeBase.DoesNotExist:
#                 return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)
    
#     knowledge = KnowledgeBase.objects.filter(company=request.user).order_by('-created_at')
#     bot_config, _ = BotConfiguration.objects.get_or_create(company=request.user)
#     conversations = ConversationHistory.objects.filter(company=request.user)[:10]
    
#     context = {
#         'knowledge_count': knowledge.count(),
#         'knowledge': knowledge,
#         'bot_config': bot_config,
#         'recent_conversations': conversations,
#         'color_schemes': COLOR_SCHEMES
#     }
#     return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def dashboard(request):

    COLOR_SCHEMES = ['blue', 'green', 'purple', 'red']

    if request.method == 'POST':
        action = request.POST.get('action')

        # -----------------------------
        # TEXT UPLOAD
        # -----------------------------
        if action == 'upload_text':
            content = request.POST.get('content', '').strip()

            if not content:
                return JsonResponse({'status': 'error', 'message': 'Empty text'}, status=400)

            process_and_save_chunk(request.user, content, 'text', None)

            return JsonResponse({
                'status': 'success',
                'message': 'Text uploaded successfully'
            })

        # -----------------------------
        # FILE UPLOAD
        # -----------------------------
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
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Unsupported file type: {file_extension}'
                    }, status=400)

            except Exception as e:
                print("Upload Error:", e)

                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=400)

        # -----------------------------
        # UPDATE BOT CONFIG
        # -----------------------------
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

                return JsonResponse({
                    'status': 'success',
                    'message': 'Bot configuration updated'
                })

            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

        # -----------------------------
        # DELETE KNOWLEDGE
        # -----------------------------
        elif action == 'delete_knowledge':

            knowledge_id = request.POST.get('knowledge_id')

            try:
                knowledge = KnowledgeBase.objects.get(
                    id=int(knowledge_id),
                    company=request.user
                )

                knowledge.delete()

                return JsonResponse({
                    'status': 'success',
                    'message': 'Knowledge deleted'
                })

            except KnowledgeBase.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)

    # ---------------------------------
    # PAGE LOAD
    # ---------------------------------

    knowledge = KnowledgeBase.objects.filter(company=request.user).order_by('-created_at')
    bot_config, _ = BotConfiguration.objects.get_or_create(company=request.user)
    conversations = ConversationHistory.objects.filter(company=request.user)[:10]

    context = {
        'knowledge_count': knowledge.count(),
        'knowledge': knowledge,
        'bot_config': bot_config,
        'recent_conversations': conversations,
        'color_schemes': COLOR_SCHEMES
    }

    return render(request, 'dashboard.html', context)

def handle_pdf_upload(user, pdf_file):
    """Handle PDF file upload and extract text"""
    try:
        from PyPDF2 import PdfReader
        
        # Validate PDF header
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
        
        # Split into chunks and save
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

# def handle_image_upload(user, image_file):
#     """Handle image file upload - extract text using OCR"""
#     try:
#         from PIL import Image
#         import pytesseract
        
#         # Open image
#         img = Image.open(image_file)
        
#         # Extract text using OCR
#         extracted_text = pytesseract.image_to_string(img)
        
#         if not extracted_text.strip():
#             return JsonResponse({
#                 'status': 'error',
#                 'message': 'No text could be extracted from the image'
#             }, status=400)
        
#         # Split into chunks and save
#         chunks = [extracted_text[i:i+1000] for i in range(0, len(extracted_text), 1000)]
#         for chunk in chunks:
#             if chunk.strip():
#                 process_and_save_chunk(user, chunk, 'image', image_file.name)
        
#         return JsonResponse({
#             'status': 'success',
#             'message': f'Image uploaded successfully! Extracted {len(chunks)} chunks of text.'
#         })
#     except ImportError:
#         return JsonResponse({
#             'status': 'error',
#             'message': 'Image processing libraries (PIL/pytesseract) not available'
#         }, status=500)
#     except Exception as e:
#         raise e

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

    # Convert to grayscale
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

    # Threshold (improves OCR a lot)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # OCR
    text = pytesseract.image_to_string(thresh, config='--psm 6')

    print("OCR OUTPUT:", repr(text))  # DEBUG

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
    
# def handle_image_upload(user, image_file):

#     from PIL import Image
#     import pytesseract

#     img = Image.open(image_file)

#     if img.mode != "RGB":
#         img = img.convert("RGB")

#     text = pytesseract.image_to_string(img)

#     if not text.strip():
#         return JsonResponse({
#             'status':'error',
#             'message':'No text found in image'
#         }, status=400)

#     chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]

#     for chunk in chunks:
#         process_and_save_chunk(user, chunk, 'image', image_file.name)

#     return JsonResponse({
#         'status':'success',
#         'message':f'Extracted {len(chunks)} chunks from image'
#     })
    
def handle_text_file_upload(user, text_file):
    """Handle plain text file upload"""
    try:
        # Read text file
        content = text_file.read().decode('utf-8')
        
        if not content.strip():
            return JsonResponse({
                'status': 'error',
                'message': 'Text file is empty'
            }, status=400)
        
        # Split into chunks and save
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
        
        # Extract text from Word document
        text = docx2txt.process(doc_file)
        
        if not text.strip():
            return JsonResponse({
                'status': 'error',
                'message': 'No text found in Word document'
            }, status=400)
        
        # Split into chunks and save
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
    
# @login_required(login_url='login')
# def dashboard(request):
#     """Company dashboard to manage knowledge base and bot settings"""

#     COLOR_SCHEMES = ['blue', 'green', 'purple', 'red']

#     if request.method == 'POST':
#         action = request.POST.get('action')

#         # Text Upload
#         if action == 'upload_text':
#             content = request.POST.get('content', '').strip()
#             if content:
#                 process_and_save_chunk(request.user, content, 'text', None)
#                 return JsonResponse({'status': 'success', 'message': 'Text uploaded successfully'})

#         # PDF Upload
#         elif action == 'upload_pdf':
#             pdf_file = request.FILES.get('pdf_file')
#             if pdf_file:
#                 try:
#                     reader = PdfReader(pdf_file)
#                     all_text = ""
#                     for page in reader.pages:
#                         page_text = page.extract_text()
#                         if page_text:
#                             all_text += page_text + " "
#                     if not all_text.strip():
#                         return JsonResponse({'status': 'error', 'message': 'No text found in PDF'}, status=400)
#                     chunks = [all_text[i:i+1000] for i in range(0, len(all_text), 1000)]
#                     for chunk in chunks:
#                         if chunk.strip():
#                             process_and_save_chunk(request.user, chunk, 'pdf', pdf_file.name)
#                     return JsonResponse({
#                         'status': 'success',
#                         'message': f'PDF uploaded successfully! Added {len(chunks)} chunks.'
#                     })
#                 except Exception as e:
#                     print("PDF Error:", e)
#                     return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
#         elif action == 'update_config':
#             try:
#                 bot_config, _ = BotConfiguration.objects.get_or_create(company=request.user)
#                 bot_config.bot_name = request.POST.get('bot_name', bot_config.bot_name)
#                 bot_config.welcome_message = request.POST.get('welcome_message', bot_config.welcome_message)
#                 bot_config.system_prompt = request.POST.get('system_prompt', bot_config.system_prompt)
#                 selected_color = request.POST.get('color_scheme')
#                 if selected_color in COLOR_SCHEMES:
#                     bot_config.color_scheme = selected_color
#                 bot_config.is_active = request.POST.get('is_active') == 'on'
#                 bot_config.save()
#                 return JsonResponse({
#                     'status': 'success',
#                     'message': 'Bot configuration updated'
#                 })
#             except Exception as e:
#                 return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
#         elif action == 'delete_knowledge':
#             knowledge_id = request.POST.get('knowledge_id')
#             try:
#                 knowledge = KnowledgeBase.objects.get(
#                     id=int(knowledge_id),
#                     company=request.user
#                 )
#                 knowledge.delete()
#                 return JsonResponse({
#                     'status': 'success',
#                     'message': 'Knowledge deleted'
#                 })
#             except KnowledgeBase.DoesNotExist:
#                 return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)
#     knowledge = KnowledgeBase.objects.filter(company=request.user).order_by('-created_at')
#     bot_config, _ = BotConfiguration.objects.get_or_create(company=request.user)
#     conversations = ConversationHistory.objects.filter(company=request.user)[:10]
#     context = {
#         'knowledge_count': knowledge.count(),
#         'knowledge': knowledge,
#         'bot_config': bot_config,
#         'recent_conversations': conversations,
#         'color_schemes': COLOR_SCHEMES
#     }
#     return render(request, 'dashboard.html', context)


# @login_required(login_url='login')
# def dashboard(request):
#     """Company dashboard to manage knowledge base and bot settings"""
#     if request.method == 'POST':
#         action = request.POST.get('action')
        
#         # Handle Text Upload
#         if action == 'upload_text':
#             content = request.POST.get('content', '').strip()
#             if content:
#                 process_and_save_chunk(request.user, content, 'text', None)
#                 return JsonResponse({'status': 'success', 'message': 'Text uploaded successfully'})

#         # Handle PDF Upload
#         elif action == 'upload_pdf':
#             pdf_file = request.FILES.get('pdf_file')
#             if pdf_file:
#                 try:
#                     # Read PDF and extract text
#                     reader = PdfReader(pdf_file)
#                     all_text = ""
                    
#                     # Extract text from all pages
#                     for page in reader.pages:
#                         page_text = page.extract_text()
#                         if page_text:
#                             all_text += page_text + " "
                    
#                     # Check if we got any text
#                     if not all_text.strip():
#                         return JsonResponse({'status': 'error', 'message': 'No text found in PDF'}, status=400)
                    
#                     # Split into chunks of 1000 chars
#                     chunks = [all_text[i:i+1000] for i in range(0, len(all_text), 1000)]
                    
#                     # Save each chunk
#                     for chunk in chunks:
#                         if chunk.strip():
#                             process_and_save_chunk(request.user, chunk, 'pdf', pdf_file.name)
                    
#                     return JsonResponse({'status': 'success', 'message': f'PDF uploaded successfully! Added {len(chunks)} chunks.'})
#                 except Exception as e:
#                     print(f"PDF Error: {str(e)}")  # Debug print
#                     return JsonResponse({'status': 'error', 'message': f'Error reading PDF: {str(e)}'}, status=400)

#         # Handle Bot Configuration Update
#         elif action == 'update_config':
#             try:
#                 bot_config, _ = BotConfiguration.objects.get_or_create(company=request.user)
#                 bot_config.bot_name = request.POST.get('bot_name', bot_config.bot_name)
#                 bot_config.welcome_message = request.POST.get('welcome_message', bot_config.welcome_message)
#                 bot_config.system_prompt = request.POST.get('system_prompt', bot_config.system_prompt)
#                 bot_config.color_scheme = request.POST.get('color_scheme', bot_config.color_scheme)
#                 bot_config.is_active = request.POST.get('is_active') == 'on'
#                 bot_config.save()
#                 return JsonResponse({'status': 'success', 'message': 'Bot configuration updated'})
#             except Exception as e:
#                 return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

#         # Handle Delete Knowledge
#         elif action == 'delete_knowledge':
#             knowledge_id = request.POST.get('knowledge_id')
#             try:
#                 knowledge = KnowledgeBase.objects.get(id=knowledge_id, company=request.user)
#                 knowledge.delete()
#                 return JsonResponse({'status': 'success', 'message': 'Knowledge deleted'})
#             except KnowledgeBase.DoesNotExist:
#                 return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)
    
#     # Get company's knowledge base and bot config
#     knowledge = KnowledgeBase.objects.filter(company=request.user).order_by('-created_at')
#     bot_config, _ = BotConfiguration.objects.get_or_create(company=request.user)
#     conversations = ConversationHistory.objects.filter(company=request.user)[:10]
    
#     context = {
#         'knowledge_count': knowledge.count(),
#         'knowledge': knowledge,
#         'bot_config': bot_config,
#         'recent_conversations': conversations,
#         'color_schemes': ['blue', 'green', 'purple', 'red']
#     }
#     return render(request, 'dashboard.html', context)


# ============ HELPER FUNCTIONS ============

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


# ============ CUSTOMER CHAT VIEWS (Public) ============

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
        # Find the company
        company = get_object_or_404(User, username=company_name)
        
        # Check if bot is active
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

        # Get audio file
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return JsonResponse({'error': 'No audio file received'}, status=400)

        # 1. Transcribe audio to text
        user_text = transcribe_audio(audio_file)
        
        # 2. Get embedding for the query
        try:
            query_vector = get_embedding(user_text)
        except Exception as e:
            print(f"Embedding error: {e}")
            return JsonResponse({
                'transcript': user_text,
                'answer': "I'm sorry, I'm having trouble processing your request. Please try again."
            })
        
        # 3. Search company's knowledge base
        context_chunks = KnowledgeBase.objects.filter(company=company).order_by(
            CosineDistance('embedding', query_vector)
        )[:3]
        
        context_text = " ".join([c.content for c in context_chunks])
        
        # 4. Generate response using LLM
        ai_answer = get_llm_answer(user_text, context_text, bot_config)
        
        # 5. Log conversation
        ConversationHistory.objects.create(
            company=company,
            customer_message=user_text,
            bot_response=ai_answer,
            customer_name='Customer'
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

        # Get embedding
        try:
            query_vector = get_embedding(user_text)
        except Exception as e:
            print(f"Embedding error: {e}")
            return JsonResponse({
                'answer': "I'm having trouble processing your question. Please try again."
            })
        
        # Search knowledge base
        context_chunks = KnowledgeBase.objects.filter(company=company).order_by(
            CosineDistance('embedding', query_vector)
        )[:3]
        context_text = " ".join([c.content for c in context_chunks])
        ai_answer = get_llm_answer(user_text, context_text, bot_config)
        ConversationHistory.objects.create(
            company=company,
            customer_message=user_text,
            bot_response=ai_answer,
            customer_name='Customer'
        )
        return JsonResponse({'answer': ai_answer})
    except Exception as e:
        print(f"Text chat error: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


# ============ COMPANY CHAT VIEW ============

@login_required(login_url='login')
def chat_page(request):
    """Internal chat page for company to test their bot"""
    bot_config, _ = BotConfiguration.objects.get_or_create(company=request.user)
    return render(request, 'chat.html', {'bot_config': bot_config})


@csrf_exempt
@login_required(login_url='login')
@require_http_methods(["POST"])
def voice_chat_view(request):
    """Internal voice API for company to test bot"""
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

        # Get embedding
        try:
            query_vector = get_embedding(user_text)
        except Exception as e:
            print(f"Embedding error: {e}")
            return JsonResponse({
                'answer': "I'm having trouble processing that. Please try again."
            })
        
        # Search knowledge base
        context_chunks = KnowledgeBase.objects.filter(company=request.user).order_by(
            CosineDistance('embedding', query_vector)
        )[:3]
        
        context_text = " ".join([c.content for c in context_chunks])
        
        # Get bot config
        bot_config, _ = BotConfiguration.objects.get_or_create(company=request.user)
        ai_answer = get_llm_answer(user_text, context_text, bot_config)
        
        return JsonResponse({'answer': ai_answer})
        
    except Exception as e:
        print(f"Text chat error: {e}")
        return JsonResponse({'error': str(e)}, status=500)