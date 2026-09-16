from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('role', 'phone')


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'profile__role')

    def get_role(self, obj):
        try:
            return obj.profile.role.upper()
        except:
            return 'NO PROFILE'
    get_role.short_description = 'Role'


# Unregister default User, register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# Profile is shown inline on User — no separate registration needed