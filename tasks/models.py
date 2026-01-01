from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class TaskCategory(models.Model):
    """Task Categories"""
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='categories')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'user')
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    RECURRENCE_CHOICES = [
        ('none', 'No Recurrence'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    # Basic fields
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Status and priority
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Dates
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    # User relationship
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tasks')

    # Categories and recurrence
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    recurrence = models.CharField(
        max_length=10,
        choices=RECURRENCE_CHOICES,
        default='none'
    )

    # Collaborative tasks
    shared_with = models.ManyToManyField(
        User,
        blank=True,
        related_name='shared_tasks'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'due_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        from django.core.exceptions import ValidationError
        # Validate due date is in future
        if self.due_date < timezone.now():
            raise ValidationError("Due date must be in the future.")

        # Prevent editing completed tasks
        if self.status == 'completed' and self.id:
            original = Task.objects.filter(id=self.id).first()
            if original and original.status != 'completed':
                raise ValidationError("Completed tasks cannot be edited.")

    def save(self, *args, **kwargs):
        # Record completion time
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'completed':
            self.completed_at = None

        super().save(*args, **kwargs)

    def time_remaining(self):
        """Get time remaining until due date"""
        now = timezone.now()
        if self.due_date > now:
            return self.due_date - now
        return timedelta(0)

    def is_overdue(self):
        """Check if task is overdue"""
        return timezone.now() > self.due_date and self.status != 'completed'

    def is_due_soon(self, hours=24):
        """Check if due date is within specified hours"""
        now = timezone.now()
        threshold = now + timedelta(hours=hours)
        return now < self.due_date <= threshold


class TaskHistory(models.Model):
    """Track task history"""
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='history')
    status_changed_from = models.CharField(max_length=20)
    status_changed_to = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = 'Task Histories'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.task.title}: {self.status_changed_from} -> {self.status_changed_to}"


class Notification(models.Model):
    """Notifications"""
    NOTIFICATION_TYPES = [
        ('due_soon', 'Task Due Soon'),
        ('overdue', 'Task Overdue'),
        ('shared', 'Task Shared'),
        ('completed', 'Task Completed'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications')
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
