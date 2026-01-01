from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from .models import Task, TaskCategory, TaskHistory, Notification
from .serializers import (
    TaskSerializer, TaskCategorySerializer,
    TaskHistorySerializer, NotificationSerializer
)
from .permissions import IsTaskOwner


class TaskViewSet(viewsets.ModelViewSet):
    """
    Task CRUD operations with filtering, sorting, and status management.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskOwner]
    filter_backends = [DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status', 'priority', 'category']
    ordering_fields = ['due_date', 'priority', 'created_at']
    ordering = ['-created_at']
    search_fields = ['title', 'description']

    def get_queryset(self):
        """Get tasks for current user only"""
        return Task.objects.filter(user=self.request.user) | Task.objects.filter(shared_with=self.request.user)

    def perform_create(self, serializer):
        """Create task and assign to current user"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Update task with history tracking"""
        old_status = self.get_object().status
        task = serializer.save()

        # Create history record if status changed
        if old_status != task.status:
            TaskHistory.objects.create(
                task=task,
                status_changed_from=old_status,
                status_changed_to=task.status,
                changed_by=self.request.user
            )

            # Create notification
            Notification.objects.create(
                user=self.request.user,
                task=task,
                notification_type='completed' if task.status == 'completed' else 'status_changed',
                message=f"Task '{task.title}' marked as {task.status}"
            )

    @action(detail=True, methods=['patch'])
    def mark_complete(self, request, pk=None):
        """Mark task as complete"""
        task = self.get_object()
        self.check_object_permissions(request, task)

        task.status = 'completed'
        task.save()

        TaskHistory.objects.create(
            task=task,
            status_changed_from='pending',
            status_changed_to='completed',
            changed_by=request.user
        )

        Notification.objects.create(
            user=request.user,
            task=task,
            notification_type='completed',
            message=f"Task '{task.title}' completed"
        )

        return Response(
            TaskSerializer(task).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['patch'])
    def mark_incomplete(self, request, pk=None):
        """Mark task as incomplete (revert from completed)"""
        task = self.get_object()
        self.check_object_permissions(request, task)

        old_status = task.status
        task.status = 'pending'
        task.completed_at = None
        task.save()

        TaskHistory.objects.create(
            task=task,
            status_changed_from=old_status,
            status_changed_to='pending',
            changed_by=request.user
        )

        return Response(
            TaskSerializer(task).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def upcoming_deadline(self, request):
        """Get tasks with deadline within 24 hours"""
        now = timezone.now()
        threshold = now + timedelta(hours=24)

        tasks = Task.objects.filter(
            user=request.user,
            status__in=['pending', 'in_progress'],
            due_date__lte=threshold,
            due_date__gte=now
        ).order_by('due_date')

        serializer = TaskSerializer(tasks, many=True)
        return Response({
            'count': tasks.count(),
            'tasks': serializer.data
        })

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue tasks"""
        now = timezone.now()
        tasks = Task.objects.filter(
            user=request.user,
            status__in=['pending', 'in_progress'],
            due_date__lt=now
        ).order_by('due_date')

        serializer = TaskSerializer(tasks, many=True)
        return Response({
            'count': tasks.count(),
            'tasks': serializer.data
        })

    @action(detail=True, methods=['post'])
    def share_task(self, request, pk=None):
        """Share task with other users"""
        task = self.get_object()
        self.check_object_permissions(request, task)

        username = request.data.get('username')
        if not username:
            return Response(
                {'error': 'Username is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user_to_share = User.objects.get(username=username)

            if user_to_share == task.user:
                return Response(
                    {'error': 'Cannot share task with yourself'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            task.shared_with.add(user_to_share)

            # Create notification
            Notification.objects.create(
                user=user_to_share,
                task=task,
                notification_type='shared',
                message=f"Task '{task.title}' shared with you by {request.user.username}"
            )

            return Response(
                {'message': f'Task shared with {username}'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class TaskCategoryViewSet(viewsets.ModelViewSet):
    """CRUD operations for task categories"""
    serializer_class = TaskCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TaskCategory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only notifications for current user"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['patch'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read"""
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return Response(
            {'message': 'All notifications marked as read'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return Response({'unread_count': count})
