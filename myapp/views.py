from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from functools import wraps
import json
from django.views.decorators.http import require_POST
from .models import User, Chat, Message


def custom_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('is_logged_in'):
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper


def index(request):
    return render(request, 'index.html')


def home(request):
    user = None
    email = request.session.get('email')

    if email:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            request.session.flush()

    return render(request, 'home.html', {'user': user})


def signup(request):
    if request.method == "POST":
        email = request.POST.get('email')

        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {"msg": "Email already exists"})

        if request.POST.get('password') != request.POST.get('cpassword'):
            return render(request, 'signup.html', {'msg': "Password and Confirm Password do not match"})

        profile_image = request.FILES.get('profile_image')

        User.objects.create(
            name=request.POST.get('name'),
            email=email,
            mobile=request.POST.get('mobile'),
            password=request.POST.get('password'),
            profile_image=profile_image
        )

        return render(request, 'login.html', {'msg': "Sign Up Done"})

    return render(request, 'signup.html')


def signup_desh(request):
    return render(request, 'signup_desh.html')


@csrf_exempt
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)

            if user.password == password:
                request.session['email'] = user.email
                request.session['profile'] = user.profile_image.url if user.profile_image else ''
                request.session['is_logged_in'] = True
                request.session['user_id'] = user.id
                return redirect('home')

            return render(request, 'login.html', {'msg': "Password doesn't match"})

        except User.DoesNotExist:
            return render(request, 'login.html', {'msg': "Email doesn't exist"})

    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


@custom_login_required
def main(request):
    return render(request, 'main.html')


@custom_login_required
def chat(request):
    email = request.session.get('email')

    try:
        user = User.objects.get(email=email)
        users = User.objects.exclude(id=user.id)
    except User.DoesNotExist:
        request.session.flush()
        return redirect('login')

    return render(request, 'chat.html', {
        'user': user,
        'users': users
    })


@custom_login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    current_user_id = request.session.get('user_id')
    if not current_user_id:
        return redirect('login')

    current_user = get_object_or_404(User, id=current_user_id)

    chat = Chat.objects.filter(
        (Q(user1=current_user) & Q(user2=other_user)) |
        (Q(user1=other_user) & Q(user2=current_user))
    ).first()

    messages = []
    if chat:
        messages = Message.objects.filter(chat=chat).order_by('created_at')

    context = {
        'other_user': other_user,
        'chat': chat,
        'messages': messages,
        'current_user': current_user
    }

    return render(request, 'chat/start_chat.html', context)


@require_POST
@csrf_exempt
def send_message(request):
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"status": "error", "message": "Invalid JSON"})

    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({"status": "error", "message": "Login required"})

    try:
        sender = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Sender not found"})

    receiver_id = data.get("receiver_id")
    message_text = data.get("content", "").strip()

    if not receiver_id or not message_text:
        return JsonResponse({"status": "error", "message": "Invalid data"})

    try:
        receiver = User.objects.get(id=receiver_id)
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Receiver not found"})

    Message.objects.create(
        sender=sender,
        receiver=receiver,
        text=message_text
    )

    return JsonResponse({"status": "success"})


def show_logs(request):
    logs_data = []

    try:
        with open('logs.txt', 'r') as f:
            lines = f.readlines()[-100:]
    except FileNotFoundError:
        lines = []

    for line in lines:
        parts = line.strip().split(' | ')
        if len(parts) == 3:
            logs_data.append({
                'time': parts[0],
                'level': parts[1],
                'message': parts[2],
            })

    return render(request, 'logs.html', {'logs': logs_data})




@custom_login_required
def get_messages(request, user_id):
    current_user_id = request.session.get('user_id')

    # ❌ No user → return empty
    if not current_user_id:
        return JsonResponse({"messages": []})

    # ✅ 1. Mark messages as read (IMPORTANT 🔥)
    Message.objects.filter(
        sender_id=user_id,
        receiver_id=current_user_id,
        is_read=False
    ).update(is_read=True)

    # ✅ 2. Fetch chat messages
    messages = Message.objects.filter(
        Q(sender_id=current_user_id, receiver_id=user_id) |
        Q(sender_id=user_id, receiver_id=current_user_id)
    ).order_by('timestamp')

    # ✅ 3. Format response
    data = [
        {
            "sender": msg.sender_id,
            "message": msg.text,
            "time": msg.timestamp.strftime("%H:%M")
        }
        for msg in messages
    ]

    return JsonResponse({"messages": data})



def get_users_with_unread(request):
    users = User.objects.exclude(id=request.user.id)

    user_list = []

    for u in users:
        unread_count = Message.objects.filter(
            sender=u,
            receiver=request.user,
            is_read=False
        ).count()

        user_list.append({
            "id": u.id,
            "username": u.username,
            "unread": unread_count
        })

    return JsonResponse({"users": user_list})
