# directory/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Location, Department, Person, ClientEntry, ZohoApp

# --------------------------
# Location
# --------------------------
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "timezone")
    search_fields = ("name", "timezone")
    list_filter = ("timezone",)


# --------------------------
# Department
# --------------------------
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name",)
    list_filter = ("parent",)


# --------------------------
# Person
# --------------------------
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("display_name", "role", "location",
                    "department", "email", "verified")
    search_fields = ("first_name", "last_name",
                     "display_name", "email", "role")
    list_filter = ("location", "department", "verified")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("location", "department", "manager")
    fieldsets = (
        (None, {
            "fields": ("first_name", "last_name",
                       "display_name", "role", "bio", "verified")
        }),
        ("Contact", {
            "fields": ("email", "phone", "desk_number", "cliq_handle")
        }),
        ("Org", {
            "fields": ("location", "department", "manager")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


# --------------------------
# Client Entry
# --------------------------
@admin.register(ClientEntry)
class ClientEntryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "location", "department", "created_at")
    list_filter = ("location", "department", "created_at")
    search_fields = ("name", "email", "notes")
    readonly_fields = ("created_at",)


# --------------------------
# Zoho App
# --------------------------
@admin.register(ZohoApp)
class ZohoAppAdmin(admin.ModelAdmin):
    list_display = ("name", "tagline", "popularity", "rating",
                    "last_updated", "doc_link")
    search_fields = ("name", "tagline", "tags")
    list_filter = ("tags",)
    readonly_fields = ("last_updated",)
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        (None, {
            "fields": ("name", "slug", "tagline", "description", "icon")
        }),
        ("Details", {
            "fields": ("use_cases", "who", "tags", "doc",
                       "internal_runbook", "cliq_channel", "access")
        }),
       
        ("Meta", {
            "fields": ("help_contact", "popularity", "rating", "last_updated")
        }),
        
        ("Guide", {
    "fields": ("guide_url", "guide_file"),
    "description": "YouTube/Loom link OR upload MP4 file"
}),
    )
    
    # directory/admin.py (ZohoAppAdmin fieldsets)
    # directory/admin.py (ZohoAppAdmin fieldsets)
   

    @admin.display(description="Docs", ordering="doc")
    def doc_link(self, obj):
        if obj.doc:
            return format_html('<a href="{}" target="_blank">Open</a>', obj.doc)
        return "-"