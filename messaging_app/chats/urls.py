from django.urls import path, include
from rest_framework import routers  # import routers to use routers.DefaultRouter()
from .views import ConversationViewSet, MessageViewSet

# Create a DefaultRouter instance explicitly
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# Include all router URLs
urlpatterns = [
    path('', include(router.urls)),
]