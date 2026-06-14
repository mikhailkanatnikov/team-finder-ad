from django.db import models
from users.models import User

NAME_MAX_LENGTH = 200
STATUS_MAX_LENGTH = 6
STATUS_OPEN = "open"
STATUS_CLOSED = "closed"


class Skill(models.Model):
    name = models.CharField(max_length=124, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_CLOSED, "Closed"),
    ]

    name = models.CharField(max_length=NAME_MAX_LENGTH)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_projects"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=STATUS_MAX_LENGTH, choices=STATUS_CHOICES, default=STATUS_OPEN
    )
    participants = models.ManyToManyField(
        User, related_name="participated_projects", blank=True
    )
    skills = models.ManyToManyField(Skill, related_name="projects", blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name