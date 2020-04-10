from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new', views.game_new, name='game_new'),
    path('<int:game_id>/actions/', views.actions, name='actions'),
    path('<int:game_id>/demand/random/', views.demand_random, name='random_demand'),
    # path('<int:game_id>/actions/add/mountain/<int:x>/<int:y>', views.action_add_mountain, name='actions'),
    path('<int:game_id>/actions/add/track/<str:color>/<int:x1>/<int:y1>/to/<int:x2>/<int:y2>', views.action_add_track, name='actions_add_track'),
    path('<int:game_id>/actions/move-train/<str:color>/<int:x>/<int:y>', views.action_move_train, name='actions_move_train')
]