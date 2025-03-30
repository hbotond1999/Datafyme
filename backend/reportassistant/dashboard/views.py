import json
import logging
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed, JsonResponse, HttpResponseForbidden, HttpResponse, HttpResponseNotFound, \
    HttpResponseServerError
from django.utils.text import slugify
from dashboard.models import Dashboard, DashboardSlot
from dashboard.services.pptx.presentation import create_presentation


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
             "chart_id": slot.chart_id,
             "title": slot.chart.title,
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

@login_required
def update_dashboard_slots(request):
    if request.method == 'POST':
        slots = json.loads(request.body).get('slots', [])
        for slot in slots:
            new_col_num = slot.get('x', 0)
            new_row_num = slot.get('y', 0)
            new_width = slot.get('w', 0)
            new_height = slot.get('h', 0)
            slot_id = slot.get('slot_id')
            if not slot_id:
                continue
            dashboard_slot = DashboardSlot.objects.get(id=slot_id)
            dashboard_slot.col_num = new_col_num
            dashboard_slot.row_num = new_row_num
            dashboard_slot.width = new_width
            dashboard_slot.height = new_height
            dashboard_slot.save()

        return JsonResponse({'ok': True}, status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=["POST"])


@login_required
def delete_dashboard_slot(request, slot_id: int):
    if request.method == 'DELETE':
        dashboard_slot = DashboardSlot.objects.get(id=slot_id)
        dashboard_slot.delete()
        return JsonResponse({'ok': True}, status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=["DELETE"])

@login_required
def delete_dashboard(request, dashboard_id: int):
    if request.method == 'DELETE':
        dashboard = Dashboard.objects.get(id=dashboard_id)
        if not dashboard:
            return JsonResponse({'error': 'dashboard not exists'}, status=404)

        dashboard.delete()
        return JsonResponse({'ok': True}, status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=["DELETE"])

@login_required
def add_dashboard_slot(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        dashboard_slot = DashboardSlot(
            dashboard_id=body['dashboard_id'],
            chart_id=body['chart_id'],
            col_num=body['x'],
            row_num=body['y'],
            width=body['w'],
            height=body['h'],
        )

        dashboard_slot.save()
        return JsonResponse({'ok': True}, status=200)
    else:
        return HttpResponseNotAllowed(permitted_methods=["POST"])


@login_required
def export_dashboard_to_pptx(request, dashboard_id: int):
    """
    Django view to export a dashboard to a PowerPoint presentation.
    Each chart will be placed on a separate slide.

    Args:
        request: The HTTP request
        dashboard_id: The ID of the dashboard to export

    Returns:
        HTTP response with the PowerPoint file for download
    """
    if request.method == 'GET':
        try:
            dashboard = Dashboard.objects.get(id=dashboard_id)
            if dashboard.user != request.user:
                return HttpResponseForbidden("You don't have permission to export this dashboard.")

            prs = create_presentation(dashboard)

            pptx_data = BytesIO()
            prs.save(pptx_data)
            pptx_data.seek(0)

            response = HttpResponse(
                pptx_data.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
            )
            filename = f"{slugify(dashboard.title)}-export.pptx"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response

        except Dashboard.DoesNotExist:
            return HttpResponseNotFound("Dashboard not found")
        except Exception as e:
            logging.error(f"Error exporting dashboard {dashboard_id}: {str(e)}")
            return HttpResponseServerError(f"Error exporting dashboard: {str(e)}")
    else:
        return HttpResponseNotAllowed(['GET'])