from django.urls import path,include
from .views import update_profile,update_preference,get_ratio,get_moodhistory,add_moodlog,get_tasks,update_tasks

urlpatterns = [
    path('auth/',include('djoser.urls')),
    path('auth/',include('djoser.urls.jwt')),
    path('update_profile/<int:user>', update_profile),
    path('update_preference/<int:user>', update_preference),
    path('update_tasks/<int:user>', update_tasks),
    path('get_ratio/<int:user>', get_ratio),
    path('get_moodhistory/<int:user>', get_moodhistory),
    path('get_tasks/<int:user>',get_tasks),
    path('add_moodlog/', add_moodlog),
    
    
]
