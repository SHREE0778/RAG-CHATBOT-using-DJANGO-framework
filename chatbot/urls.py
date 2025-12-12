from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='chatbot/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Chat
    path('', views.chat_view, name='chat'),  # ← Changed from views.index to views.chat_view
    path('send-message/', views.send_message, name='send_message'),
    path('clear-history/', views.clear_chat_history, name='clear_history'),
    
    # Documents
    path('upload/', views.upload_document, name='upload'),
    path('delete-document/<int:doc_id>/', views.delete_document, name='delete_document'),
]