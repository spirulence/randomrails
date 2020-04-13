from django.urls import path

from . import views

urlpatterns = [
    path('new', views.game_new, name='game_new'),
    path('<int:game_id>/join/<str:joincode>', views.game_join, name='game_new'),

    path('<int:game_id>/slots', views.slots_view_all, name='game_slots_view_all'),
    path('<int:game_id>/slots/joincodes', views.slots_view_joincodes, name='game_slots_view_joincodes'),
    path('<int:game_id>/slot/mine/', views.slot_view_mine, name='game_slot_view_mine'),
    path('<int:game_id>/slot/<int:player_number>/set-color/<str:color>', views.slot_set_color,
         name='game_slot_set_color'),

    path('<int:game_id>/actions', views.actions, name='actions'),
    path('<int:game_id>/actions/last', views.action_last, name='actions_last'),
    path('<int:game_id>/actions/demand/draw', views.action_demand_draw, name='action_draw_demand'),
    path('<int:game_id>/actions/adjust-money/player/<int:player>/add/<int:add_amount>', views.action_adjust_money,
         name='action_add_money'),
    path('<int:game_id>/actions/add/track/<int:x1>/<int:y1>/to/<int:x2>/<int:y2>', views.action_add_track,
         name='action_add_track'),
    path('<int:game_id>/actions/move-train/<int:x>/<int:y>', views.action_move_train,
         name='action_move_train'),
    path('<int:game_id>/actions/good/pickup/<str:good_id>', views.action_good_pickup,
         name='action_pickup_good'),
    path('<int:game_id>/actions/good/deliver/<str:good_id>/card/<int:card_id>', views.action_good_deliver,
         name='action_deliver_good'),
    path('<int:game_id>/actions/good/dump/<str:good_id>', views.action_good_dump,
         name='action_dump_good')
]
