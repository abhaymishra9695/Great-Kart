from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
# Register your models here.
class AcountAdmin(UserAdmin):
    list_display=('email','first_name','last_name','username','lats_login','date_join','is_active')
    list_display_links=('email','first_name','last_name')
    readonly_fields=('lats_login','date_join')
    ordering=('-date_join',)
    filter_horizontal=()
    list_filter=()
    fieldsets=()
admin.site.register(Account,AcountAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="30" style="border-radius: 50%;">'.format(object.profile_picture.url))
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail','user', 'city','state', 'country')

admin.site.register(UserProfile,UserProfileAdmin)
