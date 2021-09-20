from django.urls import path
from .views import ChatCreateView, ChatDetailView, ChatDetailViewtwo
urlpatterns = [
    path('new/chat_message/',ChatCreateView.as_view(), name='chat_create' ),
    path('<int:pk>/chat_detail/', ChatDetailView.as_view(), name='chat_detail'),
    path('<int:pk>/chat_detailtwo/', ChatDetailViewtwo, name='chat_detailtwo'),
]