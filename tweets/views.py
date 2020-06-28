from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.utils.http import is_safe_url
from django.conf import settings

from .models import Tweet
from .forms import TweetForm
import random


ALLOWED_HOSTS = settings.ALLOWED_HOSTS

def home_view(request):
    return render(request, 'pages/home.html', context={}, status=200)


def tweet_create_view(request, *args, **kwargs):
    form = TweetForm(request.POST or None)
    next_url = request.POST.get('next') or None
    if form.is_valid():
        obj = form.save(commit=False)
        obj.save()
        if request.is_ajax():
            return JsonResponse(obj.serialize(), status=201)
        if next_url != None and is_safe_url(next_url, ALLOWED_HOSTS):
            return redirect(next_url)
        form = TweetForm()
    if form.errors and request.is_ajax():
        return JsonResponse(form.errors, status=400)
    return render(request, 'components/form.html', context={'form': form})


def tweet_detailed_view(request, tweet_id):
    data = {
        'id': tweet_id
    }
    try:
        obj = Tweet.objects.get(id=tweet_id)
        data['content'] = obj.content
        status = 200
    except:
        data['message'] = 'Not Found'
        status = 404

    return JsonResponse(data, status=status)


def tweet_list_view(request, *qrgs, **kwargs):
    tweets = Tweet.objects.all()
    tweets_list = [tweet.serialize() for tweet in tweets]

    return JsonResponse({'isUser': False, 'response': tweets_list})