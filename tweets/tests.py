from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Tweet
from rest_framework.test import APIClient

# Create your tests here.

User = get_user_model()

class TweetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='abc', password='123')
        self.another_user = User.objects.create_user(username='def', password='456')
        for num in range(2):
            Tweet.objects.create(content=f'tweet number {num}', user=self.user)
        Tweet.objects.create(content=f'another users tweet', user=self.another_user)
        self.current_count = Tweet.objects.all().count()

    def test_tweet_created(self):
        tweet = Tweet.objects.create(content='my tweet', user=self.user)
        self.assertEqual(tweet.id, 4)
        self.assertEqual(tweet.content, 'my tweet')

    def get_client(self):
        client = APIClient()
        client.login(username=self.user.username, password='123')
        return client

    def test_tweet_list(self):
        client = self.get_client()
        response = client.get('/api/tweets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

    def test_action_like(self):
        client = self.get_client()
        response = client.post('/api/tweets/action/', {'id': 1, 'action': 'like'})
        self.assertEqual(response.status_code, 200)
        like_count = response.json().get('likes')
        self.assertEqual(like_count, 1)
    
    def test_action_unlike(self):
        client = self.get_client()
        response = client.post('/api/tweets/action/', {'id': 2, 'action': 'like'})
        self.assertEqual(response.status_code, 200)
        like_count = response.json().get('likes')
        self.assertEqual(like_count, 1)
        response = client.post('/api/tweets/action/', {'id': 2, 'action': 'unlike'})
        self.assertEqual(response.status_code, 200)
        like_count = response.json().get('likes')
        self.assertEqual(like_count, 0)

    def test_action_retweet(self):
        client = self.get_client()
        response = client.post('/api/tweets/action/', {'id': 2, 'action': 'retweet'})
        self.assertEqual(response.status_code, 201)
        new_tweet_id = response.json().get('id')
        self.assertNotEqual(new_tweet_id, '2')
        self.assertEqual(self.current_count + 1, new_tweet_id)

    def test_tweet_create(self):
        client = self.get_client()
        response = client.post('/api/tweets/create/', {'content': 'my glorious tweet'})
        new_tweet_id = response.json().get('id')
        self.assertEqual(self.current_count + 1, new_tweet_id)
    
    def test_tweet_details(self):
        client = self.get_client()
        response = client.get('/api/tweets/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('id'), 1)
    
    def test_tweet_delete(self):
        client = self.get_client()
        response = client.delete('/api/tweets/1/delete/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('message'), 'Tweet has been successfully deleted!')
        response = client.delete('/api/tweets/1/delete/')
        self.assertEqual(response.status_code, 404)
        response = client.delete('/api/tweets/3/delete/')
        self.assertEqual(response.status_code, 403)