from django.urls import path
from . import views
from .views import CustomLoginView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import PasswordChangeView

app_name = "users"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="/projects/list/"), name="logout"),
    path("<int:pk>/", views.user_detail, name="detail"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path(
        "change-password/",
        PasswordChangeView.as_view(
            template_name="users/change_password.html", success_url="/projects/list/"
        ),
        name="change_password",
    ),
    path("list/", views.user_list, name="list"),
]
