from django.conf import settings  # new
import os
from django.urls import reverse  # new
import stripe  # new
from django.views.decorators.csrf import csrf_exempt  # new
from django.http import JsonResponse  # new
from django.shortcuts import redirect, render
from debate.models import Debate
from vote.models import VotingToken, DebatePackage
from django.shortcuts import render
from django.http import HttpResponse
from general.models import DebateRequest

from vote.utils import create_voting_tokens

from account.models import Team

from general.models import SupportPackage, ServiceRate, Thread
from account.models import CustomUser, DebateViewer, DebateMember, Sponsor

def index(request):
    if request.user.is_authenticated:
        debates = Debate.objects.filter(status='active')
        return render(request, 'debate/all_debates.html', {
            'user': request.user,
            'debates': debates,
        })
    else:
        return render(request, 'general/index.html')

@csrf_exempt
def create_debate(request):
    if request.method == "POST":
        # Access the values sent with the POST request
        debate_title = request.POST.get('debate_title')
        debate_description = request.POST.get('debate_description')
        debate_goal_1 = request.POST.get('debate_goal_1')
        debate_goal_2 = request.POST.get('debate_goal_2')
        debate_goal_3 = request.POST.get('debate_goal_3')
        debate_team_1_member_1 = request.POST.get('debate_team_1_member_1')
        debate_team_1_member_2 = request.POST.get('debate_team_1_member_2')
        debate_team_1_member_3 = request.POST.get('debate_team_1_member_3')
        debate_team_2_member_1 = request.POST.get('debate_team_2_member_1')
        debate_team_2_member_2 = request.POST.get('debate_team_2_member_2')
        debate_team_2_member_3 = request.POST.get('debate_team_2_member_3')

        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price': 'price_1NxoSNBTv0So7FQo0iSWquvZ',
                        'quantity': 1, # get quantity from request
                    },
                ],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('debate_checkout_success')) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri(reverse('checkout_cancel')) + '?session_id={CHECKOUT_SESSION_ID}',
                metadata={
                    'debate_title': debate_title,
                    'debate_description': debate_description,
                    'debate_goal_1': debate_goal_1,
                    'debate_goal_2': debate_goal_2,
                    'debate_goal_3': debate_goal_3,
                    'debate_team_1_member_1': debate_team_1_member_1,
                    'debate_team_1_member_2': debate_team_1_member_2,
                    'debate_team_1_member_3': debate_team_1_member_3,
                    'debate_team_2_member_1': debate_team_2_member_1,
                    'debate_team_2_member_2': debate_team_2_member_2,
                    'debate_team_2_member_3': debate_team_2_member_3,
                }
            )
        except Exception as e:
            return str(e)
        
        data = {
            'checkout_url': checkout_session.url,
        }
        return JsonResponse(data)
    else: 
        return render(request, 'general/create_debate.html')

@csrf_exempt
def debate_checkout_success(request):
    # Get the session ID from the query parameters
    session_id = request.GET.get('session_id')

    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

    try:
        # Retrieve the Checkout session from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        customer_email = checkout_session['customer_details']['email']
        customer_name = checkout_session['customer_details']['name']

        
        # Extract information from the Checkout session
        debate_title = checkout_session.metadata.get('debate_title', '')
        debate_description = checkout_session.metadata.get('debate_description', '')
        debate_goal_1 = checkout_session.metadata.get('debate_goal_1', '')
        debate_goal_2 = checkout_session.metadata.get('debate_goal_2', '')
        debate_goal_3 = checkout_session.metadata.get('debate_goal_3', '')
        debate_team_1_member_1 = checkout_session.metadata.get('debate_team_1_member_1', '')
        debate_team_1_member_2 = checkout_session.metadata.get('debate_team_1_member_2', '')
        debate_team_1_member_3 = checkout_session.metadata.get('debate_team_1_member_3', '')
        debate_team_2_member_1 = checkout_session.metadata.get('debate_team_2_member_1', '')
        debate_team_2_member_2 = checkout_session.metadata.get('debate_team_2_member_2', '')
        debate_team_2_member_3 = checkout_session.metadata.get('debate_team_2_member_3', '')
        
        # Create a DebateRequest object with the extracted data
        debate_request = DebateRequest.objects.create(
            title = debate_title,
            description = debate_description,
            goal1 = debate_goal_1,
            goal2 = debate_goal_2,
            goal3 = debate_goal_3,
            customer_email = customer_email,
            customer_name = customer_name,
            team1_members_emails = [debate_team_1_member_1, debate_team_1_member_2, debate_team_1_member_3],
            team2_members_emails = [debate_team_2_member_1, debate_team_2_member_2, debate_team_2_member_3],
        )
        debate_request.save()

        # You can also perform any additional actions here, such as sending emails or notifications
        data = {
            'message': 'Payment successful!',
            'order_id': '123456',
            'request_number': debate_request.id,
            'request_status':debate_request.request_status,
            'customer_email': customer_email,
            'customer_name': customer_name,
            # Add other data as needed
        }
        return render(request, 'vote/checkout_success.html', context=data)  # Render a success page
    except Exception as e:
        # Handle any errors that may occur
        return HttpResponse(f"Error: {str(e)}", status=500)
    
