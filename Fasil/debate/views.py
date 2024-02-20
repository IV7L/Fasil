from django.shortcuts import render
import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import quote_plus, urlencode

from requests import Session
from general.templatetags.remaining_datetime import remaining_datetime
from account.models import Team

from vote.models import VotingToken, VoteBox
from .models import Debate, Goal, Quote, Timeline
from general.models import Comment, CommentLikes, Thread

from django.db.models import Q
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from account.models import DebateMember, DebateViewer, CustomUser, Sponsor

from django.utils import timezone

def debate(request, debate_id):
    debate = Debate.objects.get(id=debate_id)
    timeline = debate.timeline  # Replace this with how you retrieve the Timeline object

    if timeline:
        current_sub_phase = timeline.calculate_current_sub_phase(debate)
        if current_sub_phase:
            timeline.sub_phase = current_sub_phase
            timeline.save()
            # Calculate the end time for the current sub-phase
            end_time = None
            if current_sub_phase == 'support_quote':
                end_time = debate.timeline.start_time + timeline.support_quote
            elif current_sub_phase == 'opposing_quote':
                end_time = debate.timeline.start_time + timeline.opposing_quote
            elif current_sub_phase == 'rebuttal':
                end_time = debate.timeline.start_time + timeline.rebuttals
            elif current_sub_phase == 'counterargument':
                end_time = debate.timeline.start_time + timeline.counterarguments
            elif current_sub_phase == 'question':
                end_time = debate.timeline.start_time + timeline.questions
            elif current_sub_phase == 'answer':
                end_time = debate.timeline.start_time + timeline.answers
            elif current_sub_phase == 'vote':
                end_time = debate.timeline.start_time + timeline.vote

            # Convert the end_time to a formatted date and time string
            
            end_time_formatted = end_time.strftime("تاريخ: %Y-%m-%d ، الساعة:  %H:%M:%S")

            

    return render(request, 'debate/debate.html', {
        'debate': debate,
        'end_time_formatted': end_time_formatted
        })

def debate_goal(request, debate_id, goal_id):
    debate = Debate.objects.get(id=debate_id)
    goal = Goal.objects.get(id=goal_id)
    quotes = [goal.support_quote, goal.opposing_quote, [goal.rebuttal1_quote, goal.rebuttal2_quote, goal.rebuttal3_quote], [goal.counterargument1_quote, goal.counterargument2_quote,
              goal.counterargument3_quote], [goal.question1_quote, goal.question2_quote, goal.question3_quote], [goal.answer1_quote, goal.answer2_quote, goal.answer3_quote]]
    debateTeamSupport = Team.objects.get(debate=debate, type="support")
    debateTeamOpposing = Team.objects.get(debate=debate, type="opposing")
    # goal voting values || if exist
    goal_voting_values = None
    team1_count = 0
    team2_count = 0
    if goal.status == 'finished':
        tokens = VotingToken.objects.filter(
            goal=goal, used=True, debate=debate)
        for token in tokens:
            if token.selected_team == 'support':
                team1_count += 1
            elif token.selected_team == 'opposing':
                team2_count += 1

        if team1_count > team2_count:
            goal_voting_values = 'support'
        elif team1_count < team2_count:
            goal_voting_values = 'opposing'

    current_user_type = None

    if_debate_member = DebateMember.objects.filter(debate = debate, user=request.user)
    if_debate_viewer = DebateViewer.objects.filter(user=request.user)
    if_debate_sponsor = Sponsor.objects.filter(user=request.user, sponsored_debates__in=[debate])


    if if_debate_member.exists() and if_debate_member.first() in debateTeamSupport.members.all():
        current_user_type = 'support'
    elif if_debate_member.exists() and if_debate_member.first() in debateTeamOpposing.members.all():
        current_user_type = 'opposing'
    elif if_debate_sponsor:
        current_user_type = 'sponsor'
    else:
        current_user_type = 'viewer'

    vote_box = VoteBox.objects.get(debate=debate, debate_goal=goal)

    if debate.timeline.super_phase == 'goal1':
        goal_arrange = 1
    elif debate.timeline.super_phase == 'goal2':
        goal_arrange = 2
    elif debate.timeline.super_phase == 'goal3':
        goal_arrange = 3

    if debate.timeline.sub_phase == 'support_quote':
        support_quote_thread = Thread.objects.get_or_create(type = 'quote', quote_service = debate.goals.get(arrange=goal_arrange).support_quote)
    elif debate.timeline.sub_phase == 'opposing_quote':
        opposing_quote_thread = Thread.objects.get_or_create(type = 'quote', quote_service = debate.goals.get(arrange=goal_arrange).opposing_quote)
    elif debate.timeline.sub_phase == 'rebuttal':
        rebuttal_quote_thread = Thread.objects.get_or_create(type = 'quote', quote_service = debate.goals.get(arrange=goal_arrange).rebuttal1_quote)
    elif debate.timeline.sub_phase == 'counterargument':
        counterargument_quote_thread = Thread.objects.get_or_create(type = 'quote', quote_service = debate.goals.get(arrange=goal_arrange).counterargument1_quote)
    elif debate.timeline.sub_phase == 'question':
        question_quote_thread = Thread.objects.get_or_create(type = 'quote', quote_service = debate.goals.get(arrange=goal_arrange).question1_quote)
    elif debate.timeline.sub_phase == 'answer':
        answer_quote_thread = Thread.objects.get_or_create(type = 'quote', quote_service = debate.goals.get(arrange=goal_arrange).answer1_quote)

    # current_sub_phase_remaining_time [support_quote, opposing_quote, rebuttal, counterargument, question, answer]
    # current_sub_phase_elsaped_time [support_quote, opposing_quote, rebuttal, counterargument, question, answer]

    if debate.timeline:
        current_sub_phase = debate.timeline.calculate_current_sub_phase(debate)
        if current_sub_phase:
            # Calculate the end time for the current sub-phase
            end_time = None
            if current_sub_phase == 'support_quote':
                end_time = debate.timeline.start_time + debate.timeline.support_quote
            elif current_sub_phase == 'opposing_quote':
                end_time = debate.timeline.start_time + debate.debate.timeline.opposing_quote
            elif current_sub_phase == 'rebuttal':
                end_time = debate.timeline.start_time + debate.timeline.rebuttals
            elif current_sub_phase == 'counterargument':
                end_time = debate.timeline.start_time + debate.timeline.counterarguments
            elif current_sub_phase == 'question':
                end_time = debate.timeline.start_time + debate.timeline.questions
            elif current_sub_phase == 'answer':
                end_time = debate.timeline.start_time + debate.timeline.answers
            elif current_sub_phase == 'vote':
                end_time = debate.timeline.start_time + debate.timeline.vote            
            end_time_formatted = end_time.strftime("تاريخ: %Y-%m-%d ، الساعة:  %H:%M:%S")

    current_time = timezone.localtime(timezone.now())
    # print('ended after: ',end_time - current_time) # ended after: 


    return render(request, 'debate/debate_goal.html',
                  {'debate': debate,
                   'goal': goal,
                   'quotes': quotes,
                   'goal_voting_values': goal_voting_values,
                   'team1_count': team1_count,
                   'team2_count': team2_count,
                   'current_user_type': current_user_type,
                   'debate_team_support': debateTeamSupport,
                   'debate_team_opposing': debateTeamOpposing,
                   'debate_member': if_debate_member.first() if if_debate_member.exists() else None,
                   'debate_sponsor': if_debate_sponsor.first() if if_debate_sponsor.exists() else None,
                   'debate_viewer': if_debate_viewer.first() if if_debate_viewer.exists() else None,
                   'vote_box': vote_box,
                   'support_quote_thread': support_quote_thread[0] if debate.timeline.sub_phase == 'support_quote' else None,
                   'opposing_quote_thread': opposing_quote_thread[0] if debate.timeline.sub_phase == 'opposing_quote' else None,
                   'rebuttal_quote_thread': rebuttal_quote_thread[0] if debate.timeline.sub_phase == 'rebuttal' else None,
                   'counterargument_quote_thread': counterargument_quote_thread[0] if debate.timeline.sub_phase == 'counterargument' else None,
                   'question_quote_thread': question_quote_thread[0] if debate.timeline.sub_phase == 'question' else None,
                   'answer_quote_thread': answer_quote_thread[0] if debate.timeline.sub_phase == 'answer' else None,
                   'current_phase_start_from': remaining_datetime(end_time),
                   'current_phase_end_after': end_time - current_time
                })

