from django.contrib import admin
from .models import DebateRequest, SponseeRequest, SupportPackage, ServiceRate, Goal, Thread, Comment
# Register your models here.
admin.site.register(DebateRequest)
admin.site.register(SponseeRequest)
admin.site.register(SupportPackage)

class ServiceRateAdmin(admin.ModelAdmin):
    list_display = ['service', 'rate', 'name', 'email', 'save_for_later', 'comment']

class ThreadAdmin(admin.ModelAdmin):
    list_display = ('type', 'status', 'debate_service', 'quote_service')

class CommentAdmin(admin.ModelAdmin):
    list_display = ['body', 'father', 'likes_count', 'shares_counts']

    def likes_count(self, obj):
        return obj.likes.count()
    
    def shares_counts(self, obj):
        return obj.shares.count()
    

admin.site.register(Comment, CommentAdmin)
admin.site.register(ServiceRate, ServiceRateAdmin)
admin.site.register(Thread, ThreadAdmin)

