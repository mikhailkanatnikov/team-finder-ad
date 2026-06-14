from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("list/", views.project_list, name="list"),
    path("create-project/", views.create_project, name="create"),
    path("<int:pk>/", views.project_detail, name="details"),
    path(
        "<int:pk>/toggle-participate/",
        views.toggle_participate,
        name="toggle-participate",
    ),
    path("<int:pk>/complete/", views.complete_project, name="complete"),
    path("<int:pk>/edit/", views.edit_project, name="edit"),
    path("skills/", views.skill_autocomplete, name="skill_autocomplete"),
    path("<int:pk>/skills/add/", views.add_skill, name="add_skill"),
    path(
        "<int:pk>/skills/<int:skill_id>/remove/",
        views.remove_skill,
        name="remove_skill",
    ),
]