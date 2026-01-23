from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SignupForm
from .models import EmailVerificationToken

def signup(request):
    """
    Standard user registration view.
    """
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            EmailVerificationToken.objects.create(user=user)
            messages.success(
                request,
                "Account created. We'll send a verification email once email delivery is enabled.",
            )
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


def verify_email(request, token):
    verification = get_object_or_404(EmailVerificationToken, token=token)
    if verification.used_at is not None:
        messages.info(request, "This verification link has already been used.")
        return redirect("home")

    verification.user.email_verified = True
    verification.user.save(update_fields=["email_verified"])
    verification.mark_used()
    messages.success(request, "Email verified successfully.")
    return redirect("home")