# Create your views here.
from django.views.generic import DetailView, ListView
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseRedirect, Http404,
                         HttpResponseForbidden)
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from auxiliary.views import GetMoreView, BaseTagMemberListView
from .models import Motion
from .forms import EditMotionForm, LinksFormset
from links.models import Link

class MotionsMoreView(GetMoreView):
    """Get partially rendered motions content for AJAX calls to 'More'"""

    paginate_by = 20
    template_name = 'motions/_motions_summary.html'

    def get_queryset(self):
        return Motion.objects.summary()


class MotionListView(ListView):
    model = Motion
    context_object_name = 'motions'
    queryset = Motion.objects.get_public()

class MotionDetailView(DetailView):
    model = Motion
    context_object_name = 'motion'

    def get_context_data(self, **kwargs):
        context = super(MotionDetailView, self).get_context_data(**kwargs)
        motion = context['motion']
        if self.request.user.is_authenticated():
            p = self.request.user.get_profile()
            watched = motion in p.motions
        else:
            watched = False
        context['watched_object'] = watched
        return context

@login_required
@csrf_protect
def edit_motion(request, pk=None):
    if request.method == 'POST':
        if pk:
            motion = Motion.objects.get(pk=pk)
            if not motion.can_edit(request.user):
                return HttpResponseForbidden()
        else:
            # adding a new motion
            motion = None
        edit_form = EditMotionForm(data=request.POST, instance=motion)
        links_formset = LinksFormset(request.POST)
        if edit_form.is_valid() and links_formset.is_valid():
            motion = edit_form.save(commit=False)
            if pk:
                motion.id = pk
            else: # new motion
                motion.creator = request.user
            motion.save()
            edit_form.save_m2m()
            links = links_formset.save(commit=False)
            ct = ContentType.objects.get_for_model(motion)
            for link in links:
                link.content_type = ct
                link.object_pk = motion.id
                link.save()

            messages.add_message(request, messages.INFO, 'Motion has been updated')
            return HttpResponseRedirect(
                reverse('motion-detail',args=[motion.id]))

    if request.method == 'GET':
        if pk: # editing existing motion
            motion = Motion.objects.get(pk=pk)
            if not motion.can_edit(request.user):
                return HttpResponseForbidden()
            edit_form = EditMotionForm(instance=motion)
            ct = ContentType.objects.get_for_model(motion)
            links_formset = LinksFormset(queryset=Link.objects.filter(
                content_type=ct, object_pk=motion.id))
        else:
            edit_form = EditMotionForm()
            links_formset = LinksFormset(queryset=Link.objects.none())
    return render_to_response('motions/edit_motion.html',
        context_instance=RequestContext(request,
            {'edit_form': edit_form,
             'links_formset': links_formset,
            }))

@login_required
@csrf_protect
def delete_motion(request, pk):
    motion = get_object_or_404(Motion, pk=pk)
    if motion.can_edit(request.user):
        # Delete on POST
        if request.method == 'POST':
            motion.status = models.MOTION_DELETED
            motion.save()
            return HttpResponseRedirect(reverse('motion-list'))

        # Render a form on GET
        else:
            return render_to_response('motions/delete_motion.html',
                {'motion': motion},
                RequestContext(request)
            )
    else:
        raise Http404

def delete_motion_rating(request, object_id):
    if request.method=='POST':
        motion= get_object_or_404(Motion, pk=object_id)
        motion.rating.delete(request.user, request.META['REMOTE_ADDR'])
        return HttpResponse('Vote deleted.')
