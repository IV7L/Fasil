from django.contrib import admin
from .models import DebateViewer, DebateMember, Team, Sponsor, CustomUser, AcademicInterest, AcademicBackground
# Register your models here.

admin.site.register(AcademicInterest)

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'current_association', 'first_name', 'last_name', 'email_verified')
    search_fields = ('username', 'email', 'first_name', 'last_name')

admin.site.register(CustomUser, CustomUserAdmin)

class DebateMemberAdmin(admin.ModelAdmin):
    list_display = ('user_username', 'debate_title', 'first_name', 'last_name', 'previous_vote', 'order')
    search_fields = ('user_username', 'debate_title', 'first_name', 'last_name', 'order')

    def user_username(self, obj):
        return obj.user.username
    def debate_title(self, obj):
        return obj.debate.title

admin.site.register(DebateMember, DebateMemberAdmin)

class DebateViewerAdmin(admin.ModelAdmin):
    list_display = ('user_username', 'first_name', 'last_name','previous_vote')

    def user_username(self, obj):
        return obj.user.username

admin.site.register(DebateViewer, DebateViewerAdmin) 

class TeamAdmin(admin.ModelAdmin):
    list_display = ('debate', 'members_all', 'type')
    search_fields = ('debate', 'members', 'type')

    def members_all(self, obj):
        return ', '.join(member.user.username for member in obj.members.all())

admin.site.register(Team, TeamAdmin)

class AcademicBackgroundAdmin(admin.ModelAdmin):
    list_display = ('institution_type', 'degree', 'field_or_sector', 'institution', 'date')

admin.site.register(AcademicBackground, AcademicBackgroundAdmin)

class SponsorAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'description', 'website', 'get_sponsored_debates']

    def get_sponsored_debates(self, obj):
        title_list = []
        for debate in obj.sponsored_debates.all():
            title_list.append(debate.title)
        return title_list

admin.site.register(Sponsor, SponsorAdmin)