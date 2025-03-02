from datetime import date
import random
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
    return Response({'error'}, status=status.HTTP_400_BAD_REQUEST)

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



def create_tasks(personality):
    tasks = {
        "new": [  
            "Engage in light movement like stretching or walking",  
            "Do a 5-minute deep breathing exercise",  
            "Reflect on three good things that happened today",  
            "Maintain a simple journal entry about your thoughts",  
            "Spend a few minutes in mindful silence without distractions",  
            "Observe and describe your surroundings to ground yourself",  
            "Engage in a short guided meditation",  
            "Write down a small goal for the day and accomplish it",  
            "Organize a small part of your space",  
            "Listen to a calming, neutral podcast"
        ],
        "joy": [ 
            "Do an activity that brings you joy (reading, listening to music, etc.)",  
            "Engage in light social interaction with someone you enjoy talking to",  
            "Recall a happy memory and write it down",  
            "Do a creative task that doesn't feel forced (sketching, casual writing)",  
            "Take a moment to deeply enjoy something small (a breeze, a song, a scent)",  
            "Practice active appreciation—verbalize or note what you like about the moment",  
            "Strengthen self-compassion by writing down kind words to yourself",  
            "Send a positive message to a friend or acquaintance",  
            "Spend a few minutes in natural sunlight"
        ],
        "sorrow": [   
            "Talk to a trusted person about how you're feeling",  
            "Write down your thoughts and emotions without filtering them",  
            "Do controlled deep breathing to regulate distress",  
            "Engage in a simple, repetitive physical activity like pacing or stretching",    
            "Use the 'name it to tame it' method—verbalize exactly what you're feeling",  
            "Try gentle grounding—touch a textured object and describe it in detail",  
            "Allow yourself to cry if needed, then focus on deep breaths afterward",  
            "Engage in a short distraction task (sorting objects, organizing files)",  
            "Repeat a comforting phrase or affirmation to yourself"
        ],
        "fury": [  
            "Write down your frustration in detail and then tear or delete it",  
            "Engage in a controlled physical release (walking, push-ups, or squeezing a stress ball)",  
            "Do progressive muscle relaxation—clench and release your fists slowly",  
            "Practice cognitive distancing—ask, 'Will this matter in a week?'",  
            "Redirect energy into an intentional task (solving a puzzle, organizing)",  
            "Listen to neutral instrumental music to slow down thoughts",  
            "Step outside and focus on deep, slow breathing",  
        ],
        "nervous": [
            "Identify the worst-case scenario and rationalize it",  
            "Write down what's making you anxious and separate fact from assumption",  
            "Engage in a repetitive, calming activity (tapping fingers, doodling, sorting objects)",  
            "Listen to a structured guided breathing or grounding exercise",  
            "Hold a textured object and describe its feeling to yourself",  
            "Challenge irrational thoughts with logical counterarguments",  
            "Take a slow, deliberate walk while focusing on your steps",  
            "Redirect focus by completing a simple mental task (math problem, word puzzle)",  
            "Talk to someone who can provide reassurance and logical perspective"
        ],
    }
    
    tasks_by_personality = tasks.get(personality, tasks["new"])
    selected_tasks = random.sample(tasks_by_personality, 5)
    return {task: False for task in selected_tasks}


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
        ratio = Ratio.objects.get(user=user)
        new_task = Task.objects.create(user=user,date=date.today(),tasks=create_tasks(ratio.get_max_ratio_emotion()))
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

def send_message_to_rasa(user_id, message):
    payload = {"sender": str(user_id), "message": message}
    try:
        response = requests.post(RASA_URL, json=payload, timeout=5)
        response_data = response.json()
        return response_data
    except requests.exceptions.RequestException as e:
        return False

@api_view(['POST'])
def chat(request):
    
    # user = request.user.id
    user = request.user
    user_message = request.data["newMsg"]["text"]
    
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


    bot_response = send_message_to_rasa(user.id, user_message)
    if bot_response :
        profile.append_to_conversation("user", user_message)
        profile.append_to_conversation("bot", bot_response[0]["text"])
        return Response({'user':user_message,'bot':bot_response[0]["text"]}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Could not connect to chatbot.'}, status=status.HTTP_404_NOT_FOUND)

  
@api_view(['POST'])
def clear_conversation(request):
    user = request.user
    profile = Profile.objects.filter(user=user).first()  
    if profile:
        profile.conversation = []
        profile.save()
        res = send_message_to_rasa(user.id,"/restart")
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
    
# Rasa 
@api_view(['POST'])
@permission_classes([AllowAny])
def get_initial(request):
    user = request.data.user_id
    profile = Profile.objects.filter(user=user).first()

    if not profile:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
    
    preference_instance = Preference.objects.filter(user=user).first()  
    preference = {
        'sad': [key for key, value in preference_instance.on_sad.items() if value],
        'anger': [key for key, value in preference_instance.on_angry.items() if value],
        'anxious': [key for key, value in preference_instance.on_anxious.items() if value],
        'fear': [key for key, value in preference_instance.on_fear.items() if value],
    }
    ratio = Ratio.objects.get(user=user)
    return Response({"personality": ratio.get_max_ratio_emotion(),
                     "preference":preference,
                     "helpline":get_hotline(profile.country)}
    , status=status.HTTP_200_OK)



country_emergency_numbers = {
    'Albania': '112',
    'Argentina': '135',
    'Australia': '13 11 14',
    'Austria': '142',
    'Belgium': '106',
    'Brazil': '188',
    'Canada': '1-833-456-4566',
    'Chile': '600-360-7777',
    'China': '400-161-9995',
    'Colombia': '1-800-518-2211',
    'Denmark': '70 201 201',
    'Finland': '09-2525 0111',
    'France': '01 45 39 40 00',
    'Germany': '0800 111 0 111',
    'Iceland': '1717',
    'India': '91-22-2772 6771',
    'Ireland': '116 123',
    'Israel': '1201',
    'Italy': '199 284 284',
    'Japan': '03-5774-0992',
    'Korea, South': '1588-9191',
    'Mexico': '800-911-2000',
    'Nepal': '01-4287333',
    'Netherlands': '0900 0113',
    'New Zealand': '0800 543 354',
    'Norway': '116 123',
    'Pakistan': '021-3481 4450',
    'Singapore': '1800-221-4444',
    'South Africa': '0861 322 322',
    'Spain': '717-003-717',
    'Taiwan': '1995',
    'United Kingdom': '116 123',
    'United States': '988',
}

def get_hotline(country):
    country = country.strip().lower()
    
    for key, value in country_emergency_numbers.items():
        if country in key.lower():
            return value
    return "988"
       

# @permission_classes([AllowAny])


# [{"id": 1, "sender": "user", "text": "hi", "timestamp": "2025-02-06T15:57:51.817Z", "time": "09:27 PM"}, {"id": 2, "sender": "user", "text": "how are you", "timestamp": "2025-02-06T15:57:57.197Z", "time": "09:27 PM"}, {"id": 3, "sender": "user", "text": "gotta go", "timestamp": "2025-02-06T15:58:02.573Z", "time": "09:28 PM"}, {"id": 1, "sender": "user", "text": "hlo", "timestamp": "2025-02-10T17:31:16.604Z", "time": "11:01 PM"}]