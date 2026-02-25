import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .forms import SignUpForm, LoginForm, EditProfileForm, UniversitySubmissionForm, ScholarshipSubmissionForm
from .models import User, ConnectionRequest, Message, UniversitySubmission, ScholarshipSubmission


# ── Auth ──────────────────────────────────────────────────────────────

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to StudyBridge, {user.get_display_name()}!')
            return redirect('dashboard')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_display_name()}!')
            return redirect(request.GET.get('next', 'dashboard'))
        messages.error(request, 'Invalid email or password. Please try again.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('landing')


# ── Dashboard ─────────────────────────────────────────────────────────

@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html', {
        'active_page': 'dashboard',
        'page_title': 'Dashboard',
    })


# ── Find Students ─────────────────────────────────────────────────────

@login_required
def find_students(request):
    query = request.GET.get('q', '').strip()

    students = User.objects.exclude(id=request.user.id)
    if query:
        students = students.filter(
            Q(username__icontains=query) |
            Q(full_name__icontains=query) |
            Q(university__icontains=query) |
            Q(field_of_study__icontains=query) |
            Q(current_country__icontains=query)
        )
    students = students.order_by('-date_joined')[:60]

    # Build connection status map
    sent = {r.to_user_id: r for r in ConnectionRequest.objects.filter(from_user=request.user)}
    received = {r.from_user_id: r for r in ConnectionRequest.objects.filter(to_user=request.user)}

    def conn_info(uid):
        if uid in sent:
            r = sent[uid]
            return {'status': r.status, 'direction': 'sent', 'pk': r.pk}
        if uid in received:
            r = received[uid]
            return {'status': r.status, 'direction': 'received', 'pk': r.pk}
        return None

    # AJAX request → return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = []
        for s in students:
            ci = conn_info(s.id)
            data.append({
                'id': s.id,
                'username': s.username,
                'display_name': s.get_display_name(),
                'initials': s.get_initials(),
                'university': s.university,
                'field_of_study': s.field_of_study,
                'country_of_origin': s.country_of_origin,
                'current_country': s.current_country,
                'study_level': s.get_study_level_display() if s.study_level else '',
                'year_of_study': s.get_year_of_study_display() if s.year_of_study else '',
                'bio': s.bio[:100] if s.bio else '',
                'connection': ci,
            })
        return JsonResponse({'students': data, 'count': len(data)})

    students_with_conn = [(s, conn_info(s.id)) for s in students]

    return render(request, 'students/find_students.html', {
        'students_with_conn': students_with_conn,
        'query': query,
        'active_page': 'find_students',
        'page_title': 'Find Students',
    })


# ── Student Profile ───────────────────────────────────────────────────

@login_required
def student_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    if profile_user == request.user:
        return redirect('dashboard')

    connection = ConnectionRequest.objects.filter(
        Q(from_user=request.user, to_user=profile_user) |
        Q(from_user=profile_user, to_user=request.user)
    ).first()

    return render(request, 'students/profile.html', {
        'profile_user': profile_user,
        'connection': connection,
        'is_sender': connection.from_user == request.user if connection else False,
        'active_page': 'find_students',
        'page_title': profile_user.get_display_name(),
    })


# ── Connection Requests ───────────────────────────────────────────────

@login_required
def send_connection_request(request, username):
    if request.method != 'POST':
        return redirect('find_students')

    to_user = get_object_or_404(User, username=username)
    if to_user == request.user:
        messages.error(request, "You can't connect with yourself.")
        return redirect('find_students')

    existing = ConnectionRequest.objects.filter(
        Q(from_user=request.user, to_user=to_user) |
        Q(from_user=to_user, to_user=request.user)
    ).first()

    if existing:
        if existing.status == 'rejected' and existing.from_user == request.user:
            existing.status = 'pending'
            existing.save()
            messages.success(request, f'Request re-sent to {to_user.get_display_name()}!')
        elif existing.status == 'accepted':
            messages.info(request, 'You are already connected.')
        else:
            messages.info(request, 'Request already pending.')
    else:
        ConnectionRequest.objects.create(from_user=request.user, to_user=to_user)
        messages.success(request, f'Request sent to {to_user.get_display_name()}!')

    return redirect(request.POST.get('next', '') or 'student_profile', username=username)


@login_required
def handle_connection_request(request, pk, action):
    conn = get_object_or_404(ConnectionRequest, pk=pk, to_user=request.user)
    if action == 'accept':
        conn.status = 'accepted'
        conn.save()
        messages.success(request, f'You are now connected with {conn.from_user.get_display_name()}!')
    elif action == 'reject':
        conn.status = 'rejected'
        conn.save()
        messages.info(request, 'Connection request declined.')
    return redirect(request.POST.get('next', 'connections'))


