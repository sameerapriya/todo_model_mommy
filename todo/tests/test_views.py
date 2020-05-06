from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import datetime
from django.test import Client
from django.urls import reverse
import random,string
from model_mommy import mommy,recipe
from ..views import *
from ..forms import TodoForm

SIGNUP_URL = reverse('signupuser')
LOGIN_URL = reverse('loginuser')


class ViewTodos(TestCase):

    def setUp(self):
        self.client = Client()

    def test_page_load_correctly(self):
        res = self.client.get(SIGNUP_URL)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'todo/signupuser.html')

    def test_signup_user(self):
        data = {
            'username': 'hello',
            'password1': 'blahblah123',
            'password2': 'blahblah123'
        }
        res = self.client.post(SIGNUP_URL,data)
        self.assertEqual(res.status_code,302)
        self.assertRedirects(res,reverse('currenttodo'))

    def test_signup_password_not_equal(self):
        data = {
            'username': 'hello',
            'password1': 'blah',
            'password2': 'blah1'
        }
        res = self.client.post(SIGNUP_URL, data)
        self.assertTrue(res.context['error'])

    def test_signup_username_taken(self):
        user1 = mommy.make('User',username='hello1',password='hello1223')
        user1.save()
        user2_data = {
            'username': 'hello1',
            'password1': 'blah',
            'password2': 'blah'
        }
        res = self.client.post(SIGNUP_URL, user2_data)
        self.assertTrue(res.context['error'],'The following username has been taken. Please enter another Username')

    def test_login_successful_page_load(self):
        res = self.client.get(LOGIN_URL)
        self.assertEqual(res.status_code,200)
        self.assertTemplateUsed(res, 'todo/loginuser.html')

    def test_login_POST(self):
        user = get_user_model().objects.create_user(username='hello',password='hello123')
        user.save()
        self.client.force_login(user)
        data = {
            'username':'hello',
            'password':'hello123'
        }
        res = self.client.post(LOGIN_URL,data)
        self.assertEqual(res.status_code,302)
        self.assertRedirects(res,reverse('currenttodo'))

    def test_login_with_invalid_credentials(self):
        data = {
            'username': 'hello',
            'password': 'hello123'
        }
        res = self.client.post(LOGIN_URL, data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['error'],"Invalid Credentials")


CREATE_TODO_URL = reverse('createtodo')
CURRENT_TODO_URL = reverse('currenttodo')


class PrivateViewTests(TestCase):

    def setUp(self):
        self.user = mommy.make('User',username='hello',password='password12233')
        self.client = Client()
        self.client.force_login(self.user)

    def test_logout(self):
        res = self.client.post(reverse('logoutuser'),user=self.user)
        self.assertEqual(res.status_code,302)
        self.assertRedirects(res,reverse('home'))

    def test_create_todo_get(self):
        res = self.client.get(CREATE_TODO_URL)
        self.assertEqual(res.status_code,200)
        self.assertTemplateUsed(res,'todo/createtodo.html')
        self.assertTrue(res.context['form'])

    def test_create_todo_post(self):
        data ={
            'title': 'Get Money',
            'memo': '2200'
        }
        res = self.client.post(CREATE_TODO_URL,data)
        self.assertEqual(res.status_code,302)

    def test_create_todo_bad_data(self):
        data = {
            'title':''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(400)) ,
            'memo': '2200'
        }
        res = self.client.post(CREATE_TODO_URL, data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['error'],'Bad Data passed in.Try again')

    def test_current_todo(self):
        mommy.make('Todo',user=self.user,title=recipe.seq('hello'),_quantity=5)
        mommy.make('Todo', user=self.user,title=recipe.seq('helloii'), _quantity=5,completed=datetime(2019,5,5))
        res = self.client.get(CURRENT_TODO_URL)
        self.assertEqual(res.status_code,200)
        self.assertEqual(len(res.context['todos']), 5)
        self.assertTemplateUsed(res,'todo/currenttodo.html')

    def test_view_todo_get(self):
        mommy.make('Todo', user=self.user, title=recipe.seq('hello'), _quantity=5)
        view_url = reverse('viewtodo',args=[1])
        res = self.client.get(view_url)
        self.assertEqual(res.status_code, 200)
        self.assertIn('hello',res.context['todo'].title)
        view_url = reverse('viewtodo', args=[6])
        res = self.client.get(view_url)
        self.assertEqual(res.status_code, 404)

    def test_view_todo_post(self):
        mommy.make('Todo', user=self.user, title=recipe.seq('hello'), _quantity=3)
        data={
            'title':'helloblah',
            'important':True
        }
        view_url = reverse('viewtodo', args=[1])
        res = self.client.post(view_url,data)
        self.assertEqual(res.status_code, 302)

    def test_view_todo_post_baddata(self):
        mommy.make('Todo', user=self.user, title=recipe.seq('hello'), _quantity=3)
        data = {
            'title': ''.join(random.SystemRandom().choice(string.ascii_letters) for _ in range(400)),
            'important': True
        }
        view_url = reverse('viewtodo', args=[1])
        res = self.client.post(view_url, data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['error'],'Bad Info Provided')

    def test_complete_todo_post(self):
        mommy.make('Todo', user=self.user, title=recipe.seq('hello'), _quantity=3)
        url = reverse('completetodo',args=[2])
        data = {
            'completed':datetime(2020,4,2)
        }
        res = self.client.post(url,data)
        self.assertEqual(res.status_code,302)

    def test_complete_todo_invalid_pk(self):
        mommy.make('Todo', user=self.user, title=recipe.seq('hello'), _quantity=3)
        url = reverse('completetodo', args=[66])
        data = {
            'completed': datetime(2020, 4, 2)
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 404)

    def test_delete_todo(self):
        mommy.make('Todo', user=self.user, title=recipe.seq('hello'), _quantity=3)
        url = reverse('deletetodo', args=[3])
        data={}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 302)

    def test_delete_todo_invalid(self):
        mommy.make('Todo', user=self.user, title=recipe.seq('hello'), _quantity=3)
        url = reverse('deletetodo', args=[99])
        data = {}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 404)

    def test_completed_todo(self):
        mommy.make('Todo', user=self.user, title=recipe.seq('hello'), _quantity=3)
        mommy.make('Todo', user=self.user, title=recipe.seq('hello112'), _quantity=5,completed=datetime(2020,5,4))
        url = reverse('completedtodo')
        res = self.client.get(url)
        self.assertEqual(res.status_code,200)
        self.assertEqual(len(res.context['todos']),5)
