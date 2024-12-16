import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed, JsonResponse

from dashboard.models import Dashboard, DashboardSlot



# Create your views here.
@login_required
def get_dashboard_slots(request, dashboard_id: int):
    if request.method == 'GET':
        dashboard = Dashboard.objects.get(id=dashboard_id, user=request.user)
        dashboard_slots = DashboardSlot.objects.filter(dashboard=dashboard)
        slots = [
            {"id": slot.id,
             "width": slot.width,
             "height": slot.height,
             "row_num": slot.row_num,
             "col_num": slot.col_num,
             "chart_id": slot.chart_id
            } for slot in dashboard_slots]
        return JsonResponse(slots, safe=False, status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=["GET"])


@login_required
def get_dashboards(request):
    if request.method == 'GET':
        dashboards = Dashboard.objects.filter(user=request.user)
        return JsonResponse([{'id': dashboard.id, 'title': dashboard.title}  for dashboard in dashboards], safe=False, status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=["GET"])


@login_required
def create_dashboard(request):
    if request.method == 'POST':
        title = request.POST.get('title',None)

        if not title:
            return JsonResponse({'error':'title is required'}, safe=False)

        dashboard = Dashboard(title=title, user=request.user)
        dashboard.save()
        return JsonResponse({'id': dashboard.id, 'title': dashboard.title}, safe=False)
    else:
        return HttpResponseNotAllowed(permitted_methods=["POST"])

@login_required()
def update_dashboard_slots(request):
    if request.method == 'POST':
        slots = json.loads(request.body).get('slots', [])
        for slot in slots:
            new_col_num = slot.get('x', 0)
            new_row_num = slot.get('y', 0)
            new_width = slot.get('w', 0)
            new_height = slot.get('h', 0)
            slot_id = slot.get('slot_id')

            dashboard_slot = DashboardSlot.objects.get(id=slot_id)
            dashboard_slot.col_num = new_col_num
            dashboard_slot.row_num = new_row_num
            dashboard_slot.width = new_width
            dashboard_slot.height = new_height
            dashboard_slot.save()

        return JsonResponse({'ok': True}, status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=["POST"])
