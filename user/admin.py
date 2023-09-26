from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user.models import User, Post

admin.site.register(User, UserAdmin)
admin.site.register(Post)
