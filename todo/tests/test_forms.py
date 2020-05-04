from django.test import TestCase
from model_mommy import mommy

from ..forms import TodoForm


class FormTest(TestCase):

    def setUp(self):
        self.todo = mommy.make('Todo')

    def test_todoform(self):
        data = {
            'title':self.todo.title, 'memo':self.todo.memo, 'important':self.todo.important
        }
        form = TodoForm(data=data)
        self.assertTrue(form.is_valid())