def sponsee_debate(request, debate_id):
    debate = Debate.objects.get(id = debate_id)
    current_debate_team_support = list(Team.objects.get(debate=debate, type='support').members.all())
    current_debate_team_opposing = list(Team.objects.get(debate=debate, type='opposing').members.all())

    return render(request, 'general/sponsee_debate.html', {'debate': debate, 'current_debate_team_support': current_debate_team_support, 'current_debate_team_opposing': current_debate_team_opposing})

def member_cart(request, debate_id, selected_team):
    debate = Debate.objects.get(id=debate_id)
    debate_request = DebateRequest.objects.get(debate=debate)
    debate_package = debate_request.package

    # the purpose here is to give the customer(debate viewer):
    # 1- the ability to have tokens to vote
    # ** the ability: two ways to have tokens in Fasil:
    # 1- buy tokens
    # 2- transfer tokens
    # *** buy tokens: 
    # 1- the customer being father of the token
    # 2- the token shouldn't have a father before
    # 3- the token shouldn't be paid:true
    # 4- the token shouldn't be user:true
    # 5- the token should have entity value of: paid

    ## before requesting this page:
    ### if customer have a token related to this debate:
    ### 1- notify that he have a token can be used for this voting process!
    free_tokens = []
    tokens = VotingToken.objects.filter(debate=debate, father=None, used=False)
    # if tokens: that means that there's a free tokens for this debate and can be paid following the current process
    # if not: checking if the current voting tokens related to this debate are less than the token request amount of tokens
    # if yes: generate a new token for this user
    # if no: this process couldn't be completed due to the lack of tokens 
    if tokens.count() == 0:
        # get the count of tokens related to this debate
        # get the amount of tokens for this debate request
        count_of_current_debate_tokens = VotingToken.objects.filter(debate=debate).count()
        amount_of_current_debate_request_tokens = debate_package.token_amount
        if count_of_current_debate_tokens < amount_of_current_debate_request_tokens:
            current_debate_request_price_for_token = debate_package.price
            # generate a new token with father=null
            new_generated_token = create_voting_tokens(1, None, debate, current_debate_request_price_for_token)
            free_tokens.append(new_generated_token)
        else:
            raise ValueError('No available tokens for this debate !!')
            # raise an error that should be raised before !
    else:
        for token in tokens:
            free_tokens.append(token)

    return render(request, 'general/member_cart.html', {
        'debate': debate, 
        'token': free_tokens[0], 
        'selected_team': selected_team,
        'debate_package': debate_package    
    })

def support_us(request, package_id):
    current_package = SupportPackage.objects.get(id= package_id)
    current_package_rates = ServiceRate.objects.filter(service=current_package)
    support_packages = SupportPackage.objects.all()

    return render(request, 'general/support_us.html', {
        'packages':support_packages,
        'current_package': current_package,
        'current_package_rates': current_package_rates
    })

def all_debates_thread(request):
    debates = Debate.objects.filter(status='active')
    user = CustomUser.objects.get(id=request.user.id)
    if user.current_association == 'member' or user.current_association == 'viewer':
        related_quote = DebateViewer.objects.get(user=request.user).related_quote
        goal, type = related_quote.get_associated_goal_and_type()
        quote_debate = Debate.objects.get(goals__in = [goal])
        related_quote.debate = quote_debate
    elif user.current_association == 'sponsor':
        pass
 
    debate_threads = Thread.objects.filter(status='open', type='debate')
    quote_threads = Thread.objects.filter(status='open', type='quote')    

    return render(
        request,
        'debate/all_debates_threads.html',
        context={
            "session": request.session.get("user"),
            'debates': debates, 
            'quote': related_quote,
            #
            'threads':debate_threads,
            'main_debate':debate_threads[0],
        })

def thread(request, thread_id):
    thread = Thread.objects.get(id= thread_id)
    common_threads = Thread.objects.filter(type = thread.type, status='open').order_by('date').exclude(id=thread.id)[:3]
    common_members = []
    base_members = thread.comments.order_by('date').exclude(father_id = request.user.id)[:3]
    for i in base_members:
        if i.father.current_association == 'viewer':
            if DebateViewer.objects.get(user = i.father) not in common_members:
                common_members.append(DebateViewer.objects.get(user = i.father))
        elif i.father.current_association == 'member':
            if DebateMember.objects.get(user = i.father) not in common_members:
                common_members.append(DebateMember.objects.get(user = i.father))
        elif i.father.current_association == 'sponsor':
            if Sponsor.objects.get(user = i.father) not in common_members:
                common_members.append(Sponsor.objects.get(user = i.father))

    return render(request, 'general/thread.html', {
        'thread': thread,
        'common_threads': common_threads,
        'common_members': common_members
    })