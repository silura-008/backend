from datetime import date

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

import requests
from rest_framework.permissions import AllowAny

from .models import Profile, Preference, MoodLog, Task, Ratio
from .serializers import ProfileSerializer, PreferenceSerializer, MoodLogSerializer, TaskSerializer, RatioSerializer


# Profile
@api_view(['GET']) 
def get_profile(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    return Response({
    "name": profile.name,
    "email":profile.user.email,
    "country": profile.country,
  }, status=status.HTTP_200_OK)

@api_view(['PUT'])
def update_profile(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    try:
        preference = Preference.objects.get(user=user)
    except Preference.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    profdata = {
               "user":user.id,
               "name" :request.data["name"],
               "country":request.data["country"]
               }
    prefdata = {
               "user":user.id,
               "on_happy":request.data["on_happy"],
               "on_sad" :request.data["on_sad"],
               "on_angry": request.data["on_angry"],
               "on_anxious": request.data["on_anxious"],
               "on_fear": request.data["on_fear"]
               }
    profserializer = ProfileSerializer(profile, data=profdata)
    prefserializer = PreferenceSerializer(preference, data=prefdata)
    if profserializer.is_valid() and prefserializer.is_valid():
        profserializer.save()
        prefserializer.save()
        return Response({'success': True}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Preference

@api_view(['GET']) 
def get_preference(request):
    user = request.user
    try:
        preference = Preference.objects.get(user=user)
    except Preference.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = PreferenceSerializer(preference)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Ratio
@api_view(['GET']) 
def get_ratio(request):
    user = request.user
    try:
        ratio = Ratio.objects.get(user=user)
    except Ratio.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = RatioSerializer(ratio)
    return Response(serializer.data, status=status.HTTP_200_OK)

# MoodLog history
@api_view(['GET']) 
def get_moodhistory(request):
    user = request.user
    moodhistory = MoodLog.objects.filter(user=user).order_by('-date')[:7]
    serializer = MoodLogSerializer(moodhistory, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Moodlog entry
@api_view(['POST'])
def add_moodlog(request):
    user = request.user
    exsiting_log = MoodLog.objects.filter(user=user, date=date.today()).first()
    if(exsiting_log):
        data = request.data
        data['user']= user.id
        serializer = MoodLogSerializer(exsiting_log,data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        data = request.data
        data['user']= user.id
        serializer = MoodLogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Task getting
def create_tasks():
    return {
        "Take a walk":False,
        "Read a book":False,
        "Water a plant":False,
        "Excercise 30 minuts":False,
        "Talk to a friend":False
    }
@api_view(['GET']) 
def get_tasks(request): 
    user = request.user
    expired_task = Task.objects.filter(user=user).order_by('date').first()
    existing_task = Task.objects.filter(user=user,date=date.today()).first()
    if(expired_task):
        if(expired_task.date < date.today()):
            expired_task.delete()   

    if(existing_task):
        serializer = TaskSerializer(existing_task)
        return Response(serializer.data,status=status.HTTP_200_OK)
    else:
        new_task = Task.objects.create(user=user,date=date.today(),tasks=create_tasks())
        serializer = TaskSerializer(new_task)
        return Response(serializer.data,status=status.HTTP_200_OK)

# Task updating
@api_view(['PUT'])
def update_tasks(request):
    user = request.user
    try:
        task = Task.objects.get(user=user,date= date.today())
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    data = request.data
    data['user']= user.id
    serializer = TaskSerializer(task, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
 
# chat
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"
@api_view(['POST'])
@permission_classes([AllowAny])
def chatt(request):
    
    # user = request.user.id
    user = 3
    message = request.data.get("message")
    
    payload = {
        "sender":user,
        "message":message
    }
    headers={
        "Content-type":"application/json"
    }
    
    try:
        response = requests.post(RASA_URL,json=payload,headers=headers).json()
        # profile = Profile.objects.filter(user=user).first()  
        # profile.conversation.append({})
        return Response(response,status=200)
    except:
        return Response({"got an error"},status=500)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def chat(request):
    
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    
    messege = request.data
    if not isinstance(profile.conversation, list):
        profile.conversation = []
    profile.conversation.append(messege["newMsg"])
    profile.save()
    return Response({"added messege to conversation"}, status=status.HTTP_201_CREATED)
  

  
@api_view(['POST'])
def clear_conversation(request):
    user = request.user
    profile = Profile.objects.filter(user=user).first()  
    if profile:
        profile.conversation = []
        profile.save()
        return Response({'conversation cleared'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
   
   
@api_view(['GET'])
def get_conversation(request):
    user = request.user
    profile = Profile.objects.filter(user=user).first()  
    if profile:
         
        return Response({'conversation': profile.conversation}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    




# @permission_classes([AllowAny])