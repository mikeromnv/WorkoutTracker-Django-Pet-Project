from django.urls import path

from workouts.views import *

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path('', home_view, name='home'),
    path('logout/', logout_view, name='logout'),
    path('workout/', workout_list, name='workout_list'),
    path('workouts/create/', workout_create, name='workout_create'),
    path('workouts/<int:workout_id>/', workout_detail, name='workout_detail'),
    path('workout/<int:workout_id>/delete/', workout_delete, name='workout_delete'),
    path('workout_exercise/<int:workout_exercise_id>/delete/', workout_exercise_delete, name='workout_exercise_delete'),
    path('workout_set/<int:workout_set_id>/delete/', workout_set_delete, name='workout_set_delete'),
    path('history/', history, name='history')

]
