from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser
import re

User = get_user_model()

def user_registration(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        profile_picture = request.FILES.get('profile_picture')

        # Form Validations
        if not username or not email or not password:
            messages.error(request, 'Username, Email, and Password are required.')
            return render(request, "user_authentication/register.html")

        if phone_number and not re.match(r'^[6-9]\d{9}$', phone_number):
            messages.error(request, 'Please enter a valid 10-digit phone number starting with 6-9.')
            return render(request, "user_authentication/register.html")

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, "user_authentication/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, 'This username is already taken.')
            return render(request, "user_authentication/register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email address is already registered.')
            return render(request, "user_authentication/register.html")

        # Create user first to assign primary key (user.id)
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            phone_number=phone_number,
        )
        if profile_picture:
            user.profile_picture = profile_picture
            user.save()

        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('login')

    return render(request, "user_authentication/register.html")


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            return redirect('login')

    return render(request, 'user_authentication/login.html')


@login_required(login_url='login')
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required(login_url='login')
def user_profile_view(request):
    return render(request, "user_authentication/user_profile_view.html", {"user_view": request.user})


@login_required(login_url='login')
def user_profile_edit(request):
    user = request.user
    if request.method == 'POST':
        username = request.POST.get("username", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        profile_picture = request.FILES.get("profile_picture")

        if phone_number and not re.match(r'^[6-9]\d{9}$', phone_number):
            messages.error(request, 'Please enter a valid 10-digit phone number.')
            return render(request, "user_authentication/user_edit_profile.html", {"user_edit": user})

        # Check for username / email collisions with other users
        if User.objects.filter(username=username).exclude(pk=user.pk).exists():
            messages.error(request, 'This username is already taken by another account.')
            return render(request, "user_authentication/user_edit_profile.html", {"user_edit": user})

        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            messages.error(request, 'This email address is already in use by another account.')
            return render(request, "user_authentication/user_edit_profile.html", {"user_edit": user})

        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone_number = phone_number

        if profile_picture:
            user.profile_picture = profile_picture

        user.save()
        messages.success(request, 'Your profile has been successfully updated.')
        return redirect("user_view")

    return render(request, "user_authentication/user_edit_profile.html", {"user_edit": user})


def forgot_password_username(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        try:
            user = CustomUser.objects.get(username=username)
            request.session['reset_username'] = username
            return redirect("reset_password")
        except CustomUser.DoesNotExist:
            messages.error(request, "Username not found.")
    return render(request, "user_authentication/forgot_password.html")


def reset_password(request):
    username = request.session.get("reset_username")
    if not username:
        messages.error(request, "Please enter your username first.")
        return redirect("forgot_password")

    if request.method == "POST":
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password")

        try:
            user = CustomUser.objects.get(username=username)
            user.set_password(password)
            user.save()
            del request.session['reset_username']
            messages.success(request, "Password reset successful. Please log in with your new password.")
            return redirect("login")
        except CustomUser.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect("forgot_password")

    return render(request, "user_authentication/reset_password.html")