from django.urls import path, include
from . import views

urlpatterns = [
    # Public Pages
    path('', views.landing_page, name='landing'),
    
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Company Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('bot/', views.chat_page, name='chat_page'),
    path('voice-chat/', views.voice_chat_view, name='voice_chat'),
    path('text-chat/', views.text_chat_view, name='text_chat'),
    
    # Public Customer Chat
    path('chat/<str:company_name>/', views.public_chat_page, name='public_chat'),
    path('chat/<str:company_name>/voice/', views.public_voice_chat, name='public_voice_api'),
    path('chat/<str:company_name>/text/', views.public_text_chat, name='public_text_api'),
    
    # Voice URLs
    path('voice/', views.voice_chat_view, name='voice_chat'),
    path('voice/process/', views.process_voice_input, name='process_voice'),
    path('voice/public/', views.public_voice_chat, name='public_voice_chat'),
    
    # Voice call URLs
    path('voice-call/', views.voice_call_interface, name='voice_call'),
    path('voice-call/<str:company_name>/', views.customer_voice_call, name='customer_voice_call'),
    path('voice/process-stream/', views.process_voice_stream, name='process_voice_stream'),
    path('voice/customer-stream/<str:company_name>/', views.process_customer_voice_stream, name='customer_voice_stream'),
    path('dashboard/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
]