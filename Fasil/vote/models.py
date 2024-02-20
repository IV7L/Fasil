from collections.abc import Iterable
from django.db import models
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver

# Create your models here.

class VotingToken(models.Model):
    hash = models.CharField(max_length=100)
    debate = models.ForeignKey('debate.Debate', on_delete=models.CASCADE)
    father = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    price = models.IntegerField(default=20)
    used = models.BooleanField(default=False)
    entity = models.CharField(choices=(('paid', 'Paid'), ('invited', 'Invited')), max_length=255)
    invited_by = models.ForeignKey(
        'account.Sponsor', 
        on_delete=models.CASCADE, 
        related_name='invited_by', 
        blank=True, 
        null=True,
    )

    # 2- every token related to a debate
    # if debate request created: 
        # tokens request
    # if new debate request == 'accepted':
        # generate new tokens

    def __str__(self) -> str:
        return f" {self.hash}: {self.entity}"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.entity == 'paid':
            # If entity is 'paid', set invited_by to None
            self.invited_by = None
            # You can also make the field non-editable
            self._meta.get_field('invited_by').editable = False

class DebateVotingTokensRequest(models.Model):
    VOTING_TOKENS_REQUEST_CHOICES = (
        ('waiting', 'انتظار'),
        ('accepted', 'موافق'),
        ('rejected', 'مرفوض'),
    )
    debate_request = models.ForeignKey('general.DebateRequest', on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)
    price = models.IntegerField(default=20)
    status = models.CharField(choices=VOTING_TOKENS_REQUEST_CHOICES, max_length=255)

    def __str__(self) -> str:
        return f"{self.debate_request.title} توكين, حالة الطلب: {self.get_status_display()}"

class PaymentRecord(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('other', 'Other'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'معلق'),
        ('completed', 'انتهى'),
        ('failed', 'فشل'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    invoice_reference = models.CharField(max_length=50, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.amount} ({self.payment_status})"

class DebatePackage(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    price = models.IntegerField(default=0)
    token_amount = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    contract_ownership = models.BooleanField(default=False)
    contract_controlled = models.BooleanField(default=False)
    pay_for_all_tokens = models.BooleanField(default=False)
    similarity_percentage = models.IntegerField(default=0)
    po_neg_percentage = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.title
    
class VoteBox(models.Model):
    BOXSTATUSCHOICES = (
        ('on-hold','معلق'),
        ('available','متاح'),
        ('not-available','غير متاح')
    )
    debate = models.ForeignKey('debate.Debate', on_delete=models.CASCADE)
    debate_goal = models.ForeignKey('debate.Goal', on_delete=models.CASCADE)
    support_team_tokens = models.ManyToManyField('vote.VotingToken', related_name='support_team_tokens', null=True, blank=True)
    opposing_team_tokens = models.ManyToManyField('vote.VotingToken', related_name='opposing_team_tokens', null=True, blank=True)
    best_quotes = models.ManyToManyField('debate.Quote', null=True, blank=True)
    box_holder = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE)
    box_status = models.CharField(choices=BOXSTATUSCHOICES, max_length=255)

    def __str__(self) -> str:
        return super().__str__()
    
    def save(self) -> None:
        # check if token exist in other team tokens
        if self.debate_goal not in self.debate.goals.all():
            raise ValidationError('Sorry, Selected goal is not realted to this token debate.')                        

        return super().save()

@receiver(m2m_changed, sender=VoteBox.support_team_tokens.through)
def check_for_support_tokens(sender, instance, **kwargs):
    if instance.support_team_tokens.count() > 0:
        for token in instance.support_team_tokens.all():
            # check if token exist in other team tokens
            if token in instance.opposing_team_tokens.all():
                raise ValidationError('Sorry, Current Token is been set to the other team in debate.')
            # check if token related to debate and check used field
            if token.debate != instance.debate:
                raise ValidationError('Sorry, Current Token not related to this debate.')
            elif token.debate == instance.debate:
                if token.used:
                    raise ValidationError('Sorry, Current Token is been used before.')
        
@receiver(m2m_changed, sender=VoteBox.opposing_team_tokens.through)
def check_for_opposing_tokens(sender, instance, **kwargs):
    if instance.opposing_team_tokens.count() > 0:
        for token in instance.opposing_team_tokens.all():
            # check if token exist in other team tokens
            if token in instance.support_team_tokens.all():
                raise ValidationError('Sorry, Current Token is been set to the other team in debate.')
            # check if token related to debate and check used field
            if token.debate != instance.debate:
                raise ValidationError('Sorry, Current Token not related to this debate.')
            elif token.debate == instance.debate:
                if token.used:
                    raise ValidationError('Sorry, Current Token is been used before.')


# after MVP version should be two main classes, Proposal Argument and DAO Argument
# Proposal Argument should hold debate data from Fasil and relation to BC contract
# DAO Argument should hold the default settings to apply after creating debate
## Current voting system is not based on DAO, but it should be after MVP version
### voting system: current version is generating voting token and relation to debate
