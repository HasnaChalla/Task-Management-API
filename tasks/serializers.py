from rest_framework import serializers
from .models import Task, TaskCategory, TaskHistory, Notification
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class TaskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCategory
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class TaskHistorySerializer(serializers.ModelSerializer):
    changed_by_username = serializers.CharField(
        source='changed_by.username', read_only=True)

    class Meta:
        model = TaskHistory
        fields = ['id', 'status_changed_from', 'status_changed_to',
                  'changed_at', 'changed_by_username']
        read_only_fields = ['id']


class TaskSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(
        source='user.username', read_only=True)
    category_name = serializers.CharField(
        source='category.name', read_only=True, required=False)
    time_remaining = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    is_due_soon = serializers.SerializerMethodField()
    history = TaskHistorySerializer(many=True, read_only=True)
    shared_with_usernames = serializers.StringRelatedField(
        source='shared_with',
        many=True,
        read_only=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status',
            'due_date', 'created_at', 'completed_at', 'updated_at',
            'user', 'user_username', 'category', 'category_name',
            'recurrence', 'shared_with_usernames', 'time_remaining',
            'is_overdue', 'is_due_soon', 'history'
        ]
        read_only_fields = ['id', 'created_at',
                            'completed_at', 'updated_at', 'user', 'history']

    def get_time_remaining(self, obj):
        return str(obj.time_remaining())

    def get_is_overdue(self, obj):
        return obj.is_overdue()

    def get_is_due_soon(self, obj):
        return obj.is_due_soon()

    def validate_due_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "Due date must be in the future.")
        return value

    def validate(self, data):
        # Prevent editing completed tasks
        if self.instance and self.instance.status == 'completed':
            if data.get('status') != 'completed' or data.get('title') or data.get('description'):
                raise serializers.ValidationError(
                    "Completed tasks cannot be edited unless reverted to incomplete."
                )
        return data


class NotificationSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'task', 'task_title', 'notification_type',
                  'message', 'created_at', 'is_read']
        read_only_fields = ['id', 'created_at']
