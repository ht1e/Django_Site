from django.contrib import admin
from .models import License

@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('key', 'expiration_date', 'status', 'created_at')  # Các trường hiển thị trong list
    search_fields = ('key',)  # Tìm kiếm theo key
    list_filter = ('status', 'expiration_date')  # Filter theo trạng thái và ngày hết hạn