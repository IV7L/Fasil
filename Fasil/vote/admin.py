from django.contrib import admin
from .models import VotingToken, PaymentRecord, DebatePackage, DebateVotingTokensRequest, VoteBox
from django import forms

# Register your models here.
# admin.site.register(VotingToken)
admin.site.register(PaymentRecord)
admin.site.register(DebatePackage)

class DebateVotingTokenRequestAdmin(admin.ModelAdmin):
    list_display = ['get_debate_request_title', 'amount', 'price', 'get_full_price', 'status', 'get_debate_request_status']

    def get_debate_request_title(self, obj):
        return obj.debate_request.title
    def get_full_price(self, obj):
        return obj.amount * obj.price
    def get_debate_request_status(self, obj):
        return obj.debate_request.get_request_status_display()
    
admin.site.register(DebateVotingTokensRequest, DebateVotingTokenRequestAdmin)

class DebateVotingTokenAdmin(admin.ModelAdmin):
    list_display = ['hash', 'debate', 'father', 'price', 'used', 'entity']

admin.site.register(VotingToken, DebateVotingTokenAdmin)

class VoteBoxAdmin(admin.ModelAdmin):
    list_display = ['debate', 'debate_goal', 'support_tokens_count', 'opposing_tokens_count', 'box_holder', 'box_status']

    def support_tokens_count(self, obj):
        return obj.support_team_tokens.all().count()
    def opposing_tokens_count(self, obj):
        return obj.opposing_team_tokens.all().count()
    
admin.site.register(VoteBox, VoteBoxAdmin)