from django.urls import path
from . import views

urlpatterns = [
    path('<int:debate_id>/', views.debate, name='debate'),
    path('<int:debate_id>/<int:goal_id>/goal/', views.debate_goal, name='debate_goal'),
    path('like-comment/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('team_thought/<int:team_id>/<int:goal_id>/', views.team_thought, name='team_thought'),
]
