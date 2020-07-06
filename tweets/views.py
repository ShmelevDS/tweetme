from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.utils.http import is_safe_url
from django.conf import settings

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Tweet
from .forms import TweetForm
from .serializers import TweetSerializer, TweetActionSerializer, TweetCreateSerializer


ALLOWED_HOSTS = settings.ALLOWED_HOSTS

def home_view(request):
    return render(request, 'pages/home.html', context={}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @authentication_classes([SessionAuthentication])
def tweet_create_view(request, *args, **kwargs):
    serializer = TweetCreateSerializer(data=request.POST or None)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)    
    return Response({}, status=400)


@api_view(['GET'])
def tweet_list_view(request, *args, **kwargs):
    tweets = Tweet.objects.all()
    serializer = TweetSerializer(tweets, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def tweet_detailed_view(request, tweet_id, *args, **kwargs):
    tweets = Tweet.objects.filter(id=tweet_id)
    if not tweets.exists():
        return Response({}, status=404)
    obj = tweets.first()
    serializer = TweetSerializer(obj)
    return Response(serializer.data, status=200)


@api_view(['DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def tweet_delete_view(request, tweet_id, *args, **kwargs):
    tweets = Tweet.objects.filter(id=tweet_id)
    if not tweets.exists():
        return Response({}, status=404)
    tweets = tweets.filter(user=request.user)
    if not tweets.exists():
        return Response({'message': 'You cannot delete this tweet!'}, status=403)
    obj = tweets.first()
    obj.delete()
    return Response({'message': 'Tweet has been successfully deleted!'}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tweet_action_view(request, *args, **kwargs):
    serializer = TweetActionSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data = serializer.validated_data
        tweet_id = data.get('id')
        action = data.get('action')
        content = data.get('content')

        tweets = Tweet.objects.filter(id=tweet_id)
        if not tweets.exists():
            return Response({}, status=404)
        
        obj = tweets.first()
        if action == 'like':
            obj.likes.add(request.user)
            serializer = TweetSerializer(obj)
            return Response(serializer.data, status=200)
        elif action == "unlike":
            obj.likes.remove(request.user)
            serializer = TweetSerializer(obj)
            return Response(serializer.data, status=200)
        elif action == 'retweet':
            new_tweet = Tweet.objects.create(user=request.user, parent=obj, content=content)
            serializer = TweetSerializer(new_tweet)
            return Response(serializer.data, status=201)
