from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.core.paginator import Paginator

from .forms import RegistrationForm, ProfileForm
from users.models import User


def paginate_queryset(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("projects:list")
    else:
        form = RegistrationForm()
    return render(request, "users/register.html", {"form": form})


def user_detail(request, pk):
    user = User.objects.filter(pk=pk).first()
    if not user:
        return render(request, "404.html", status=404)
    projects = user.owned_projects.all().order_by("-created_at")
    return render(
        request, "users/user-details.html", {"user_obj": user, "projects": projects}
    )


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:detail", pk=request.user.pk)
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


def user_list(request):
    users_list = User.objects.all().order_by("id")
    page_obj = paginate_queryset(request, users_list)
    return render(request, "users/participants.html", {"page_obj": page_obj})


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    form_class = CustomLoginForm