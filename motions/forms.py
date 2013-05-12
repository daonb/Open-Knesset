from django import forms
from django.forms.models import modelformset_factory

from models import Motion
from links.models import Link

class EditMotionForm(forms.ModelForm):
    class Meta:
        model = Motion
        fields = ('title','description')

# TODO: move to links app
LinksFormset = modelformset_factory(Link,
                                    can_delete=True,
                                    fields=('url', 'title'),
                                    extra=3)


