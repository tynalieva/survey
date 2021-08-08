from django.urls import path
from main.views import *

urlpatterns = [
    path('', index, name='home'),
    path('category/<str:slug>/', category_detail, name='category'),
    # path('create_post/', CreatePostView.as_view(), name='create_post'),
    path('post_detail/<int:pk>/', post_detail, name='post_detail'),
    path('post_create/', post_create, name='post_create'),
    path('post_update/<int:pk>/', post_update, name='post_update'),
    path('post_delete/<int:pk>/', post_delete, name='post_delete'),
]