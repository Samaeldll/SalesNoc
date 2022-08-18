from django.contrib import admin

from front.models import Contract, CommentRow, FrontUser

admin.site.register(Contract)

admin.site.register(CommentRow)
admin.site.register(FrontUser)