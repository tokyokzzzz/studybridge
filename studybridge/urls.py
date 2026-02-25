from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from accounts import views as av

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('accounts/', include('accounts.urls')),

    # Dashboard
    path('dashboard/', av.dashboard_view, name='dashboard'),

    # Students
    path('students/', av.find_students, name='find_students'),
    path('students/<str:username>/', av.student_profile, name='student_profile'),
    path('students/<str:username>/connect/', av.send_connection_request, name='send_connection_request'),

    # Connections  (must come before chat/<username>/)
    path('connections/', av.connections_view, name='connections'),
    path('connections/<int:pk>/<str:action>/', av.handle_connection_request, name='handle_connection_request'),

    # Chat  (send/ MUST be before <username>/ to avoid matching "send" as a username)
    path('chat/send/', av.send_message_ajax, name='send_message'),
    path('chat/messages/<str:username>/', av.get_messages_ajax, name='get_messages'),
    path('chat/<str:username>/', av.chat_view, name='chat'),
]
