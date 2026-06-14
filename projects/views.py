from django.shortcuts import render
from .models import Project
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from .forms import ProjectForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Skill

from django.views.decorators.http import require_POST


def project_list(request):
    skills_list = Skill.objects.all().order_by("name")
    active_skill = request.GET.get("skill")

    projects_list = Project.objects.all().order_by("-created_at")
    if active_skill:
        projects_list = projects_list.filter(skills__name__iexact=active_skill)

    paginator = Paginator(projects_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "projects/project_list.html",
        {
            "page_obj": page_obj,
            "all_skills": skills_list,
            "active_skill": active_skill,
        },
    )


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:details", pk=project.pk)
    else:
        form = ProjectForm()
    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": False}
    )


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user in project.participants.all():
        project.participants.remove(request.user)
        is_participant = False
    else:
        project.participants.add(request.user)
        is_participant = True

    return JsonResponse({"status": "ok", "participant": is_participant})


@login_required
def complete_project(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if project.status == "open":
        project.status = "closed"
        project.save()
        return JsonResponse({"status": "ok", "project_status": "closed"})
    return JsonResponse({"status": "error"}, status=400)


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:details", pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": True}
    )


def skill_autocomplete(request):
    query = request.GET.get("q", "")
    skills = Skill.objects.filter(name__istartswith=query).order_by("name")[:10]
    data = [{"id": skill.id, "name": skill.name} for skill in skills]
    return JsonResponse(data, safe=False)


import json


@login_required
@require_POST
def add_skill(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    skill_id = data.get("skill_id")
    skill_name = data.get("name")

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
        created = False
    elif skill_name:
        skill, created = Skill.objects.get_or_create(name=skill_name.strip())
    else:
        return JsonResponse({"error": "Не указан skill_id или name"}, status=400)

    if skill in project.skills.all():
        added = False
    else:
        project.skills.add(skill)
        added = True

    return JsonResponse(
        {"id": skill.id, "name": skill.name, "created": created, "added": added}
    )


@login_required
@require_POST
def remove_skill(request, pk, skill_id):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    skill = get_object_or_404(Skill, pk=skill_id)
    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})
