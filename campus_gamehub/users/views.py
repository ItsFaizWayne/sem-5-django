from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.core.mail import send_mail
from django.conf import settings
import random
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from rentals.models import Rental
from games.models import Game

User = get_user_model()

# ------------------ Register ------------------
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

# ------------------ Forgot Password (Send OTP) ------------------
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = str(random.randint(100000, 999999))

            # Store OTP and email in session
            request.session['otp'] = otp
            request.session['reset_email'] = email

            send_mail(
                subject="Password Reset OTP",
                message=f"Your OTP is: {otp}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
            )

            messages.success(request, "OTP has been sent to your email.")
            return redirect('verify_otp')
        except User.DoesNotExist:
            messages.error(request, "Email not registered.")

    return render(request, 'users/forgot_password.html')

# ------------------ Verify OTP ------------------
def verify_otp_view(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if str(entered_otp) == str(request.session.get('otp')):
            request.session['otp_verified'] = True
            messages.success(request, "OTP verified. You can now reset your password.")
            return redirect('reset_password')
        else:
            messages.error(request, "Invalid OTP. Try again.")
    return render(request, 'users/otp_verify.html')

# ------------------ Reset Password ------------------
def reset_password_view(request):
    if not request.session.get('otp_verified'):
        messages.error(request, "You must verify OTP first.")
        return redirect('forgot_password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            email = request.session.get('reset_email')
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            # Clear session data
            request.session.pop('otp', None)
            request.session.pop('reset_email', None)
            request.session.pop('otp_verified', None)

            messages.success(request, "Password reset successful! You can log in now.")
            return redirect('login')

    return render(request, 'users/reset_password.html')


# ---------------- to make sure that dashboards work----------------


@login_required
def login_redirect_view(request):
    user = request.user
    if user.role == 'super_admin':
        return redirect('superadmin_dashboard')
    elif user.role == 'student_admin':
        return redirect('student_admin_dashboard')
    else:
        return redirect('student_dashboard')
    
# ------------------------ users Dashboard views ------------------------------

@login_required
def superadmin_dashboard(request):
    users = User.objects.all()
    games = Game.objects.all()
    rentals = Rental.objects.all().order_by('-requested_at')  # latest first

    return render(request, 'dashboard/superadmin_dashboard.html', {
        'users': users,
        'games': games,
        'rentals': rentals
    })


#--------------------- student admin Dashboard views --------------------------------
@login_required
def student_admin_dashboard(request):
    # Show games they added
    games = Game.objects.filter(added_by=request.user)

    # Show rentals for those games
    rentals = Rental.objects.filter(game__added_by=request.user)

    return render(request, 'dashboard/student_admin_dashboard.html', {
        'games': games,
        'rentals': rentals
    })

#------------------------- Student dasboard views -----------------------
@login_required
def student_dashboard(request):
    games = Game.objects.filter(available=True)
    rentals = Rental.objects.filter(user=request.user)
    return render(request, 'dashboard/student_dashboard.html', {'games': games, 'rentals': rentals})