# ── Connections List ──────────────────────────────────────────────────

@login_required
def connections_view(request):
    accepted_qs = ConnectionRequest.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user),
        status='accepted'
    ).select_related('from_user', 'to_user')

    connections = []
    for conn in accepted_qs:
        other = conn.to_user if conn.from_user == request.user else conn.from_user
        last_msg = Message.objects.filter(
            Q(sender=request.user, receiver=other) |
            Q(sender=other, receiver=request.user)
        ).order_by('-timestamp').first()
        unread = Message.objects.filter(sender=other, receiver=request.user, is_read=False).count()
        connections.append({'user': other, 'connection': conn, 'last_message': last_msg, 'unread': unread})

    pending_received = ConnectionRequest.objects.filter(
        to_user=request.user, status='pending'
    ).select_related('from_user')

    pending_sent = ConnectionRequest.objects.filter(
        from_user=request.user, status='pending'
    ).select_related('to_user')

    return render(request, 'students/connections.html', {
        'connections': connections,
        'pending_received': pending_received,
        'pending_sent': pending_sent,
        'active_page': 'connections',
        'page_title': 'My Network',
    })


# ── Messages Inbox ────────────────────────────────────────────────────

@login_required
def messages_inbox(request):
    accepted_qs = ConnectionRequest.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user),
        status='accepted'
    ).select_related('from_user', 'to_user')

    chat_list = []
    for conn in accepted_qs:
        other = conn.to_user if conn.from_user == request.user else conn.from_user
        last_msg = Message.objects.filter(
            Q(sender=request.user, receiver=other) |
            Q(sender=other, receiver=request.user)
        ).order_by('-timestamp').first()
        unread = Message.objects.filter(sender=other, receiver=request.user, is_read=False).count()
        chat_list.append({'user': other, 'last_message': last_msg, 'unread': unread})

    chat_list.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else x['user'].date_joined,
        reverse=True
    )

    return render(request, 'students/messages_inbox.html', {
        'chat_list': chat_list,
        'active_page': 'messages',
        'page_title': 'Messages',
    })


# ── Chat ──────────────────────────────────────────────────────────────

@login_required
def chat_view(request, username):
    other_user = get_object_or_404(User, username=username)

    connection = ConnectionRequest.objects.filter(
        Q(from_user=request.user, to_user=other_user) |
        Q(from_user=other_user, to_user=request.user),
        status='accepted'
    ).first()

    if not connection:
        messages.error(request, 'You must be connected to chat.')
        return redirect('student_profile', username=username)

    msgs = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    Message.objects.filter(
        sender=other_user, receiver=request.user, is_read=False
    ).update(is_read=True)

    # Build conversations list for sidebar panel
    accepted_qs = ConnectionRequest.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user),
        status='accepted'
    ).select_related('from_user', 'to_user')

    chat_list = []
    for conn in accepted_qs:
        other = conn.to_user if conn.from_user == request.user else conn.from_user
        last_msg = Message.objects.filter(
            Q(sender=request.user, receiver=other) |
            Q(sender=other, receiver=request.user)
        ).order_by('-timestamp').first()
        unread = Message.objects.filter(sender=other, receiver=request.user, is_read=False).count()
        chat_list.append({'user': other, 'last_message': last_msg, 'unread': unread})

    chat_list.sort(key=lambda x: x['last_message'].timestamp if x['last_message'] else x['user'].date_joined, reverse=True)

    last_id = msgs.last().id if msgs.exists() else 0

    return render(request, 'students/chat.html', {
        'other_user': other_user,
        'chat_messages': msgs,
        'chat_list': chat_list,
        'last_id': last_id,
        'active_page': 'messages',
        'page_title': 'Messages',
    })


