from django.urls import path,include
from .views import get_profile,get_preference,update_profile,update_preference,get_ratio,get_moodhistory,add_moodlog,get_tasks,update_tasks,chat,get_conversation,clear_conversation

urlpatterns = [
    path('auth/',include('djoser.urls')),
    path('auth/',include('djoser.urls.jwt')),
    path('update_profile/', update_profile),
    path('update_tasks/', update_tasks),
    path('get_profile/', get_profile),
    path('get_preference/', get_preference),
    path('get_ratio/', get_ratio),
    path('get_moodhistory/', get_moodhistory),
    path('get_tasks/',get_tasks),
    path('add_moodlog/', add_moodlog),
    path('get_conversation/',get_conversation),
    path('clear_conversation/',clear_conversation),
    path('chat/', chat),
    
    
]
