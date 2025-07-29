"""Views."""

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render


@login_required
@permission_required("evemap.basic_access")
def index(request, name=None):
    context = {"text": "Hello, World!"}
    return render(request, "evemap/index.html", context)
