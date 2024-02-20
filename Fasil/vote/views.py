from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt  
from django.shortcuts import render
import os 
import stripe
from django.urls import reverse
from django.shortcuts import redirect

from account.models import Team

from debate.models import Debate

def payment_success(request):
    debate = Debate.objects.get(id=request.session['debate'])
    current_goal = debate.goals.get(status="active")

    phase_remaining_time_days = request.session['phase_remaining_time'][0]
    phase_remaining_time_hours = request.session['phase_remaining_time'][1]

    selected_team = request.session['selected_team']
    selected_goal = request.session['selected_goal']

    return render(request, 'vote/checkout_success.html', {
        'debate':debate,
        'goal':current_goal,
        'phase_remaining_time': [phase_remaining_time_days, phase_remaining_time_hours],
        'selected_team': selected_team,
        'selected_goal':selected_goal
    })

def payment_cancel(request):
    return render(request, 'vote/checkout_cancel.html')

@csrf_exempt
def create_checkout_session(request, quantity):
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': 'price_1Nu09jBTv0So7FQo3PHliX7X',
                    'quantity': quantity, # get quantity from request
                },
            ],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('checkout_success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('checkout_cancel')) + '?session_id={CHECKOUT_SESSION_ID}',
        )
    except Exception as e:
        return str(e)
    
    return redirect(checkout_session.url, code=303)

@csrf_exempt
def submit_vote(request, team_id, goal_id):
    # request should be POST
    redirect_url = reverse('team_thought',args=[team_id,goal_id])
    return redirect(redirect_url)