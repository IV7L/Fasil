from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_debate/', views.create_debate, name='create_debate'),
    path('debate_checkout_success/', views.debate_checkout_success, name='debate_checkout_success'),
    path('sponsee_debate/<int:debate_id>/', views.sponsee_debate, name='sponsee_debate'),
    path('member_cart/<int:debate_id>/<int:selected_team>', views.member_cart, name='member_cart'),
    path('support_us/<int:package_id>/', views.support_us, name='support_us'),

    path('all_debates_thread/', views.all_debates_thread, name='all_debates_thread'),
    path('thread/<int:thread_id>/', views.thread, name='thread')
]
