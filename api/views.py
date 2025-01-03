from datetime import date

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Profile, Preference, MoodLog, Task, Ratio
from .serializers import ProfileSerializer, PreferenceSerializer, MoodLogSerializer, TaskSerializer, RatioSerializer


# Profile
@api_view(['PUT'])
def update_profile(request, user):
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    data = request.data
    serializer = ProfileSerializer(profile, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Preference
@api_view(['PUT'])
def update_preference(request, user):
    try:
        preference = Preference.objects.get(user=user)
    except Preference.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    data = request.data
    serializer = PreferenceSerializer(preference, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Ratio
@api_view(['GET']) 
def get_ratio(request, user):
    try:
        ratio = Ratio.objects.get(user=user)
    except Ratio.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = RatioSerializer(ratio)
    return Response(serializer.data, status=status.HTTP_200_OK)

# MoodLog history
@api_view(['GET']) 
def get_moodhistory(request, user):
    moodhistory = MoodLog.objects.filter(user=user).order_by('-date')[:7]
    serializer = MoodLogSerializer(moodhistory, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Moodlog entry
@api_view(['POST'])
def add_moodlog(request):
    user = request.data["user"]
    exsiting_log = MoodLog.objects.filter(user=user, date=date.today()).first()
    if(exsiting_log):
        data = request.data
        serializer = MoodLogSerializer(exsiting_log,data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        data = request.data
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
def get_tasks(request, user): 

    expired_task = Task.objects.filter(user=user).order_by('date').first()
    if(expired_task.date < date.today()):
        expired_task.delete()
    existing_task = Task.objects.filter(user=user,date=date.today()).first()

    if(existing_task):
        if(existing_task.rate != 100):
            serializer = TaskSerializer(existing_task)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else :
            return Response({"completed":"Tasks completed for today"},status=status.HTTP_200_OK)
    else:
        new_task = Task.objects.create(user_id=user,date=date.today(),tasks=create_tasks())
        serializer = TaskSerializer(new_task)
        return Response(serializer.data,status=status.HTTP_200_OK)

# Task updating
@api_view(['PUT'])
def update_tasks(request, user):
    try:
        task = Task.objects.get(user=user,date= date.today())
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    data = request.data
    serializer = TaskSerializer(task, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)