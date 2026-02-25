from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as av

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('accounts/', include('accounts.urls')),

    # Dashboard
    path('dashboard/', av.dashboard_view, name='dashboard'),

    # Profile
    path('profile/edit/', av.edit_profile, name='edit_profile'),

    # Students
    path('students/', av.find_students, name='find_students'),
    path('students/<str:username>/', av.student_profile, name='student_profile'),
    path('students/<str:username>/connect/', av.send_connection_request, name='send_connection_request'),

    # Connections
    path('connections/', av.connections_view, name='connections'),
    path('connections/<int:pk>/<str:action>/', av.handle_connection_request, name='handle_connection_request'),

    # Messages inbox
    path('messages/', av.messages_inbox, name='messages_inbox'),

    # Chat (send/ MUST be before <username>/)
    path('chat/send/', av.send_message_ajax, name='send_message'),
    path('chat/messages/<str:username>/', av.get_messages_ajax, name='get_messages'),
    path('chat/<str:username>/', av.chat_view, name='chat'),

    # Universities
    path('universities/', av.universities_page, name='universities'),
    path('universities/submit/', av.submit_university, name='submit_university'),

    # Scholarships
    path('scholarships/', av.scholarships_page, name='scholarships'),
    path('scholarships/submit/', av.submit_scholarship, name='submit_scholarship'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
