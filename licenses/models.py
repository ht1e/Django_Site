from django.db import models

class License(models.Model):
    key = models.CharField(max_length=255, unique=True)  # Khóa license duy nhất
    expiration_date = models.DateField(blank=True, null=True)  # Ngày hết hạn
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('deactive', 'Deactive')])  # Trạng thái
    created_at = models.DateTimeField(auto_now_add=True)  # Thời gian tạo
    hardware_id = models.CharField(max_length=255, default=None, blank=True, null=True) #thiết bị

    def __str__(self):
        return self.key