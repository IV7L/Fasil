from django.forms import ModelForm
from .models import DebateRequest, SponseeRequest


class DebateRequestForm(ModelForm):
    class Meta:
        model = DebateRequest
        fields = ['title', 'description', 'goal1',
                  'goal2', 'goal3', 'start_date', 'end_date']


class SponseeRequestForm(ModelForm):
    class Meta:
        model = SponseeRequest
        fields = ['debate', 'sponsor_name', 'sponsor_email']
