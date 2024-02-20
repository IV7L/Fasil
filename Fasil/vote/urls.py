from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<int:quantity>', views.create_checkout_session, name='checkout'),
    path('checkout_success/', views.payment_success, name='checkout_success'),
    path('checkout_cancel/', views.payment_cancel, name='checkout_cancel'),

    path('submit_vote/<int:team_id>/<int:goal_id>/', views.submit_vote, name='submit_vote')
]
