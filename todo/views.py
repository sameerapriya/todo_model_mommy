from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .forms import TodoForm
from .models import Todo


def home(request):
    return render(request, 'todo/home.html')


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(), 'error': "Invalid Credentials"})
        else:
            login(request, user)
            return redirect('currenttodo')


def signupuser(request):
    if request.method == 'GET':
        return render(request,'todo/signupuser.html',{'form':UserCreationForm()})
    else:
        try:
            if request.POST['password1'] == request.POST['password2']:
                user = User.objects.create_user(request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect('currenttodo')
        except IntegrityError:
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(),'error':'The following username has been taken. Please enter another Username'})

        else:
            return render(request,'todo/signupuser.html',{'form':UserCreationForm(),'error':'Passwords do not match'})


@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request,'todo/createtodo.html',{'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodo')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form': TodoForm(),'error':'Bad Data passed in.Try again'})


@login_required
def currenttodo(request):
    todos = Todo.objects.filter(user=request.user,completed__isnull=True)
    return render(request,'todo/currenttodo.html',{'todos':todos})


@login_required
def viewtodo(request,todo_pk):
    todo = get_object_or_404(Todo,pk=todo_pk,user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST,instance=todo)
            form.save()
            return redirect('currenttodo')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form, 'error': 'Bad Info Provided'})


@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.completed = timezone.now()
        todo.save()
        return redirect('currenttodo')


@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodo')


@login_required
def completedtodo(request):
    todos = Todo.objects.filter(user=request.user,completed__isnull=False).order_by('-completed')
    return render(request, 'todo/completedtodo.html', {'todos': todos})
