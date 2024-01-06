
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, FollowerList, FollowingList


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'username', 'email', 'password', 'profile_image', 'last_login')}),
        ('Permissions', {'fields': (
            'is_creator',
            'is_admin',
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        )}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2')
            }
        ),
    )

    list_display = ('email', 'username', 'is_creator', 'last_login')
    list_filter = ('is_creator', 'is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(User, UserAdmin)
admin.site.register(FollowingList)
admin.site.register(FollowerList)

# We can register our models like before
# This was the model we commented in the previous snippet.

#admin.site.register(user_type)