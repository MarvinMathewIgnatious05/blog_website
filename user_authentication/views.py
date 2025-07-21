from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from .models import CustomUser
import re
# Create your views here.
def user_registration(request):
    User = get_user_model()


    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name= request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        profile_picture = request.FILES.get('profile_picture')

        if not re.match(r'^[6-9]\d{9}$', phone_number):
            messages.info(request, 'Enter valid 10-digit phone number')
            return redirect('register')

        if password==confirm_password:
            if User.objects.filter(username=username).exists():
                messages.info(request,'this username already exist')
                return redirect('register')

            elif User.objects.filter(email=email).exists():
                messages.info(request,'this email already exist')
                return redirect('register')

            elif User.objects.filter(first_name=first_name).exists():
                messages.info(request,'this first_name already exist')
                return redirect('register')

            else:
                user = User.objects.create_user(username=username,first_name=first_name,last_name=last_name,email=email,password=password
                                                ,phone_number=phone_number,profile_picture=profile_picture)
                user.save()
                return redirect('login')

        else:
            messages.info(request,'this password is not match')
            return redirect('register')

    return render(request, "register.html")


def user_login(request):

    if request.method=='POST':

        username=request.POST.get('username')
        password=request.POST.get('password')
        user=auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            return redirect('home')

        else:
            messages.info(request,'please provide correct info')
            return redirect('login')

    return render(request,'login.html')

@login_required(login_url='login')
def user_logout(request):
    # auth.logout(request.user)
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def user_profile_view(request):
    user = request.user
    print("user:", user)
    return render(request, "user_profile_view.html", {"user_view": request.user})
@login_required(login_url='login')
def user_profile_edit(request):
    user = request.user
    if request.method == 'POST':
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get('last_name')
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        profile_picture = request.FILES.get("profile_picture")

        user.username = username
        user.first_name = first_name
        user.last_name= last_name
        user.email = email
        user.phone_number = phone_number


        if profile_picture:
            user.profile_picture = profile_picture

        else:
            pass

        user.save()
        return redirect("user_view")

    return render(request, "user_edit_profile.html", {"user_edit": user})


def forgot_password_username(request):
    if request.method == "POST":
        username = request.POST.get("username")
        try:
            user = CustomUser.objects.get(username=username)
            print("////",user)
            request.session['reset_username'] = username
            return redirect("reset_password")
        except CustomUser.DoesNotExist:
            messages.error(request, "Username not found.")
    return render(request, "forgot_password.html")



def reset_password(request):
    username = request.session.get("reset_username")
    if not username:
        return redirect("forgot_password")

    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password")

        user = CustomUser.objects.get(username=username)
        user.set_password(password)
        user.save()
        messages.success(request, "Password reset successful. Please login.")
        return redirect("login")

    return render(request, "reset_password.html")