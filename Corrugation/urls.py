from django.urls import path
from .views import search_reels, paper_reels, update_reel, delete_reel, restore_reel

urlpatterns = [
    path('paper_reels/', paper_reels, name='paper_reels'),
    path('search_reels/', search_reels, name='search_reels'),
    path('update_reel/<int:pk>/', update_reel, name='update_reel'),
    path('delete_reel/<int:pk>/', delete_reel, name='delete_reel'),
    path('restore_reel/<int:pk>/', restore_reel, name='restore_reel'),
]
