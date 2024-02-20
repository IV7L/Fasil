from django import template
from account.models import DebateMember, DebateViewer, Sponsor
register = template.Library()

@register.filter(name='current_user_profile_image')
def get_associated_account_profile_image(value):
    if value.current_association == 'member':
        current_user_profile_image = DebateMember.objects.get(user = value).profile_image.url
    elif value.current_association == 'viewer':
        current_user_profile_image = DebateViewer.objects.get(user = value).profile_image.url
    elif value.current_association == 'sponsor':
        current_user_profile_image = Sponsor.objects.get(user = value).logo.url
    else:
        current_user_profile_image = '/media/default/2.png'
    
    return current_user_profile_image
