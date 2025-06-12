from django.urls import path
from .views import * 

urlpatterns = [
    path('get/all-news/', list_news),
    path('get/news-detail/<int:news_id>/', get_news_detail),
    path('post/reactions/<int:news_id>/', create_or_update_reaction),
   
]
