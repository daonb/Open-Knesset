'''
API for the accounts app
'''
from django.contrib.auth.models import User
from tastypie.constants import ALL
import tastypie.fields as fields
from avatar.templatetags.avatar_tags import avatar_url

from knesset.api.resources.base import BaseResource

class UserResource(BaseResource):
    class Meta(BaseResource.Meta):
        queryset = User.objects.all()
        include_absolute_url = True
        include_resource_uri = False
        allowed_methods = ['get']
        fields = ['username']

    avatar = fields.CharField()

    def dehydrate_avatar(self, bundle):
        return avatar_url(bundle.obj, 48)
