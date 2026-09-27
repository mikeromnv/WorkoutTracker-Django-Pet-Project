from urllib.parse import uses_query

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from workouts.forms import RegisterForm
from workouts.models import Workout, Exercise, WorkoutExercise, MuscleGroup, Set


def home_view(request):
    if request.user.is_authenticated:
        user = request.user

        workouts_count = Workout.objects.filter(user=user).count()
        exercises_count = WorkoutExercise.objects.filter(workout__user=user).count()
        sets_count = Set.objects.filter(workout_exercise__workout__user=user).count()

        last_workout = Workout.objects.filter(
            user=user
        ).order_by('-date').first()

        last_workout_date = last_workout.date if last_workout else None

        fav_exercises = WorkoutExercise.objects.filter(workout__user=user).values(
            'exercise', 'exercise__name'
        ).annotate(
            count = Count('exercise')
        ).order_by('-count')

        for fe in fav_exercises:
            print(fe)
        fav_exercise = fav_exercises.first()
        set_fav_exercise = 0
        if fav_exercise:
            set_fav_exercise = Set.objects.filter(
                workout_exercise__workout__user=user,
                workout_exercise__exercise=fav_exercise['exercise']
            ).count()

        context = {
            'workouts_count': workouts_count,
            'exercises_count': exercises_count,
            'sets_count': sets_count,
            'last_workout_date': last_workout_date,
            'fav_exercise': fav_exercise,
            'set_fav_exercise': set_fav_exercise
        }
        return render(request, 'workouts/home.html', context)

    return redirect('login')

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )

            login(request, user)

            return redirect('home')
    else:
        form = RegisterForm()

    return render(
        request,
        'workouts/register.html',
        {'form': form}
    )

def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user=authenticate(
            request,
            username=username,
            password=password
        )
        if user is not None:
            login(request, user)
            return redirect('home')
        error = "Неверный логин или пароль"
    return render(
        request,
        'workouts/login.html',
        {'error': error}
    )

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def workout_list(request):
    workouts = Workout.objects.filter(
        user=request.user
    ).order_by('-id')

    return render(request, 'workouts/workout_list.html', {'workouts': workouts})

@login_required(login_url='login')
def workout_create(request):
    if request.method == "POST":
        name = request.POST['name']
        date = request.POST.get('date')

        if name=='':
            counts = len(Workout.objects.filter(user=request.user))
            name = f'Тренировка №{counts}'

        Workout.objects.create(
            name=name,
            date=date,
            user=request.user
        )

        return redirect('workout_list')

    return render(request, 'workouts/workout_create.html')

@login_required(login_url='login')
def workout_detail(request, workout_id):
    workout = get_object_or_404(
        Workout,
        id=workout_id,
        user=request.user
    )
    if request.method == "POST":

        if 'exercise' in request.POST:

            exercise_id = request.POST['exercise']
            print(f'************************* {exercise_id} *************************')
            if exercise_id:
                exercise = get_object_or_404(
                    Exercise,
                    id=exercise_id,
                )

                WorkoutExercise.objects.create(
                    workout=workout,
                    exercise=exercise,
                )

        if 'workout_exercise_id' in request.POST:
            workout_exercise_id = request.POST.get('workout_exercise_id')
            weight = request.POST.get('weight')
            repetitions = request.POST.get('repetitions')
            distance = request.POST.get('distance')

            if workout_exercise_id:
                workout_exercise = get_object_or_404(
                    WorkoutExercise,
                    id=workout_exercise_id,
                    workout=workout
                )

                if (weight and repetitions) or distance:
                    Set.objects.create(
                        workout_exercise=workout_exercise,
                        weight=weight or None,
                        repetitions=repetitions or None,
                        distance=distance or None
                    )

        return redirect(
            'workout_detail',
            workout_id=workout.id
        )

    muscle_group = MuscleGroup.objects.all().order_by('name')

    exercises = Exercise.objects.all().order_by('name')

    workout_exercises = workout.workoutexercise_set.select_related(
        'exercise',
        'exercise__muscle_group'
    )
    return render(
        request,
        'workouts/workout_detail.html',
        {'workout': workout, 'exercises': exercises, 'workout_exercises': workout_exercises, 'muscle_group': muscle_group}
    )

@login_required(login_url='login')
def workout_delete(request, workout_id):
    workout = get_object_or_404(
        Workout,
        id = workout_id,
        user = request.user
    )

    if request.method == 'POST':
        workout.delete()
        return redirect('workout_list')

    return redirect('workout_detail', workout_id=workout.id)

@login_required(login_url='login')
def workout_exercise_delete(request, workout_exercise_id):
    workout_exercise = get_object_or_404(
        WorkoutExercise,
        id=workout_exercise_id,
        workout__user=request.user
    )
    workout_id = workout_exercise.workout_id
    if request.method == 'POST':
        workout_exercise.delete()

    return redirect('workout_detail', workout_id=workout_id)

@login_required(login_url='login')
def workout_set_delete(request, workout_set_id):
    workout_set = get_object_or_404(
        Set,
        id=workout_set_id,
        workout_exercise__workout__user=request.user
    )
    workout_id = workout_set.workout_exercise.workout_id
    if request.method == 'POST':
        workout_set.delete()

    return redirect('workout_detail', workout_id=workout_id)


@login_required(login_url='login')
def history(request):
    user = request.user

    user_sets = Set.objects.filter(
        workout_exercise__workout__user=user
    ).order_by('-workout_exercise__workout__date', 'workout_exercise__exercise__name')

    return render(request, 'workouts/history.html', {'user_sets': user_sets})