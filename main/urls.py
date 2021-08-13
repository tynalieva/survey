from django.urls import path
from main.views import *

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('category/<str:slug>/', CategoryDetailView.as_view(), name='category'),
    path('post_detail/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post_create/', post_create, name='post_create'),
    path('post_update/<int:pk>/', post_update, name='post_update'),
    path('post_delete/<int:pk>/', PostDeleteView.as_view(), name='post_delete'),
    path('like_post/<int:pk>/', like, name='like_post'),
    path('<int:pk>/comment_create/', CommentCreateView.as_view(), name='comment_create'),
]