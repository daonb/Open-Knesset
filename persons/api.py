from itertools import chain
from apis.resources.base import BaseResource
from models import Role, Person
from tastypie.constants import ALL, ALL_WITH_RELATIONS
import tastypie.fields as fields
from django.contrib.auth.models import User
from links.models import Link
from links.api import LinkResource

class RoleResource(BaseResource):
    ''' Role API
    '''
    class Meta(BaseResource.Meta):
        queryset = Role.objects.all()
        allowed_methods = ['get']
        excludes = ["id"]
        include_resource_uri = False
        filtering = {
                'org': ALL,
                'text': ALL,
                }

class PersonResource(BaseResource):

    roles = fields.ToManyField(RoleResource, 'roles', full=True)
    mk = fields.ToOneField('mks.api.MemberResource', 'mk', null=True, full=True)
    links = fields.ToManyField(LinkResource,
                    attribute = lambda b: Link.objects.for_model(b.obj),
                    full = True,
                    null = True)

    class Meta(BaseResource.Meta):
        queryset = Person.objects.all()
        allowed_methods = ['get']
        filtering = {
                'roles': ALL_WITH_RELATIONS,
                }

    def get_object_list(self, request):
        persons = super(PersonResource, self).get_object_list(request)
        user_id = request.GET.get('user_id', '')
        if len(user_id) > 0:
            persons = persons.filter(user__id=user_id)
        return persons
