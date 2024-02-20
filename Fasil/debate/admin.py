from django.contrib import admin
from .models import Debate, Goal, Quote, Timeline

# Register your models here.
admin.site.register(Debate)
admin.site.register(Timeline)

class QuoteAdmin(admin.ModelAdmin):
    list_display = ('body', 'goal', 'father_firstlast', 'available', 'status')
    search_fields = ('father', 'body', 'status')

    def father_firstlast(self, obj):
        return obj.father.first_name + ' ' + obj.father.last_name
    def goal(self, obj):
        goal_and_type = obj.get_associated_goal_and_type()
        return f'{goal_and_type[0].body, {goal_and_type[1]}}'
    
class GoalAdmin(admin.ModelAdmin):
    list_display = ('body', 'status', 'arrange', 'debate_assocation')
    
    def debate_assocation(self, obj):
        debate = Debate.objects.get(goals__in=[obj])
        return debate.title
    
admin.site.register(Quote, QuoteAdmin)
admin.site.register(Goal, GoalAdmin)



