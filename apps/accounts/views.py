from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.decorators import login_required

from .forms import RegisterForm, LoginForm, OTPVerificationForm, ProfileUpdateForm
from .models import EmailOTP
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)

def send_otp_email(user):
    otp_code = EmailOTP.generate_otp()

    EmailOTP.objects.update_or_create(
        user=user,
        defaults={
            'otp': otp_code,
            'created_at': timezone.now(),
        }
    )

    send_mail(
        subject='Room Finder Email Verification OTP',
        message=f'Your Room Finder verification OTP is: {otp_code}. It expires in 10 minutes.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.email_verified = False
            user.is_active = True
            user.save()

            try:
                send_otp_email(user)
            except Exception:
                user.delete()
                messages.error(
                    request,
                    "Could not send OTP email. Please try again later."
                )
                return redirect('register')

            request.session['verify_user_id'] = user.id

            messages.success(
                request,
                "Account created. Please verify your email using the OTP."
            )
            return redirect('verify_otp')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {
        'form': form
    })


def verify_otp_view(request):
    user_id = request.session.get('verify_user_id')

    if not user_id:
        messages.error(request, "Verification session expired. Please register again.")
        return redirect('register')

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)

        if form.is_valid():
            entered_otp = form.cleaned_data['otp']

            try:
                otp_obj = EmailOTP.objects.get(user_id=user_id)
            except EmailOTP.DoesNotExist:
                messages.error(request, "OTP not found. Please request a new one.")
                return redirect('verify_otp')

            if otp_obj.is_expired():
                messages.error(request, "OTP has expired. Please request a new one.")
                return redirect('verify_otp')

            if otp_obj.otp != entered_otp:
                messages.error(request, "Invalid OTP.")
                return redirect('verify_otp')

            user = otp_obj.user
            user.email_verified = True
            user.save(update_fields=['email_verified'])

            otp_obj.delete()

            request.session.pop('verify_user_id', None)

            messages.success(request, "Email verified successfully. You can now login.")
            return redirect('login')
    else:
        form = OTPVerificationForm()

    return render(request, 'accounts/verify_otp.html', {
        'form': form
    })


def resend_otp_view(request):
    user_id = request.session.get('verify_user_id')

    if not user_id:
        messages.error(request, "Verification session expired.")
        return redirect('register')

    from .models import User
    user = User.objects.get(id=user_id)

    try:
        send_otp_email(user)
    except Exception:
        logger.exception("OTP resend failed")
        messages.error(request, "Could not send OTP email. Please try again later.")
        return redirect('verify_otp')

    messages.success(request, "A new OTP has been sent.")
    return redirect('verify_otp')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            user = form.cleaned_data['user']

            if not user.email_verified:
                request.session['verify_user_id'] = user.id
                try:
                    send_otp_email(user)
                except Exception:
                    logger.exception("OTP email failed during login verification")
                    messages.error(request, "Could not send OTP email. Please try again later.")
                    return redirect('login')

                messages.warning(request, "Please verify your email first. A new OTP was sent.")
                return redirect('verify_otp')

            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect('home')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {
        'form': form
    })


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {
        'form': form
    })


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {
        'form': form
    })