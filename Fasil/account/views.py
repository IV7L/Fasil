from django.shortcuts import render
# 📁 webappexample/views.py -----

import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_user
from django.contrib.auth import logout as logout_user
import requests

from .models import DebateViewer, DebateMember, CustomUser, Sponsor
from debate.models import Debate, Quote, Goal
from django.db.models import Q
from django.shortcuts import get_object_or_404


oauth = OAuth()
oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    if token:
        print('this is token !', token)
        user = authenticate(request, token=token)
        print('passed', user)
        if user:
            login_user(request, user)
    return redirect(request.build_absolute_uri(reverse("all_debates")))

def logout(request):
    logout_user(request)
    request.session.clear()

    # Clear Auth0 session
    auth0_logout_url = f"https://{settings.AUTH0_DOMAIN}/v2/logout"
    auth0_params = {
        "returnTo": request.build_absolute_uri(reverse("index")),
        "client_id": settings.AUTH0_CLIENT_ID,
        "federated": "true",  # Clear Auth0 session
    }
    response = requests.get(auth0_logout_url, params=auth0_params)
    
    # Redirect to Auth0 logout
    return redirect(response.url)

def verify_email(request):
    return render(request, "account/verify_email.html")

def profile(request, id):

    user_object = {
        'type': None,
        'data': None,
        'user_facebook': None,
        'user_twitter': None,
        'user_linkedin': None,
        'related_debates': None,
        'related_quote': None,
        'related_quote_debate': None,
        'academic_backgrounds':None
    }
    user = CustomUser.objects.get(id=id)

    if user.current_association == 'member':
        debate_member = get_object_or_404(DebateMember, user_id=id)
        if debate_member:
            user = debate_member
            user_object['type'] = 'member'
            user_object['data'] = user
            social_values = user.social.values_list()

            if len(social_values) > 0:
                user_object['user_facebook'] = social_values[0][1]

            if len(social_values) > 1:
                user_object['user_twitter'] = social_values[1][1]

            if len(social_values) > 2:
                user_object['user_linkedin'] = social_values[2][1]

            user_object['related_debates'] = user.related_debates
            user_object['related_quote'] = user.related_quote
            if user.related_quote:
                quote_instance = get_object_or_404(Quote, id=user.related_quote.id)
                # Assuming you have a Quote instance called 'my_quote'
                associated_goal, quote_type = quote_instance.get_associated_goal_and_type()

                for debate in Debate.objects.all():
                    for goal in debate.goals.all():
                        if goal == associated_goal:
                            user_object['related_quote_debate'] = debate
            user_object['academic_backgrounds'] = user.academic_backgrounds
    elif user.current_association == 'sponsor':
        sponsor = get_object_or_404(Sponsor, user_id=id)
        if sponsor:
            user = sponsor
            user_object['type'] = 'sponsor'
            user_object['data'] = user
            social_values = user.social.values_list()

            if len(social_values) > 0:
                user_object['user_facebook'] = social_values[0][1]

            if len(social_values) > 1:
                user_object['user_twitter'] = social_values[1][1]

            if len(social_values) > 2:
                user_object['user_linkedin'] = social_values[2][1]
            user_object['sponsored_debates'] = user.sponsored_debates
        # continue soposor details sent to profile page here ....
    elif user.current_association == 'viewer':
        debate_viewer = get_object_or_404(DebateViewer, user_id=id)
        if debate_viewer:
            user = debate_viewer
            user_object['type'] = 'viewer'
            user_object['data'] = user
            social_values = user.social.values_list()

            if len(social_values) > 0:
                user_object['user_facebook'] = social_values[0][1]

            if len(social_values) > 1:
                user_object['user_twitter'] = social_values[1][1]

            if len(social_values) > 2:
                user_object['user_linkedin'] = social_values[2][1]
            
            user_object['related_debates'] = user.related_debates
            user_object['related_quote'] = user.related_quote
            if user.related_quote:
                quote_instance = Quote.objects.get(pk=user.related_quote.id)
                # Assuming you have a Quote instance called 'my_quote'
                associated_goal, quote_type = quote_instance.get_associated_goal_and_type()
                for debate in Debate.objects.all():
                    for goal in debate.goals.all():
                        if goal == associated_goal:
                            user_object['related_quote_debate'] = debate
            user_object['academic_interests'] = user.academic_interests
    else:
        user = CustomUser.objects.get(id = id)
        user_object['type'] = 'user'
        user_object['data'] = user

    return render(request, "account/profile.html", {'user_object': user_object})