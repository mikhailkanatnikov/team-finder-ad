import json
from http import HTTPStatus

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Project, Skill
from .forms import ProjectForm


def paginate_queryset(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def project_list(request):
    skills_list = Skill.objects.all().order_by("name")
    active_skill = request.GET.get("skill")

    projects_list = Project.objects.all().order_by("-created_at")
    if active_skill:
        projects_list = projects_list.filter(skills__name__iexact=active_skill)

    page_obj = paginate_queryset(request, projects_list)

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
    project = Project.objects.filter(pk=pk).first()
    if not project:
        return render(request, "404.html", status=404)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def toggle_participate(request, pk):
    project = Project.objects.filter(pk=pk).first()
    if not project:
        return JsonResponse(
            {"error": "Project not found"}, status=HTTPStatus.NOT_FOUND
        )

    is_participant = project.participants.filter(pk=request.user.pk).exists()
    if is_participant:
        project.participants.remove(request.user)
        is_participant = False
    else:
        project.participants.add(request.user)
        is_participant = True

    return JsonResponse({"status": "ok", "participant": is_participant})


@login_required
def complete_project(request, pk):
    project = Project.objects.filter(pk=pk, owner=request.user).first()
    if not project:
        return JsonResponse(
            {"error": "Project not found"}, status=HTTPStatus.NOT_FOUND
        )

    if project.status == "open":
        project.status = "closed"
        project.save()
        return JsonResponse({"status": "ok", "project_status": "closed"})
    return JsonResponse({"error": "Invalid status"}, status=HTTPStatus.BAD_REQUEST)


@login_required
def edit_project(request, pk):
    project = Project.objects.filter(pk=pk, owner=request.user).first()
    if not project:
        return render(request, "404.html", status=404)

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


@login_required
@require_POST
def add_skill(request, pk):
    project = Project.objects.filter(pk=pk, owner=request.user).first()
    if not project:
        return JsonResponse(
            {"error": "Project not found"}, status=HTTPStatus.NOT_FOUND
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST
        )

    skill_id = data.get("skill_id")
    skill_name = data.get("name")

    if skill_id:
        skill = Skill.objects.filter(pk=skill_id).first()
        if not skill:
            return JsonResponse(
                {"error": "Skill not found"}, status=HTTPStatus.NOT_FOUND
            )
        created = False
    elif skill_name:
        skill, created = Skill.objects.get_or_create(name=skill_name.strip())
    else:
        return JsonResponse(
            {"error": "Не указан skill_id или name"},
            status=HTTPStatus.BAD_REQUEST,
        )

    added = not project.skills.filter(pk=skill.pk).exists()
    if added:
        project.skills.add(skill)

    return JsonResponse(
        {"id": skill.id, "name": skill.name, "created": created, "added": added}
    )


@login_required
@require_POST
def remove_skill(request, pk, skill_id):
    project = Project.objects.filter(pk=pk, owner=request.user).first()
    skill = Skill.objects.filter(pk=skill_id).first()

    if not project or not skill:
        return JsonResponse(
            {"error": "Project or Skill not found"}, status=HTTPStatus.NOT_FOUND
        )

    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})