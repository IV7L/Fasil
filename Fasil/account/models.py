from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from taggit.managers import TaggableManager
from django.db.models.signals import m2m_changed, post_save, pre_save
from django.core.exceptions import ValidationError
from django.dispatch import receiver

from general.models import DebateRequest
from debate.models import Debate
from django.utils import timezone

from django.db.models import Q
from django.core.exceptions import ValidationError
import random



class CustomUser(AbstractUser):
    ACCOUNT_CHOICES = (
        ('member', 'مشارك بالمناقشات'),
        ('viewer', 'مشاهد للمناقشات'),
        ('sponsor', 'راعِ للمناقشات'),
        ('user', 'غير مصنف'),
    )
    email = models.EmailField(max_length=255, unique=True)  # Increase max_length
    email_verified = models.BooleanField(default=False)
    current_association = models.CharField(choices=ACCOUNT_CHOICES, max_length=255, default='user')

    def save(self, *args, **kwargs):
        # Check if first_name or last_name has changed
        if self.first_name or self.last_name:
            try:
                debate_member = self.debatemember
            except DebateMember.DoesNotExist:
                debate_member = None

            # Update the corresponding fields in the associated DebateMember model if values have changed
            if debate_member and (self.first_name != debate_member.first_name or self.last_name != debate_member.last_name):
                debate_member.first_name = self.first_name
                debate_member.last_name = self.last_name
                debate_member.save()

            

    

        # Check if first_name or last_name to fill username field
        if self.first_name or self.last_name and self.username == self.email:
            first_names = CustomUser.objects.filter(first_name = self.first_name)
            if first_names.count() >= 1:
                for first_name in first_names:
                    if first_name.last_name == self.last_name:
                        self.username = self.generate_unique_username(self.first_name + self.last_name)
            else:
                self.username = self.first_name + ' ' + self.last_name

        elif self.first_name == None:
            self.username = self.last_name
        elif self.last_name == None:
            self.username = self.first_name


        # Check if user exist in DebateMember or Sponsor or DebateViewer models to change current_association value
        try:
            member = DebateMember.objects.get(user_id=self.id)
            if member:
                self.current_association = 'member'
        except DebateMember.DoesNotExist:
            try:
                viewer = DebateViewer.objects.get(user_id=self.id)
                if viewer:
                    self.current_association = 'viewer'
            except DebateViewer.DoesNotExist:
                try:
                    sponsor = Sponsor.objects.get(user_id=self.id)
                    if sponsor:
                        self.current_association = 'sponsor'
                except:
                    self.current_association = 'user'

        super().save(*args, **kwargs)

    def generate_unique_username(self, base_username):
            counter = 1
            while True:
                new_username = f"{base_username}{random.randint(1000, 9999)}"
                if not CustomUser.objects.filter(username=new_username).exists():
                    return new_username
                counter += 1


class DebateViewer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateTimeField(auto_created=True, null=True, blank=True)
    previous_vote = models.BooleanField(default=False)
    bio = models.TextField(max_length=500, blank=True, null=True)
    profile_image = models.ImageField(upload_to='media/profile_images', default='/media/profile_images/default/1.png')
    related_debates = models.ManyToManyField('debate.Debate', related_name='viewer_related_debates', blank=True)
    social = TaggableManager(verbose_name = 'Social Accounts', help_text='A comma-separated list of social accounts[Facebook, Twitter, Linkedin].')
    related_quote = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, related_name='viewer_related_quote', blank=True, null=True)
    academic_interests = models.ManyToManyField('account.AcademicInterest', related_name='viewer_academic_interests', blank=True)
    academic_backgrounds = models.ManyToManyField('account.AcademicBackground', related_name='viewer_academic_backgrounds', blank=True)

    def __str__(self):
        return self.user.username
  
