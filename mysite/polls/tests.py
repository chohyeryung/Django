import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30) #너무 길어서 변수에 넣음 30일 후
        future_question = Question(pub_date=time)

        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1) #하루하고 1초 전
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59) #23시간 59분 59초 전
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)   #지금으로부터 며칠후에
    return Question.objects.create(question_text=question_text, pub_date=time)  #미래에 question 만드는

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')

        self.assertQuerysetEqual(response.context['lastest_question_list'], [])

    def test_past_question(self):
        create_question(question_text='Past question.', days=-30)   #30일 전
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['lastest_question_list'], ['<Question:Past question.>'])

    def test_future_question(self):
        create_question(question_text='Future question.', days=30)  #30일 후
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available.')

        self.assertQuerysetEqual(response.context['lastest_question_list'], [])

    def test_future_question_and_past_question(self):
        create_question(question_text='Past question.', days=-30)    #30일 전
        create_question(question_text='Future question.', days=30)  #30일 후
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question:Past question.>'])

    def test_two_past_question(self):
        create_question(question_text='Past question 1.', days=-30)    #30일 전
        create_question(question_text='Past question 2.', days=-5)   #5일 전
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['lastest_question_list'], ['<Question:Past question 2.>', '<Question: Past question 1.>'])

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)  #미래는 안보여야함

    def test_past_question(self):
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

