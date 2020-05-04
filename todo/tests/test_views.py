from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import datetime
from django.test import Client
from django.urls import reverse
from model_mommy import mommy
from ..views import *
from ..forms import TodoForm


class SignupViewTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_for_signup(self):
        self.user = mommy.make(get_user_model(), username='hello', password='punkstarz1223')
        post_data = {
            "username": self.user.username,
            "password1": self.user.password,
            "password2": self.user.password,
        }
        res = self.client.post(reverse('signupuser'),data=post_data,follow=True)
        self.assertEqual(res.status_code,200)

    def test_logged_user_cant_signup(self):
        self.user = mommy.make(get_user_model(), username='hello', password='punkstarz1223')
        self.client.force_login(self.user)
        response = self.client.get(reverse('signupuser'))
        self.assertTrue(response.context['user'].is_authenticated)


class LoginLogoutViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = mommy.make(get_user_model())

    def test_successful_login(self):
        self.user = mommy.make(get_user_model(),username='hello',password='hello123')
        self.client.login(username=self.user.username, password=self.user.password)
        response = self.client.get(reverse('loginuser'), follow=True)
        user = User.objects.get(username=self.user.username)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(response.status_code,200)

    def test_unsuccessful_login(self):
        response = self.client.post(reverse('loginuser'), {
            'username': self.user.username,
            'password': self.user.password
        })
        self.assertTrue(response.context['error'])

    def test_logout_view(self):
        self.client.login(username=self.user.username,password=self.user.password)
        res = self.client.get(reverse('logoutuser'))
        self.assertEqual(res.status_code, 302)


class TodoViews(TestCase):

    def setUp(self):
        self.user = mommy.make(get_user_model())
        self.todo = mommy.make(Todo,user=self.user)
        self.client = Client()
        self.client.force_login(user=self.user)

    def test_view_currenttodo(self):
        res = self.client.get(reverse('currenttodo'))
        self.assertTrue(res.status_code,200)
        self.todo = mommy.make(Todo,completed=datetime.now())
        self.assertTrue(res.context['todos'])

    def test_createtodo(self):
        res = self.client.get(reverse('createtodo'))
        self.assertTrue(res.status_code, 200)
        self.assertIsInstance(res.context['form'], TodoForm)

    def test_viewtodo(self):
        res = self.client.get(reverse('viewtodo',args=[self.todo.id]))
        self.assertTrue(res.status_code,200)
        self.assertTrue(res.context['todo'])
        todo = Todo.objects.get(pk=self.todo.id)
        res =  self.client.get(reverse('viewtodo',args=[todo.id]))
        self.assertTrue(res.status_code,200)
        self.assertIsInstance(res.context['form'], TodoForm)

    def test_complete_todo(self):
        self.todo = mommy.make(Todo, completed=datetime.now())
        res = self.client.get(reverse('completetodo',args=[self.todo.id]))
        self.assertTrue(res.status_code, 200)

    def test_completed_todo(self):
        self.todo = mommy.make(Todo, completed=datetime.now())
        res = self.client.get(reverse('completedtodo'))
        self.assertTrue(res.status_code, 200)
        self.assertFalse(res.context['todos'])

    def test_delete_todo(self):
        self.todo = mommy.make(Todo)
        Todo.objects.filter(id=self.todo.id).delete()




















