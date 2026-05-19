from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import  redirect, render

from .forms import (
    LoginForm,
    RegistrationForm,
)
from .models import BookingRequest, Review, Venue


def check_admin_access(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.is_staff:
        messages.error(request, 'Доступ разрешён только администратору.')
        return redirect('login')

    return None


def home(request):
    context = {
        'venues': Venue.objects.all()[:4],
        'reviews': Review.objects.select_related('user', 'booking_request')[:4],
        'stats': {
            'venues': Venue.objects.count(),
            'requests': BookingRequest.objects.count(),
            'completed': BookingRequest.objects.filter(status=BookingRequest.Status.COMPLETED).count(),
        },
    }
    return render(request, 'conference/home.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно. Добро пожаловать!')
            return redirect('dashboard')
    else:
        form = RegistrationForm()

    return render(request, 'conference/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_requests')
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_staff:
                return redirect('admin_requests')
            return redirect('dashboard')
        messages.error(request, 'Неверный логин или пароль.')
    else:
        form = LoginForm(request)

    return render(request, 'conference/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')


