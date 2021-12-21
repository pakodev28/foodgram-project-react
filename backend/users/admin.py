from django.contrib import admin

from .models import Follow

class FollowAdmin(admin.ModelAdmin):
    list_dispaly = (
        "pk",
        "user",
        "author",
    )
    list_filter = (
        "user",
        "author",
    )


admin.site.register(Follow, FollowAdmin)
