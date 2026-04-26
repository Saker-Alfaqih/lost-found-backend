"""
Matches App Models
Mapped from Flutter lib/models/match.dart
"""

from django.db import models


class MatchType(models.TextChoices):
    HIGH = 'high', 'High'
    MEDIUM = 'medium', 'Medium'
    LOW = 'low', 'Low'


class SmartMatch(models.Model):
    """
    Smart Match model linking lost and found items
    Mapped from Flutter SmartMatch model in match.dart
    """
    id = models.CharField(max_length=255, primary_key=True)
    lost_item_id = models.CharField(max_length=255)
    found_item_id = models.CharField(max_length=255)
    
    # Similarity scores (stored as percentages 0-100)
    similarity_text = models.DecimalField(max_digits=5, decimal_places=2)
    similarity_location = models.DecimalField(max_digits=5, decimal_places=2)
    similarity_category = models.DecimalField(max_digits=5, decimal_places=2)
    similarity_date = models.DecimalField(max_digits=5, decimal_places=2)
    similarity_overall = models.DecimalField(max_digits=5, decimal_places=2)
    
    match_type = models.CharField(max_length=10, choices=MatchType.choices)
    is_reviewed = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'matches'
        ordering = ['-similarity_overall', '-created_at']
        indexes = [
            models.Index(fields=['lost_item_id']),
            models.Index(fields=['found_item_id']),
            models.Index(fields=['match_type']),
            models.Index(fields=['is_reviewed']),
            models.Index(fields=['is_dismissed']),
        ]

    def __str__(self):
        return f"Match {self.id}: {self.match_type} ({self.similarity_overall}%)"