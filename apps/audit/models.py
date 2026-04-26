"""
Audit App Models
Mapped from Flutter lib/models/admin_models.dart - AuditLog section
"""

from django.db import models


class AuditAction(models.TextChoices):
    USER_CREATED = 'userCreated', 'User Created'
    USER_UPDATED = 'userUpdated', 'User Updated'
    USER_DELETED = 'userDeleted', 'User Deleted'
    USER_SUSPENDED = 'userSuspended', 'User Suspended'
    USER_BANNED = 'userBanned', 'User Banned'
    USER_ACTIVATED = 'userActivated', 'User Activated'
    USER_ROLE_CHANGED = 'userRoleChanged', 'User Role Changed'
    PASSWORD_RESET = 'passwordReset', 'Password Reset'
    ITEM_CREATED = 'itemCreated', 'Item Created'
    ITEM_UPDATED = 'itemUpdated', 'Item Updated'
    ITEM_DELETED = 'itemDeleted', 'Item Deleted'
    ITEM_ARCHIVED = 'itemArchived', 'Item Archived'
    ITEM_CLOSED = 'itemClosed', 'Item Closed'
    ITEM_IMAGE_DELETED = 'itemImageDeleted', 'Item Image Deleted'
    BULK_ITEMS_DELETED = 'bulkItemsDeleted', 'Bulk Items Deleted'
    BULK_ITEMS_ARCHIVED = 'bulkItemsArchived', 'Bulk Items Archived'
    BULK_ITEMS_CLOSED = 'bulkItemsClosed', 'Bulk Items Closed'
    MATCH_CREATED = 'matchCreated', 'Match Created'
    MATCH_APPROVED = 'matchApproved', 'Match Approved'
    MATCH_REJECTED = 'matchRejected', 'Match Rejected'
    MATCH_DISMISSED = 'matchDismissed', 'Match Dismissed'
    MANUAL_MATCH_CREATED = 'manualMatchCreated', 'Manual Match Created'
    SYSTEM_SETTING_CHANGED = 'systemSettingChanged', 'System Setting Changed'
    NOTIFICATION_SENT = 'notificationSent', 'Notification Sent'
    REPORT_GENERATED = 'reportGenerated', 'Report Generated'
    DATA_EXPORTED = 'dataExported', 'Data Exported'
    TICKET_RESOLVED = 'ticketResolved', 'Ticket Resolved'
    TICKET_ASSIGNED = 'ticketAssigned', 'Ticket Assigned'
    ADMIN_LOGIN = 'adminLogin', 'Admin Login'
    ADMIN_LOGOUT = 'adminLogout', 'Admin Logout'
    LOGIN_FAILED = 'loginFailed', 'Login Failed'


class AuditLog(models.Model):
    """
    Audit Log for tracking admin actions
    Mapped from Flutter AuditLog model in admin_models.dart
    """
    id = models.CharField(max_length=255, primary_key=True)
    admin_id = models.CharField(max_length=255)
    admin_name = models.CharField(max_length=255)
    action = models.CharField(max_length=50, choices=AuditAction.choices)
    target_id = models.CharField(max_length=255, null=True, blank=True)
    target_type = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()
    
    # Store old and new values as JSON
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['admin_id']),
            models.Index(fields=['action']),
            models.Index(fields=['target_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.admin_name} - {self.action}"