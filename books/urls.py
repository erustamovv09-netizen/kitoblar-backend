from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, BookViewSet, AdminStatsView, LoginView, RegisterView, PingView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'books', BookViewSet, basename='book')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/ping/', PingView.as_view(), name='ping'),
]
