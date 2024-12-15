from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed, JsonResponse
from django.utils.translation import gettext as _

from home.models import Notification, Level


# Create your views here.
@login_required
def get_messages(request):
    if request.method == 'GET':
        notifications = Notification.objects.filter(user=request.user)
        notes = [{"level": _(n.level), 'text': _(n.text), 'created': n.created_at} for n in notifications]
        for note in notifications:
            note.delete()
        return JsonResponse(data=notes, status=200, safe=False)
    else:
        return HttpResponseNotAllowed(permitted_methods=["GET"])