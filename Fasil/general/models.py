from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import post_save
from django.dispatch import receiver
from debate.models import Debate, Timeline, Goal
from .utils import generate_image_based_on_data
from account.utils import send_custom_email
from vote.utils import create_voting_tokens
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator

from django.conf import settings

class DebateRequest(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'انتظار'),
        ('accepted', 'موافق'),
        ('rejected', 'مرفوض'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal1 = models.CharField(max_length=200)
    goal2 = models.CharField(max_length=200)
    goal3 = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    customer_email = models.CharField(max_length=200, default='')
    customer_name = models.CharField(max_length=200, default='')
    team1_members_emails = ArrayField(models.EmailField(), blank=True, null=True)
    team2_members_emails = ArrayField(models.EmailField(), blank=True, null=True)
    package = models.ForeignKey('vote.DebatePackage', on_delete=models.CASCADE)
    request_status = models.CharField(max_length=200, choices=STATUS_CHOICES, default='waiting')

    def __str__(self):
        return self.title + ' | ' + self.request_status

class SponseeRequest(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'انتظار'),
        ('accepted', 'موافق'),
        ('rejected', 'مرفوض'),
    ]
    debate = models.ForeignKey('debate.Debate', on_delete=models.CASCADE)
    sponsor_name = models.CharField(max_length=200)
    sponsor_email = models.CharField(max_length=200)
    request_status = models.CharField(max_length=200, choices=STATUS_CHOICES, default='waiting')

    def __str__(self):
        return self.sponsor_name + ' | ' + self.request_status

@receiver(post_save, sender=DebateRequest)
def teamManagment_post_save_receiver(sender, instance, **kwargs):
    try:
        # Try to get the previous status from the database
        previous_instance = sender.objects.get(pk=instance.pk)
        previous_status = previous_instance.request_status
    except ObjectDoesNotExist:
        # If the object is new, set the previous status to None
        previous_status = None

    if previous_status != 'accepted' and instance.request_status == 'accepted':
        Sponsor = apps.get_model('account', 'Sponsor')
        User = apps.get_model('account', 'CustomUser')
        # create timeline object
        timeline = Timeline.objects.create()
        timeline.save()
        # create user account
        print('here ...............')
        user = User.objects.create(
            username=instance.customer_name,
            email=instance.customer_email,
            password='123456',
        )
        user.save()
        # create sponsor account
        sponsor = Sponsor.objects.create(
            user = user,
            name = instance.customer_name
        )
        sponsor.save()
        # create goal objects
        goal1 = Goal.objects.create(
            body = instance.goal1,
        )
        goal1.save()
        goal2 = Goal.objects.create(
            body = instance.goal2
        )
        goal2.save()
        goal3 = Goal.objects.create(
            body = instance.goal3
        )
        goal3.save()
        # generate image of the debate
        generated_image = generate_image_based_on_data(
            instance.title,
            [instance.goal1, instance.goal2, instance.goal3]
        )
        # create debate object
        debate = Debate.objects.create(
            father = user,
            title = instance.title,
            description = instance.description,
            generated_image = generated_image['image'],
            status = 'waiting',
            timeline = timeline,
        )
        debate.save()
        debate.goals.set([goal1, goal2, goal3])
        debate.sponsors.add(sponsor)
        debate.save()
        # generate token for the debate
        create_voting_tokens(instance.package.token_amount, user)
        # assign debate to sponsor
        sponsor.sponsored_debates.add(debate)
        sponsor.save()
        # send mail notifications
        # send mail to the sponsor
        # send_custom_email(
        #     'Debate Request Accepted',
        #     'utils/mail/notify_sponsor.html',
        #     [sponsor.user.email]
        # )
        # # send mail to the members in team1
        # send_custom_email(
        #     'Debate Request Accepted',
        #     'utils/mail/notify_member.html',
        #     [instance.team1_members_emails]
        #     )
        # # send mail to the members in team2
        # send_custom_email(
        #     'Debate Request Accepted',
        #     'utils/mail/notify_member.html',
        #     [instance.team2_members_emails]
        #     )
        

class SupportPackage(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField(default=200)
    image = models.ImageField()
    # rate = models.IntegerChoices([1,2])
    sepcification1 = models.CharField(max_length=255)
    sepcification2 = models.CharField(max_length=255)
    sepcification3 = models.CharField(max_length=255)
    sepcification4 = models.CharField(max_length=255)
    sepcification5 = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.title
    
class ServiceRate(models.Model):
    service = models.ForeignKey(SupportPackage, on_delete=models.CASCADE)
    rate = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    comment = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    save_for_later = models.BooleanField(default=False)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return super().__str__()
    
class Thread(models.Model):
    THREADTYPECHOICES = (
        ('debate', 'لوح نقاش خاص بمناظرة'),
        ('quote', 'لوح نقاش خاص باقتباس'),
    )
    THREADSTATUSCHOICES = (
        ('open', 'متاح'),
        ('closed', 'غير متاح'),
    )
    type = models.CharField(max_length=255, choices=THREADTYPECHOICES)
    comments = models.ManyToManyField('general.Comment', blank=True)
    status = models.CharField(max_length=255, choices=THREADSTATUSCHOICES)
    debate_service = models.ForeignKey('debate.Debate', on_delete=models.CASCADE, blank=True, null=True, unique=True)
    quote_service = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, blank=True, null=True, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.type == 'debate':
            # You can also make the field non-editable
            self._meta.get_field('quote_service').editable = False
            self._meta.get_field('debate_service').editable = True
            self.quote_service = None
        elif self.type == 'quote':
            self._meta.get_field('quote_service').editable = True
            self._meta.get_field('debate_service').editable = False
            self.debate_service = None
        else:
            self._meta.get_field('quote_service').editable = True
            self._meta.get_field('debate_service').editable = True

    def __str__(self) -> str:
        return self.get_type_display()

class Comment(models.Model):
    body = models.TextField(max_length=500)
    father = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    likes = models.ManyToManyField('general.CommentLikes', blank=True)
    shares = models.ManyToManyField('general.CommentShares', blank=True, related_name='comment_external_shares')
    media = models.FileField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.body
    
class CommentLikes(models.Model):
    from_account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='like_from_account')
    related_to_comment = models.ForeignKey(Comment, on_delete= models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return super().__str__()
    
class CommentShares(models.Model):
    PLATFORM_CHOICES = (
        ('facebook', 'فيسبوك'),
        ('X', 'تويتر | اكس'),
        ('linkedin', 'لينكد ان'),
        ('threads', 'ثريدس'),
    )
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    platform = models.CharField(choices=PLATFORM_CHOICES, max_length=255)

    def __str__(self) -> str:
        return super().__str__()

    