from typing import Any
from django.db import models
from taggit.managers import TaggableManager
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import m2m_changed, post_save, pre_save, post_init
from django.core.validators import MaxValueValidator, MinValueValidator

from django.db.models.signals import m2m_changed
from django.dispatch import receiver

def default_start_time():
        return timezone.now() + timedelta(days=10)

class Debate(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'قيد انتظار'),
        ('active', 'نشطه'),
        ('finished', 'انتهت'),
        ('canceled', 'تم الالغاء'),
        ('archieved', 'ارشيف')
    ]
    father = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    generated_image = models.ImageField(upload_to='media/debates_image', blank=True, null=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='waiting')
    goals = models.ManyToManyField('Goal')
    timeline = models.ForeignKey('Timeline', on_delete=models.CASCADE, blank=True, null=True)
    sponsors = models.ManyToManyField('account.Sponsor', blank=True)
    debate_request = models.ForeignKey('general.DebateRequest', on_delete=models.CASCADE, blank=True, null=True)

    # debate settings
    winning_team_percentage = models.IntegerField(validators=[MaxValueValidator(100),MinValueValidator(0)], null=True, blank=True, verbose_name="Debate settings: Winning Team Percentage")
    donation_percentage = models.IntegerField(validators=[MaxValueValidator(100),MinValueValidator(0)], null=True, blank=True, verbose_name="Debate settings: Donation Percentage")
    donation_entity_data = TaggableManager(help_text='Name, Details, Website | Seprated using comma', blank=True, verbose_name="Debate settings: Donation Entity Data")

    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs):
        # 1- if both have values but sum is not equal to 100
        if self.winning_team_percentage + self.donation_percentage < 100:
            if self.winning_team_percentage > self.donation_percentage:
                the_more = 100 - (self.winning_team_percentage + self.donation_percentage)
                self.donation_percentage = self.donation_percentage + the_more
            elif self.donation_percentage > self.winning_team_percentage:
                the_more = 100 - (self.donation_percentage + self.winning_team_percentage)
                self.winning_team_percentage = self.winning_team_percentage + the_more

        # 2- if one of them is None, fill the other with the remaining to 100
        if self.winning_team_percentage == None:
            self.winning_team_percentage = 100 - self.donation_percentage
        elif self.donation_percentage == None:
            self.donation_percentage = 100 - self.winning_team_percentage

        super().save(*args, **kwargs)
    
class Goal(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'انتظار'),
        ('active', 'فعال'),
        ('finished', 'انتهت'),
        ('rejected', 'مرفوض'),
    ]
    body = models.TextField(max_length=500)
    arrange = models.IntegerField(default=0, validators=[MaxValueValidator(3), MinValueValidator(1)])
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='waiting')
    support_quote = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, related_name='support_quote', blank=True, null=True)
    opposing_quote = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, related_name='opposing_quote', blank=True, null=True)
    rebuttal1_quote = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, related_name='rebuttal1_quote', blank=True, null=True)
    rebuttal2_quote = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, related_name='rebuttal2_quote', blank=True, null=True)
    rebuttal3_quote = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, related_name='rebuttal3_quote', blank=True, null=True)
    counterargument1_quote = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, related_name='counterargument1_quote', blank=True, null=True)
    counterargument2_quote = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, related_name='counterargument2_quote', blank=True, null=True)
    counterargument3_quote = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, related_name='counterargument3_quote', blank=True, null=True)
    question1_quote = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, related_name='question1_quote', blank=True, null=True)
    question2_quote = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, related_name='question2_quote', blank=True, null=True)
    question3_quote = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, related_name='question3_quote', blank=True, null=True)
    answer1_quote = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, related_name='answer1_quote', blank=True, null=True)   
    answer2_quote = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, related_name='answer2_quote', blank=True, null=True)
    answer3_quote = models.ForeignKey('debate.Quote', on_delete=models.CASCADE, related_name='answer3_quote', blank=True, null=True)

    def __str__(self) -> str:
        return self.body
    
class Quote(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'انتظار'),
        ('active', 'فعال'),
        ('finished', 'انتهت'),
        ('rejected', 'مرفوض'),
    ]
    body = models.TextField(max_length=500)
    father = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    generated_image = models.ImageField(upload_to='media/quotes_image', blank=True, null=True)
    available = models.BooleanField(default=True) # for debate_member
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='waiting')
    comments = models.ManyToManyField('general.Comment', blank=True)
    tags = TaggableManager()

    def __str__(self) -> str:
        return self.body
    
    def get_associated_goal_and_type(self):
        goal_fields = [field for field in Goal._meta.get_fields() if field.is_relation and isinstance(field, models.ForeignKey)]

        for field in goal_fields:
            field_name = field.name
            try:
                goal = Goal.objects.get(**{field_name: self})
                print(f"{field_name}: {goal}")
                return goal, field_name
            except Goal.DoesNotExist:
                continue

        return None, None

