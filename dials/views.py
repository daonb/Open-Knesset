from markdown import markdown
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from models import Dial

GRADE_N_COLOR = ((15, "#ED1C24"), # < 15% red color
                 (60, "#F7AA1E"), # < 60% orange color
                 (100, "#509E33"),# green all the way to 100%
                )
DIAL_WIDTH = 746

def dial_svg(request, slug):
    dial = get_object_or_404(Dial, slug=slug)
    for grade, color in GRADE_N_COLOR:
        if dial.precent < grade:
            break;

    return render_to_response("dials/dial.html",
            {'width': dial.precent * DIAL_WIDTH / 100,
             'precent': dial.precent,
             'color': color,
             'slug': dial.slug,
             },
            context_instance=RequestContext(request))


def dial_desc(request, slug):
    dial = get_object_or_404(Dial, slug=slug)
    return render_to_response("dials/desc.html",
            {'dial': dial,
             'description': markdown(dial.description),
            },
            context_instance=RequestContext(request))

