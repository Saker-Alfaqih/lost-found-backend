"""
Support App Models
Mapped from Flutter lib/models/admin_models.dart - SupportTicket section
"""

from django.db import models


class TicketStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    IN_PROGRESS = 'inProgress', 'In Progress'
    WAITING_FOR_USER = 'waitingForUser', 'Waiting For User'
    RESOLVED = 'resolved', 'Resolved'
    CLOSED = 'closed', 'Closed'


class TicketPriority(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'


class TicketType(models.TextChoices):
    INQUIRY = 'inquiry', 'Inquiry'
    COMPLAINT = 'complaint', 'Complaint'
    SUGGESTION = 'suggestion', 'Suggestion'
    TECHNICAL_ISSUE = 'technicalIssue', 'Technical Issue'
    ACCOUNT_ISSUE = 'accountIssue', 'Account Issue'
    OTHER = 'other', 'Other'


class SupportTicket(models.Model):
    """
    Support Ticket model for user support
    Mapped from Flutter SupportTicket model in admin_models.dart
    """
    id = models.CharField(max_length=255, primary_key=True)
    ticket_number = models.CharField(max_length=50, unique=True)
    user_id = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255)
    user_email = models.EmailField()
    
    type = models.CharField(max_length=20, choices=TicketType.choices)
    priority = models.CharField(max_length=20, choices=TicketPriority.choices, default=TicketPriority.MEDIUM)
    status = models.CharField(max_length=20, choices=TicketStatus.choices, default=TicketStatus.OPEN)
    
    subject = models.CharField(max_length=500)
    description = models.TextField()
    related_item_id = models.CharField(max_length=255, null=True, blank=True)
    assigned_admin_id = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'support_tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['assigned_admin_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Ticket #{self.ticket_number}: {self.subject}"


class TicketMessage(models.Model):
    """
    Individual messages within a support ticket
    Mapped from Flutter TicketMessage model in admin_models.dart
    """
    id = models.CharField(max_length=255, primary_key=True)
    ticket = models.ForeignKey(SupportTicket, related_name='messages', on_delete=models.CASCADE)
    sender_id = models.CharField(max_length=255)
    sender_name = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ticket_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['ticket']),
            models.Index(fields=['sender_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Message from {self.sender_name} in Ticket {self.ticket.ticket_number}"