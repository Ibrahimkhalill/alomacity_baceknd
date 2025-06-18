
# Register your models here.
from django.contrib import admin
from .models import Advertisement, AdvertisementImage

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'title', 'category', 'views', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'serial_number')
    actions = ['approve_advertisements']

    def approve_advertisements(self, request, queryset):
        queryset.update(status='approved')
    approve_advertisements.short_description = "Approve selected advertisements"