def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check if the user has already liked the comment
    existing_like = comment.likes.filter(from_account=request.user).first()
    like_status = None

    if existing_like:
        # User has already liked the comment, so remove the like (dislike)
        like_status = 'تأييد'
        existing_like.delete()
    else:
        # User has not liked the comment, create a new like
        like_status = 'عدم تأييد'
        new_like = CommentLikes.objects.create(
            from_account=request.user,
            related_to_comment=comment,
        )
        comment.likes.add(new_like)

    # Return the updated like count in JSON format
    return JsonResponse({'likes_count': comment.likes.count(), 'like_status': like_status})

def team_thought(request, team_id, goal_id):
    current_team = Team.objects.get(id=team_id)
    current_goal = Goal.objects.get(id=goal_id)
    current_debate = Debate.objects.get(goals__in=[current_goal])
    current_user_tokens = VotingToken.objects.filter(debate=current_debate, father=request.user, used=False)

    team_member1 = current_team.members.filter(order=1).first()
    team_member2 = current_team.members.filter(order=2).first()
    team_member3 = current_team.members.filter(order=3).first()

    support_team = Team.objects.get(debate=current_debate, type="support")
    opposing_team = Team.objects.get(debate=current_debate, type="opposing")

    vote_box = VoteBox.objects.get(debate=current_debate, debate_goal=current_goal)

    debate_timeline = current_debate.timeline 
    # vote_phase_duration = debate_timeline.vote

    vote_phase_start_datetime = debate_timeline.start_time + debate_timeline.support_quote + debate_timeline.opposing_quote + debate_timeline.rebuttals + debate_timeline.counterarguments + debate_timeline.questions + debate_timeline.answers
    vote_phase_end_datetime = vote_phase_start_datetime + debate_timeline.vote

    current_datetime = timezone.now()

    vote_phase_remaining_datetime = vote_phase_end_datetime - current_datetime
    vote_phase_remaining_datetime_days = str(vote_phase_remaining_datetime).split(',')[0].split(' ')[0]
    vote_phase_remaining_datetime_hours = str(vote_phase_remaining_datetime).split(',')[1].split('.')[0]

    request.session['debate'] = current_debate.id
    request.session['phase_remaining_time'] = [vote_phase_remaining_datetime_days, vote_phase_remaining_datetime_hours]
    request.session['selected_team'] = current_team.id
    request.session['selected_goal'] = current_goal.id

    return render(request, 'debate/team_thought.html', {
        'team': current_team,
        'goal': current_goal,
        'debate': current_debate, 
        'team_member1': team_member1,
        'team_member2': team_member2,
        'team_member3': team_member3,
        'support_team':support_team,
        'opposing_team':opposing_team,
        'vote_box':vote_box,
        'vote_phase_remaining_datetime':[vote_phase_remaining_datetime_days, vote_phase_remaining_datetime_hours],
        'current_user_tokens':current_user_tokens
    })