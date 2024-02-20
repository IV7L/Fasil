# forms.py
from django import forms
from .models import AcademicInterest #، AcademicBackground

class AcademicInterestForm(forms.ModelForm):
    class Meta:
        model = AcademicInterest
        fields = ['interest_type', 'value']

# class AcademicBackgroundForm(forms.ModelForm):
#     class Meta:
#         model = AcademicBackground
#         fields = ['institution_type', 'degree', 'field_or_sector', 'institution']