class DebateMember(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    debate = models.ForeignKey('debate.Debate', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateField(auto_now_add=True, null=True, blank=True)
    previous_vote = models.BooleanField(default=False)
    bio = models.TextField(max_length=500, blank=True)
    profile_image = models.ImageField(upload_to='media/profile_images', blank=True, null=True)
    related_debates = models.ManyToManyField('debate.Debate', related_name='member_related_debates', blank=True)
    social = TaggableManager(verbose_name = 'Social Accounts', help_text='A comma-separated list of social accounts[Facebook, Twitter, Linkedin].')
    related_quote = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, related_name='member_related_quote', blank=True, null=True)
    academic_interests = models.ManyToManyField('account.AcademicInterest', related_name='member_academic_interests', blank=True)
    academic_backgrounds = models.ManyToManyField('account.AcademicBackground', related_name='member_academic_backgrounds', blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        # Check if first_name or last_name has changed
        if self.first_name or self.last_name:
            # Update the corresponding fields in the associated user model
            self.user.first_name = self.first_name
            self.user.last_name = self.last_name
            self.user.save()

        # Check if the member already has an order, or if the order is 0 or greater than 3
        if not self.order or self.order == 0 or self.order > 3:
            # Get the team to which the member belongs
            team = Team.objects.get(debate=self.debate, members__in = [self])
            # If the team exists, get the members with orders
            if team:
                print('so here ?')
                ordered_members = team.members.exclude(order__isnull=True).exclude(order=0).exclude(order__gt=3).order_by('order')
                print(ordered_members)
                # If all three members don't have an order, assign based on user date joined
                if not ordered_members.exists():
                    self.order = ordered_members.count() + 1
                # If two members don't have an order, assign based on user date joined after order 1
                elif ordered_members.count() == 1:
                    self.order = ordered_members.first().order + 1
                # If only one member, give it order 3
                elif ordered_members.count() == 2:
                    self.order = 3

        # Check if the member has been associated with any debate to change related_debates value
        teams = Team.objects.filter(members__in = [self])
        if teams:
            if len(teams) > 1:
                for team in teams:
                    self.related_debates.add(team.debate)
            else:
                self.related_debates.add(teams[0].debate)

        # Call the save method of the parent class
        super().save(*args, **kwargs)
    
class Team(models.Model):
    debate = models.ForeignKey('debate.Debate', on_delete=models.CASCADE, null=True, blank=True)
    members = models.ManyToManyField('account.DebateMember', related_name='team_members', blank=True)
    type = models.CharField(max_length=10, choices=(('support', 'Support'), ('opposing', 'Opposing')))

    def __str__(self) -> str:
        return super().__str__()
    
class Sponsor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='sponsor_logos/', blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    social = TaggableManager()
    sponsored_debates = models.ManyToManyField('debate.Debate', related_name='sponsor_sponsored_debates', blank=True)

    def __str__(self) -> str:
        return self.name

class AcademicInterest(models.Model):
    INTEREST_TYPES = [
        ('book', 'كتاب'),
        ('author', 'كاتب'),
        ('experience', 'خبرة'),
        ('other1', 'خيار ١'),
        ('other2', 'خيار ٢'),
        ('other3', 'خيار ٣'),
        # Add more types as needed
    ]

    interest_type = models.CharField(max_length=20, choices=INTEREST_TYPES)
    value = models.CharField(max_length=255)
    generated_image = models.ImageField(upload_to='media/debates_image', blank=True, null=True)
    date = models.DateField(default=timezone.now())
    url = models.URLField()

    def __str__(self):
        return f"{self.interest_type}: {self.value}"

class AcademicBackground(models.Model):
    INSTITUTION_TYPES = [
        ('school', 'المدرسة'),
        ('college', 'الكلية'),
        ('university', 'الجامعة'),
        ('other', 'غير ذلك'),
    ]

    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPES)
    degree = models.CharField(max_length=255)
    field_or_sector = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    date = models.DateField(default=timezone.now())
    generated_image = models.ImageField(upload_to='media/debates_image', blank=True, null=True)
    url = models.URLField()

    def __str__(self):
        return f"{self.institution_type}: {self.degree} in {self.field_or_sector} at {self.institution}"

@receiver(post_save, sender=CustomUser)
def teamManagmentSignal(sender, instance, created, **kwargs):
    if created:
        for i in DebateRequest.objects.all():
            for x in i.team1_members_emails:
                if x == instance.email:
                    for debate in Debate.objects.all():
                        if debate.debate_request == i:
                            if debate.timeline.start_time > timezone.now():
                                # this means that this user is associated with debate that it doesnt started
                                member = DebateMember.objects.create(
                                    user = instance,
                                    debate = debate
                                )
                                member.save()
                                # create or connect with team
                                if Team.objects.filter(debate=debate, type="support").exists():
                                    team = Team.objects.get(debate=debate, type="support")
                                    if team.members.count() == 1:
                                        member.order = 2
                                        member.save()
                                    elif team.members.count() == 2:
                                        member.order = 3
                                        member.save()
                                    team.members.add(member)
                                    team.save()
                                    internal_created = True
                                    # notify sponsor and other members
                                else:
                                    print('starting ....')
                                    team = Team.objects.create(
                                        debate = debate,
                                        type = 'support'
                                    )
                                    team.save()
                                    member.order = 1
                                    member.save()
                                    team.members.add(member)
                                    team.save()
                                    internal_created = True
                                    # notify sponsor
                            else:
                                # this means that this user is associated with debate that it already started !!!
                                pass
            for v in i.team2_members_emails:
                if v == instance.email:
                    for debate in Debate.objects.all():
                        if debate.debate_request == i:
                            if debate.timeline.start_time > timezone.now():
                                # this means that this user is associated with debate that it doesnt started
                                member = DebateMember.objects.create(
                                    user = instance,
                                    debate = debate
                                )
                                member.save()
                                # create or connect with team
                                if Team.objects.filter(debate=debate, type="opposing").exists():
                                    team = Team.objects.get(debate=debate, type="opposing")
                                    if team.members.count() == 1:
                                        member.order = 2
                                        member.save()
                                    elif team.members.count() == 2:
                                        member.order = 3
                                        member.save()
                                    team.members.add(member)
                                    team.save()
                                    internal_created = True
                                    # notify sponsor and other members
                                else:
                                    print('starting ....')
                                    team = Team.objects.create(
                                        debate = debate,
                                        type = 'opposing'
                                    )
                                    team.save()
                                    member.order = 1
                                    member.save()
                                    team.members.add(member)
                                    team.save()
                                    internal_created = True
                                    # notify sponsor
                            else:
                                # this means that this user is associated with debate that it already started !!!
                                pass

            if i.customer_email == instance.email:
                # this means that this mail related to a sponsor account !!!
                internal_created = True

        matching_requests = DebateRequest.objects.filter(
            Q(team1_members_emails__contains=[instance.email]) | Q(team2_members_emails__contains=[instance.email])
        )
        if matching_requests.exists():
            print('this means that the current user has passed the above code !!!')
            pass
        else:
            print(f"The email '{instance.email}' is found in some DebateRequests.")
            viewer = DebateViewer.objects.create(
                user = instance,
            )
            viewer.save()            

@receiver(pre_save, sender=DebateViewer)
def checkForViewerAccount(sender, instance, *args, **kwargs):
    # Check if any DebateViewer object already exists for the given user
    existing_viewer = DebateViewer.objects.filter(user=instance.user).exclude(pk=instance.pk).first()
    existing_member = DebateMember.objects.filter(user=instance.user).exclude(pk=instance.pk).first()
    existing_sponsor = Sponsor.objects.filter(user=instance.user).exclude(pk=instance.pk).first()

@receiver(m2m_changed, sender=Team.members.through)
def limit_team_members(sender, instance, action, reverse, model, pk_set, **kwargs):
    if instance.members.count() + len(pk_set) > 3:
        raise ValidationError("A team can only have 3 members.")