class Timeline(models.Model):
    SUPER_CHOICES = [
        ('goal1', 'الهدف الاول'),
        ('goal2', 'الهدف الثاني'),
        ('goal3', 'الهدف الثالث'),
    ]
    SUB_CHOICES = [
        ('support_quote', 'اقتباس الدعم'),
        ('opposing_quote', 'اقتباس التعارض'),
        ('rebuttal', 'اقتباسات الحجج'),
        ('counterargument', 'اقتباسات رد الحجج'),
        ('question', 'الاسئلة'),
        ('answer', 'الاجابات'),
        ('vote', 'التصويت'),
    ]
    
    
    start_time = models.DateTimeField(null=True, blank=True, default=default_start_time)
    end_time = models.DateTimeField(null=True, blank=True, default=default_start_time)

    support_quote = models.DurationField(null=True, blank=True)
    opposing_quote = models.DurationField(null=True, blank=True)
    rebuttals = models.DurationField(null=True, blank=True)
    counterarguments = models.DurationField(null=True, blank=True)
    questions = models.DurationField(null=True, blank=True)
    answers = models.DurationField(null=True, blank=True)
    vote = models.DurationField(null=True, blank=True)

    super_phase = models.CharField(max_length=100, choices=SUPER_CHOICES, default='goal1')
    sub_phase = models.CharField(max_length=100, choices=SUB_CHOICES, default='support_quote')

    def save(self, *args, **kwargs):
        # Calculate the total time interval
        total_time = (self.end_time - self.start_time)

        # Define the time allocation percentages
        allocation_percentages = {
            "support_quote": 0.10,
            "opposing_quote": 0.10,
            "rebuttals": 0.10,
            "counterarguments": 0.10,
            "questions": 0.10,
            "answers": 0.10,
            "vote": 0.40,
        }

        # Calculate and set the durations based on percentages
        for field_name, percentage in allocation_percentages.items():
            duration_seconds = total_time.total_seconds() * percentage
            duration_timedelta = timedelta(seconds=duration_seconds)
            setattr(self, field_name, duration_timedelta)

        super(Timeline, self).save(*args, **kwargs)


    def calculate_current_sub_phase(self, debate=None):
        current_time = timezone.localtime(timezone.now())  # Convert current time to local timezone

        # Convert start_time to local timezone
        start_time_local = timezone.localtime(self.start_time)
        end_time_local = timezone.localtime(self.end_time)

        if debate and debate.goals.all() and end_time_local > current_time > start_time_local:
            elapsed_time = current_time - start_time_local
            self.super_phase = "goal1"
            self.save()

            # activate everything related to goal1 status:
            goal1 = Goal.objects.get(id = debate.goals.get(arrange=1).id)
            goal1.status = 'active'
            goal1.save()


        if debate and debate.goals.all() and debate.goals.get(arrange=1).status == "finished":
            # If the first goal is finished and debate object is provided, adjust the start time
            goal1_duration = (end_time_local - start_time_local) // 3
            elapsed_time = (current_time - start_time_local) + goal1_duration
            self.super_phase = "goal2"
            self.save()

            # activate everything related to goal1 status:
            goal2 = Goal.objects.get(id = debate.goals.get(arrange=2).id)
            goal2.status = 'active'
            goal2.save()

        elif debate and debate.goals.all() and debate.goals.get(arrange=2).status == "finished":
            # If the first goal is finished and debate object is provided, adjust the start time
            goal1_duration = (end_time_local - start_time_local) // 3
            goal2_duration = (end_time_local - start_time_local) // 3
            elapsed_time = (current_time - start_time_local) + goal1_duration + goal2_duration
            self.super_phase = "goal3"
            self.save()

            # activate everything related to goal1 status:
            goal3 = Goal.objects.get(id = debate.goals.get(arrange=3).id)
            goal3.status = 'active'
            goal3.save()
        else:
            # here what
            pass

        if elapsed_time < self.support_quote:
            return "support_quote"
        elif elapsed_time < self.support_quote + self.opposing_quote:
            return "opposing_quote"
        elif elapsed_time < self.support_quote + self.opposing_quote + self.rebuttals:
            return "rebuttal"
        elif elapsed_time < self.support_quote + self.opposing_quote + self.rebuttals + self.counterarguments:
            return "counterargument"
        elif elapsed_time < self.support_quote + self.opposing_quote + self.rebuttals + self.counterarguments + self.questions:
            return "question"
        elif elapsed_time < self.support_quote + self.opposing_quote + self.rebuttals + self.counterarguments + self.questions + self.answers:
            return "answer"
        elif elapsed_time < self.support_quote + self.opposing_quote + self.rebuttals + self.counterarguments + self.questions + self.answers + self.vote:
            return "vote"
    
        # If none of the conditions match, return None or a default value
        return None

    def __str__(self) -> str:
        return self.super_phase + ' ' + self.sub_phase
    