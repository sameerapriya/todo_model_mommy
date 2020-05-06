from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from model_mommy import mommy,recipe
from model_mommy.recipe import Recipe, foreign_key
from django.forms import model_to_dict



from todo.models import Todo

SIGNUP_URL = reverse('signupuser')
CURRENT_URL = reverse('currenttodo')

class ModelTests(TestCase):
    """Class for creating tests for todo model"""
    def setUp(self):
        """ Set up all the tests"""
        self.user = mommy.make('User')
        self.user.set_password('password')
        self.user.save()

    def test_model_todo(self):
        """Tests for the model methods"""
        mommy.make('Todo',user=self.user,title=recipe.seq('hello'), _quantity=5)
        todos = Todo.objects.all()
        self.assertEqual(len(todos), 5)
        self.assertIn('hello', todos.__str__())










