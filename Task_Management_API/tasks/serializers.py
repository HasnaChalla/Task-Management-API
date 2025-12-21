from rest_framework import serializers
from .models import Task
from django.utils import timezone

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'completed_at']

    def update(self, instance, validated_data):
        # Empêcher édition si completed
        if instance.status == 'completed' and validated_data.get("status") != "pending":
            raise serializers.ValidationError("Cannot edit a completed task unless reverted to pending.")
        
        # Marquer completed
        if validated_data.get("status") == "completed" and instance.status != "completed":
            validated_data["completed_at"] = timezone.now()

        return super().update(instance, validated_data)
