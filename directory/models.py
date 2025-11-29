# directory/models.py
import re
from django.db import models
from django.conf import settings  # if you want sender as a User, optional

# ----------------------------------------------
#   Helpers
# ----------------------------------------------
YOUTUBE_ID_RE = re.compile(r'(?:v=|youtu\.be/|embed/|/v/)([A-Za-z0-9_-]{6,})')

def extract_youtube_id(value):
    """
    Accepts:
      - raw id (e.g. '0yVgZWgR2dQ')
      - https://www.youtube.com/watch?v=ID
      - https://youtu.be/ID
      - https://www.youtube.com/embed/ID
      - pasted <iframe> HTML
    Returns the video ID string or None.
    """
    if not value:
        return None
    value = str(value).strip()

    # If it's an iframe HTML snippet, extract src
    if '<iframe' in value:
        src_m = re.search(r'src=["\']([^"\']+)["\']', value)
        if src_m:
            value = src_m.group(1)

    # If they pasted only the ID
    if re.fullmatch(r'[A-Za-z0-9_-]{6,}', value):
        return value

    # Try to extract with regex
    m = YOUTUBE_ID_RE.search(value)
    if m:
        return m.group(1)

    return None


# ----------------------------------------------
#   Location
# ----------------------------------------------
class Location(models.Model):
    name = models.CharField(max_length=120)
    address = models.TextField(blank=True)
    timezone = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return self.name


# ----------------------------------------------
#   Department
# ----------------------------------------------
class Department(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


# ----------------------------------------------
#   Person
# ----------------------------------------------
class Person(models.Model):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120, blank=True)
    display_name = models.CharField(max_length=200, blank=True)

    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    cliq_handle = models.CharField(max_length=150, blank=True)
    desk_number = models.CharField(max_length=40, blank=True)

    role = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or f"{self.first_name} {self.last_name}"


# ----------------------------------------------
#   ClientEntry
# ----------------------------------------------
class ClientEntry(models.Model):
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL, related_name='client_entries')
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name='client_entries')

    name = models.CharField(max_length=255)
    email = models.EmailField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.email}"


# ----------------------------------------------
#   ZohoApp
# ----------------------------------------------
class ZohoApp(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)

    use_cases = models.JSONField(blank=True, default=list)
    who = models.CharField(max_length=200, blank=True)

    doc = models.URLField(blank=True)
    internal_runbook = models.URLField(blank=True)
    cliq_channel = models.URLField(blank=True)
    access = models.CharField(max_length=200, blank=True)

    icon = models.ImageField(upload_to="app_icons/", blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True)

    help_contact = models.JSONField(blank=True, default=dict)

    popularity = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)

    last_updated = models.DateTimeField(auto_now=True)

    # For external links (YouTube / Loom)
    guide_url = models.URLField(blank=True, null=True, help_text="YouTube / Loom / direct mp4 link")
    guide_file = models.FileField(upload_to='guides/', blank=True, null=True, help_text="Upload MP4")

    def guide_source(self):
        """
        Return the URL to use in the frontend:
         - prefer uploaded file (guide_file.url) if present
         - otherwise return guide_url (YouTube/watch URL or direct mp4 link)
        """
        if self.guide_file:
            return self.guide_file.url
        return self.guide_url
    
    
