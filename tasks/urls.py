from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tasks', views.TaskViewSet, basename='task')
router.register(r'categories', views.TaskCategoryViewSet, basename='category')
router.register(r'notifications', views.NotificationViewSet,
                basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
