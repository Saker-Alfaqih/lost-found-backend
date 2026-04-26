"""
Items App Models
Mapped from Flutter lib/models/item.dart
"""

from django.db import models


class ItemType(models.TextChoices):
    LOST = 'lost', 'Lost'
    FOUND = 'found', 'Found'


class ItemStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    RESOLVED = 'resolved', 'Resolved'


class ItemCategory(models.TextChoices):
    ELECTRONICS = 'electronics', 'Electronics'
    DOCUMENTS = 'documents', 'Documents'
    ACCESSORIES = 'accessories', 'Accessories'
    BAGS = 'bags', 'Bags'
    CLOTHING = 'clothing', 'Clothing'
    KEYS = 'keys', 'Keys'
    OTHER = 'other', 'Other'
    JEWELRY = 'jewelry', 'Jewelry'


class Item(models.Model):
    """
    Item model for Lost & Found functionality
    Mapped from Flutter Item model in item.dart
    """
    id = models.CharField(max_length=255, primary_key=True)
    reference_number = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=10, choices=ItemType.choices)
    status = models.CharField(max_length=20, choices=ItemStatus.choices, default=ItemStatus.ACTIVE)
    category = models.CharField(max_length=20, choices=ItemCategory.choices)
    title = models.CharField(max_length=500)
    description = models.TextField()
    location = models.CharField(max_length=500)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    
    # User information
    user_id = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255)
    user_phone = models.CharField(max_length=20, null=True, blank=True)
    user_email = models.EmailField(null=True, blank=True)
    
    # Images and keywords stored as JSON
    images = models.JSONField(default=list)
    keywords = models.JSONField(null=True, blank=True)
    reward = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'items'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['type']),
            models.Index(fields=['category']),
            models.Index(fields=['user_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.type}) - {self.reference_number}"