@login_required
def send_message_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        receiver_username = data.get('receiver', '').strip()
        content = data.get('content', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not content:
        return JsonResponse({'error': 'Empty message'}, status=400)
    if not receiver_username:
        return JsonResponse({'error': 'No receiver'}, status=400)

    receiver = get_object_or_404(User, username=receiver_username)

    connected = ConnectionRequest.objects.filter(
        Q(from_user=request.user, to_user=receiver) |
        Q(from_user=receiver, to_user=request.user),
        status='accepted'
    ).exists()

    if not connected:
        return JsonResponse({'error': 'Not connected'}, status=403)

    msg = Message.objects.create(sender=request.user, receiver=receiver, content=content)

    return JsonResponse({
        'id': msg.id,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%H:%M'),
        'sender': request.user.username,
        'is_mine': True,
    })


@login_required
def get_messages_ajax(request, username):
    other_user = get_object_or_404(User, username=username)
    after_id = int(request.GET.get('after', 0))

    msgs = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user),
        id__gt=after_id
    ).order_by('timestamp')

    msgs.filter(sender=other_user, receiver=request.user).update(is_read=True)

    return JsonResponse({
        'messages': [{
            'id': m.id,
            'content': m.content,
            'timestamp': m.timestamp.strftime('%H:%M'),
            'sender': m.sender.username,
            'is_mine': m.sender == request.user,
        } for m in msgs]
    })


# ── Edit Profile ──────────────────────────────────────────────────────

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('edit_profile')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {
        'form': form,
        'active_page': 'profile',
        'page_title': 'Edit Profile',
    })


# ── University Submission ─────────────────────────────────────────────

@login_required
def submit_university(request):
    user_submissions = UniversitySubmission.objects.filter(submitted_by=request.user)

    if request.method == 'POST':
        form = UniversitySubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.submitted_by = request.user
            sub.save()
            messages.success(request, 'University submitted for review! Our admin team will review it shortly.')
            return redirect('submit_university')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = UniversitySubmissionForm()

    return render(request, 'students/submit_university.html', {
        'form': form,
        'user_submissions': user_submissions,
        'active_page': 'universities',
        'page_title': 'Submit University',
    })


# ── Universities Page ─────────────────────────────────────────────────

def universities_page(request):
    approved = UniversitySubmission.objects.filter(
        status='approved'
    ).select_related('submitted_by').order_by('university_name')

    query = request.GET.get('q', '').strip()
    country_filter = request.GET.get('country', '').strip()

    if query:
        approved = approved.filter(
            Q(university_name__icontains=query) |
            Q(country__icontains=query) |
            Q(city__icontains=query) |
            Q(description__icontains=query)
        )
    if country_filter:
        approved = approved.filter(country__icontains=country_filter)

    countries = UniversitySubmission.objects.filter(
        status='approved'
    ).values_list('country', flat=True).distinct().order_by('country')

    context = {
        'universities': approved,
        'query': query,
        'country_filter': country_filter,
        'countries': countries,
        'active_page': 'universities',
        'page_title': 'Universities',
    }

    # Support both dashboard and landing page view
    if request.user.is_authenticated:
        return render(request, 'students/universities.html', context)
    return render(request, 'students/universities_public.html', context)


# ── Scholarship Submission ─────────────────────────────────────────────

@login_required
def submit_scholarship(request):
    user_submissions = ScholarshipSubmission.objects.filter(submitted_by=request.user)
    has_university = bool(request.user.university.strip())

    if request.method == 'POST':
        form = ScholarshipSubmissionForm(request.POST)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.submitted_by = request.user
            sub.university_name = request.user.university
            sub.save()
            messages.success(request, 'Scholarship submitted for review! Our admin team will review it shortly.')
            return redirect('submit_scholarship')
        messages.error(request, 'Please fix the errors below.')
    else:
        initial = {'university_name': request.user.university}
        form = ScholarshipSubmissionForm(initial=initial)

    return render(request, 'students/submit_scholarship.html', {
        'form': form,
        'user_submissions': user_submissions,
        'has_university': has_university,
        'active_page': 'scholarships',
        'page_title': 'Submit a Scholarship',
    })


# ── Scholarships Page ──────────────────────────────────────────────────

def scholarships_page(request):
    approved = ScholarshipSubmission.objects.filter(
        status='approved'
    ).select_related('submitted_by').order_by('-submitted_at')

    query = request.GET.get('q', '').strip()
    type_filter = request.GET.get('type', '').strip()

    if query:
        approved = approved.filter(
            Q(university_name__icontains=query) |
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    if type_filter:
        approved = approved.filter(scholarship_type=type_filter)

    type_choices = ScholarshipSubmission.SCHOLARSHIP_TYPE_CHOICES

    context = {
        'scholarships': approved,
        'query': query,
        'type_filter': type_filter,
        'type_choices': type_choices,
        'active_page': 'scholarships',
        'page_title': 'Scholarships',
    }

    if request.user.is_authenticated:
        return render(request, 'students/scholarships.html', context)
    return render(request, 'students/scholarships_public.html', context)
