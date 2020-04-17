from django.urls import path

from . import views

urlpatterns = [
    path('new/', views.game_new, name='game_new'),
    path('<int:game_id>/join/<str:color>/<str:screen_name>/', views.game_join, name='game_join'),

    path('<int:game_id>/my-player-id/', views.game_my_player_id, name="game_my_player_id"),
    path('<int:game_id>/my-membership/', views.game_my_membership, name="game_my_membership"),
    path('<int:game_id>/lobby/colors-available/', views.game_lobby_colors_available, name="game_lobby_colors_available"),

    path('<int:game_id>/actions/', views.actions, name='actions'),
    path('<int:game_id>/actions/after/<int:sequence_number>/', views.actions_after, name='actions_after'),
    path('<int:game_id>/actions/demand/draw/', views.action_demand_draw, name='action_draw_demand'),
    path('<int:game_id>/actions/adjust-money/player/<int:player_id>/<str:sign>/<int:amount>/', views.action_adjust_money,
         name='action_add_money'),
    path('<int:game_id>/actions/add/track/<int:x1>/<int:y1>/to/<int:x2>/<int:y2>/', views.action_add_track,
         name='action_add_track'),
    path('<int:game_id>/actions/erase/track/<int:x1>/<int:y1>/to/<int:x2>/<int:y2>/', views.action_erase_track,
         name='action_erase_track'),
    path('<int:game_id>/actions/move-train/<int:x>/<int:y>/', views.action_move_train,
         name='action_move_train'),
    path('<int:game_id>/actions/good/pickup/<str:good_id>/', views.action_good_pickup,
         name='action_pickup_good'),
    path('<int:game_id>/actions/good/deliver/<str:good_id>/card/<int:card_id>/', views.action_good_deliver,
         name='action_deliver_good'),
    path('<int:game_id>/actions/good/dump/<str:good_id>/', views.action_good_dump,
         name='action_dump_good'),
    path('<int:game_id>/actions/flow/start/', views.start_game, name='action_start_game'),
    path('<int:game_id>/actions/flow/advance/turn/', views.start_game, name='action_start_game'),

    path('<int:game_id>/map/render/', views.map_render),

    path('<int:game_id>/invite/use/<str:invite_code>/', views.invite_use, name='invite_use'),
    path('<int:game_id>/invite/create/', views.invite_create, name='invite_create'),
]
