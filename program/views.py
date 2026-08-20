from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import openpyxl
from openpyxl.styles import Font

from .models import Rsvp
from .serializers import RsvpSerializer


def tukuja(request):
    return render(request, 'tukuja/index.html')


@api_view(['POST'])
def submit_rsvp(request):
    serializer = RsvpSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                'message': 'RSVP confirmed.',
                'registration_id': serializer.instance.registration_id,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def _filtered_rsvps(request):
    rsvps = Rsvp.objects.annotate(
        guest_total=F('attending_members') + F('attending_children'),
    )
    filters = {
        'q': request.GET.get('q', '').strip(),
        'name': request.GET.get('name', '').strip(),
        'phone': request.GET.get('phone', '').strip(),
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
        'members': request.GET.get('members', ''),
        'children': request.GET.get('children', ''),
        'party': request.GET.get('party', ''),
        'sort': request.GET.get('sort', '-created_at'),
    }

    if filters['q']:
        rsvps = rsvps.filter(
            Q(name__icontains=filters['q'])
            | Q(phone_number__icontains=filters['q'])
            | Q(registration_id__icontains=filters['q'])
        )
    if filters['name']:
        rsvps = rsvps.filter(name__icontains=filters['name'])
    if filters['phone']:
        rsvps = rsvps.filter(phone_number__icontains=filters['phone'])
    if filters['date_from']:
        rsvps = rsvps.filter(created_at__date__gte=filters['date_from'])
    if filters['date_to']:
        rsvps = rsvps.filter(created_at__date__lte=filters['date_to'])
    if filters['members'].isdigit():
        rsvps = rsvps.filter(attending_members=int(filters['members']))
    if filters['children'].isdigit():
        rsvps = rsvps.filter(attending_children=int(filters['children']))
    if filters['party'] == 'with_children':
        rsvps = rsvps.filter(attending_children__gt=0)
    elif filters['party'] == 'members_only':
        rsvps = rsvps.filter(attending_children=0)

    sort_map = {
        '-created_at': '-created_at',
        'created_at': 'created_at',
        'name': 'name',
        '-name': '-name',
        '-guests': '-guest_total',
        'guests': 'guest_total',
    }
    rsvps = rsvps.order_by(sort_map.get(filters['sort'], '-created_at'))
    return rsvps, filters


@login_required
def tukuja_dashboard(request):
    rsvps_qs, filters = _filtered_rsvps(request)
    totals = rsvps_qs.aggregate(
        members=Sum('attending_members'),
        children=Sum('attending_children'),
    )
    members = totals['members'] or 0
    children = totals['children'] or 0

    paginator = Paginator(rsvps_qs, 25)
    page = paginator.get_page(request.GET.get('page'))
    query = request.GET.copy()
    query.pop('page', None)

    return render(request, 'tukuja/dashboard.html', {
        'rsvps': page,
        'filters': filters,
        'querystring': query.urlencode(),
        'has_filters': any(v for k, v in filters.items() if k != 'sort' and v),
        'stats': {
            'total_rsvps': rsvps_qs.count(),
            'total_members': members,
            'total_children': children,
            'total_attending': members + children,
        },
    })


@login_required
def export_tukuja_excel(request):
    rsvps_qs, _ = _filtered_rsvps(request)
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Tu Kuja RSVPs'
    headers = ['ID', 'Name', 'Phone Number', 'Attending Members', 'Attending Children', 'Total', 'Submitted']
    sheet.append(headers)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    for rsvp in rsvps_qs:
        sheet.append([
            rsvp.registration_id,
            rsvp.name,
            rsvp.phone_number,
            rsvp.attending_members,
            rsvp.attending_children,
            rsvp.total_attending,
            rsvp.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=tukuja-rsvps.xlsx'
    workbook.save(response)
    return response


@login_required
def delete_tukuja_rsvp(request, pk):
    rsvp = get_object_or_404(Rsvp, pk=pk)
    rsvp.delete()
    return redirect('tukuja_dashboard')
