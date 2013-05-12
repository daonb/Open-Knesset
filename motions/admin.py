from django.contrib.contenttypes.generic import GenericTabularInline
from django.contrib import admin
from models import Motion
from links.models import Link

class LinksTable(GenericTabularInline):
    model = Link
    ct_field = 'content_type'
    ct_fk_field = 'object_pk'


class MotionAdmin(admin.ModelAdmin):
    ordering = ('-created', )
    inlines = [
        LinksTable,
    ]


admin.site.register(Motion, MotionAdmin)

