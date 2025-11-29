from django.shortcuts import render, get_object_or_404
from .models import Person, Location, Department, ClientEntry
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import ClientEntryForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
import requests

from .models import ZohoApp
from django.conf import settings
from pathlib import Path
import json
def home(request):
    locations = Location.objects.all()
    location_id = request.GET.get('location')
    q = request.GET.get('q','').strip()
    people = Person.objects.select_related('department','location').all()
    if location_id:
        people = people.filter(location_id=location_id)
    if q:
        people = people.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) | 
            Q(display_name__icontains=q) | Q(role__icontains=q) | 
            Q(email__icontains=q)
        ).distinct()
    context = {'locations': locations, 'people': people, 'q': q}
    return render(request, 'directory/home.html', context)


def person_detail(request, pk):
    person = get_object_or_404(Person, pk=pk)
    return render(request, 'directory/detail.html', {'person': person})


def client_entry_page(request):
    locations = Location.objects.all()
    departments = Department.objects.all()
    return render(request, 'directory/client_entry.html', {
        'locations': locations,
        'departments': departments,
    })

@require_POST
def client_entry_create(request):
    form = ClientEntryForm(request.POST)
    if not form.is_valid():
        # return JSON errors so client can show them
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)

    entry = form.save()
    return JsonResponse({
        'ok': True,
        'entry': {
            'id': entry.id,
            'location': entry.location.id if entry.location else None,
            'department': entry.department.id if entry.department else None,
            'name': entry.name,
            'email': entry.email,
            'notes': entry.notes
        }
    })
    
    
    


def apps_list(request):
    """
    Load ZohoApp objects from DB, normalize fields for template:
      - tags_list : list[str] (normalized tags)
      - icon_url  : best-effort URL to show an icon (ImageField url or static fallback)
    This returns a list of plain dicts so template rendering is consistent whether your
    data comes from DB models or from a static JSON file.
    """
    q = request.GET.get("q", "").strip()

    # start with DB queryset (preferred)
    apps_qs = ZohoApp.objects.all().order_by("name")

    if q:
        apps_qs = apps_qs.filter(
            Q(name__icontains=q) |
            Q(tagline__icontains=q) |
            Q(description__icontains=q) |
            Q(tags__icontains=q)
        )

    apps = []
    # helper: static base url for fallback icons (if you stored string paths in 'icon')
    static_base = getattr(settings, "STATIC_URL", "/static/")
    if not static_base.endswith("/"):
        static_base = static_base + "/"

    for app in apps_qs:
        # normalize tags field into a list of strings
        raw_tags = getattr(app, "tags", "") or ""
        if isinstance(raw_tags, (list, tuple)):
            tags_list = [str(t).strip() for t in raw_tags if str(t).strip()]
        else:
            # split comma-separated string safely
            tags_list = [t.strip() for t in str(raw_tags).split(",") if t.strip()]

        # compute icon URL: prefer ImageField.url, else try treating app.icon as a static path
        icon_url = None
        icon_val = getattr(app, "icon", None)
        try:
            # If icon is an ImageFieldFile with a url attribute (uploaded media)
            if icon_val and hasattr(icon_val, "url"):
                icon_url = icon_val.url
            # If icon is stored as a string path (e.g. "directory/icons/people.png")
            elif icon_val:
                # ensure no leading slash so join works
                icon_path = str(icon_val).lstrip("/")
                icon_url = static_base + icon_path
        except Exception:
            icon_url = None

        apps.append({
            "name": app.name,
            "slug": getattr(app, "slug", "") or "",
            "tagline": app.tagline or "",
            "description": app.description or "",
            "doc": app.doc or "",
            "cliq_channel": app.cliq_channel or "",
            "internal_runbook": app.internal_runbook or "",
            "help_contact": getattr(app, "help_contact", None),
            "rating": getattr(app, "rating", None),
            "popularity": getattr(app, "popularity", 0),
            "icon_url": icon_url,
            "tags_list": tags_list,
            "who": getattr(app, "who", None),
            "access": getattr(app, "access", None),
            "guide_source": app.guide_source,   # <-- ADD THIS LINE

        })
        
        
        
        

    return render(request, "directory/apps_list.html", {"apps": apps, "q": q})




def send_to_cliq(request):
    # Paste the full webhook URL you copied from Cliq (including ?zapikey=...)
    webhook_url = "https://cliq.zoho.in/api/v2/channelsbyname/announcements/message?zapikey=1001.9668d45da95b565b627bd1ff89d12738.f2419b6dad801618261ef93d50e2d1d6"

    payload = {
        "text": "Hello from Django via webhook!"    # simplest payload
    }

    # No Authorization header for the webhook URL
    headers = {
        "Content-Type": "application/json"
    }

    resp = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
    return JsonResponse({
        "status": resp.status_code,
        "body": resp.text
    })