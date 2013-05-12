from committees.views import MeetingListView, CommitteeDetailView
from committees.models import Committee, CommitteeMeeting

class PlenumView(CommitteeDetailView):    
    
    def get_object(self, *args, **kwargs):
        return Committee.objects.get(type='plenum')
    
class PlenumMeetingListView(MeetingListView):
    
    def get_queryset (self):
        c_id = Committee.objects.get(type='plenum').id
        if c_id:
            return CommitteeMeeting.objects.filter(committee__id=c_id)
        else:
            return CommitteeMeeting.objects.all()
        
    def get_context(self):
        context = super(PlenumMeetingListView, self).get_context()
        context['committee_type'] = 'plenum'
        return context
