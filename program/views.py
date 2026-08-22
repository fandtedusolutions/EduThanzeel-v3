from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Q, Sum
from django.http import HttpResponse, FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from urllib.parse import quote
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import logging
import openpyxl
from openpyxl.styles import Font

from .models import Rsvp
from .serializers import RsvpSerializer
from .coupon_utils import build_coupon_image

logger = logging.getLogger(__name__)


def tukuja(request):
    return render(request, 'tukuja/index.html')


def _absolute(request, name, **kwargs):
    return request.build_absolute_uri(reverse(name, kwargs=kwargs))


def _detail_absolute_url(request, registration_id):
    """Public registration detail page (WhatsApp + QR target)."""
    return _absolute(request, 'tukuja_coupon', registration_id=registration_id)


def _pass_absolute_url(request, registration_id):
    return _detail_absolute_url(request, registration_id)


def _coupon_image_absolute_url(request, registration_id):
    return _absolute(request, 'tukuja_coupon_image', registration_id=registration_id)


def _ensure_coupon(request, lead, force=False):
    """Build coupon image; return path or None if generation fails."""
    detail_url = _detail_absolute_url(request, lead.registration_id)
    try:
        return build_coupon_image(lead, detail_url, force=force)
    except Exception:
        logger.exception('Coupon generation failed for %s', lead.registration_id)
        return None


def _whatsapp_share_url(request, lead):
    """WhatsApp message: greeting + line break + pass link (no image build here)."""
    detail_url = _detail_absolute_url(request, lead.registration_id)
    phone = ''.join(ch for ch in (lead.phone_number or '') if ch.isdigit())
    message = (
        f'Your journey to TU KUJA MAN KUJA,\n'
        f'pass : {detail_url}'
    )
    return f'https://wa.me/{phone}?text={quote(message)}'


def _attach_share_links(request, leads):
    for lead in leads:
        lead.pass_url = _detail_absolute_url(request, lead.registration_id)
        lead.coupon_image_url = _coupon_image_absolute_url(request, lead.registration_id)
        lead.whatsapp_url = _whatsapp_share_url(request, lead)
        lead.whatsapp_send_url = reverse('send_tukuja_whatsapp', kwargs={'pk': lead.pk})
    return leads


def tukuja_pass(request, registration_id):
    return redirect('tukuja_coupon', registration_id=registration_id)


def tukuja_coupon(request, registration_id):
    """Registration detail page: guest fields + coupon + download."""
    lead = get_object_or_404(Rsvp, registration_id=registration_id)
    path = _ensure_coupon(request, lead)
    cache_bust = int(path.stat().st_mtime) if path and path.exists() else 0
    image_url = _coupon_image_absolute_url(request, lead.registration_id)
    return render(request, 'tukuja/coupon.html', {
        'lead': lead,
        'coupon_image_url': f'{image_url}?v={cache_bust}' if path else '',
        'coupon_download_url': image_url if path else '',
        'detail_url': _detail_absolute_url(request, lead.registration_id),
        'coupon_error': path is None,
    })


def tukuja_coupon_image(request, registration_id):
    lead = get_object_or_404(Rsvp, registration_id=registration_id)
    path = _ensure_coupon(request, lead)
    if not path or not path.exists():
        raise Http404('Coupon image not found')
    response = FileResponse(open(path, 'rb'), content_type='image/jpeg')
    response['Content-Disposition'] = f'inline; filename="{lead.registration_id}-coupon.jpg"'
    response['Cache-Control'] = 'no-cache, max-age=0, must-revalidate'
    return response


def tukuja_scan(request, registration_id):
    """Old QR URLs redirect to the registration detail page."""
    return redirect('tukuja_coupon', registration_id=registration_id)


@api_view(['POST'])
def submit_rsvp(request):
    serializer = RsvpSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                'message': 'Registration confirmed.',
                'registration_id': serializer.instance.registration_id,
                'pass_url': _pass_absolute_url(request, serializer.instance.registration_id),
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def _normalize_phone(value):
    digits = ''.join(ch for ch in (value or '') if ch.isdigit())
    if digits.startswith('91') and len(digits) == 12:
        digits = digits[2:]
    if len(digits) != 10:
        return None, 'Enter a 10 digit phone number.'
    return f'+91{digits}', None


def _filtered_leads(request, status_value):
    leads = Rsvp.objects.filter(status=status_value).annotate(
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
        leads = leads.filter(
            Q(name__icontains=filters['q'])
            | Q(phone_number__icontains=filters['q'])
            | Q(registration_id__icontains=filters['q'])
        )
    if filters['name']:
        leads = leads.filter(name__icontains=filters['name'])
    if filters['phone']:
        leads = leads.filter(phone_number__icontains=filters['phone'])
    if filters['date_from']:
        leads = leads.filter(created_at__date__gte=filters['date_from'])
    if filters['date_to']:
        leads = leads.filter(created_at__date__lte=filters['date_to'])
    if filters['members'].isdigit():
        leads = leads.filter(attending_members=int(filters['members']))
    if filters['children'].isdigit():
        leads = leads.filter(attending_children=int(filters['children']))
    if filters['party'] == 'with_children':
        leads = leads.filter(attending_children__gt=0)
    elif filters['party'] == 'members_only':
        leads = leads.filter(attending_children=0)

    sort_map = {
        '-created_at': '-created_at',
        'created_at': 'created_at',
        'name': 'name',
        '-name': '-name',
        '-guests': '-guest_total',
        'guests': 'guest_total',
    }
    leads = leads.order_by(sort_map.get(filters['sort'], '-created_at'))
    return leads, filters


def _dashboard_context(request, status_value, page_title, empty_message, include_whatsapp=False):
    leads_qs, filters = _filtered_leads(request, status_value)
    totals = leads_qs.aggregate(
        members=Sum('attending_members'),
        children=Sum('attending_children'),
    )
    members = totals['members'] or 0
    children = totals['children'] or 0

    paginator = Paginator(leads_qs, 25)
    page = paginator.get_page(request.GET.get('page'))
    if include_whatsapp:
        _attach_share_links(request, page.object_list)
    query = request.GET.copy()
    query.pop('page', None)

    return {
        'leads': page,
        'filters': filters,
        'querystring': query.urlencode(),
        'has_filters': any(v for k, v in filters.items() if k != 'sort' and v),
        'status_value': status_value,
        'page_title': page_title,
        'empty_message': empty_message,
        'show_whatsapp': include_whatsapp,
        'nav_page': 'converted' if status_value == Rsvp.STATUS_CONVERTED else 'leads',
        'stats': {
            'total_leads': leads_qs.count(),
            'total_members': members,
            'total_children': children,
            'total_attending': members + children,
            'pending_count': Rsvp.objects.filter(status=Rsvp.STATUS_PENDING).count(),
            'converted_count': Rsvp.objects.filter(status=Rsvp.STATUS_CONVERTED).count(),
        },
    }


@login_required
def tukuja_dashboard(request):
    pending = Rsvp.objects.filter(status=Rsvp.STATUS_PENDING)
    converted = Rsvp.objects.filter(status=Rsvp.STATUS_CONVERTED)
    pending_totals = pending.aggregate(
        members=Sum('attending_members'),
        children=Sum('attending_children'),
    )
    converted_totals = converted.aggregate(
        members=Sum('attending_members'),
        children=Sum('attending_children'),
    )
    pending_members = pending_totals['members'] or 0
    pending_children = pending_totals['children'] or 0
    converted_members = converted_totals['members'] or 0
    converted_children = converted_totals['children'] or 0
    all_members = pending_members + converted_members
    all_children = pending_children + converted_children

    return render(request, 'tukuja/dashboard_home.html', {
        'nav_page': 'dashboard',
        'stats': {
            'pending_count': pending.count(),
            'converted_count': converted.count(),
            'total_count': pending.count() + converted.count(),
            'total_members': all_members,
            'total_children': all_children,
            'total_attending': all_members + all_children,
            'pending_members': pending_members,
            'pending_children': pending_children,
            'converted_members': converted_members,
            'converted_children': converted_children,
        },
    })


@login_required
def tukuja_leads(request):
    context = _dashboard_context(
        request,
        Rsvp.STATUS_PENDING,
        'Leads',
        'No pending leads match these filters.',
        include_whatsapp=False,
    )
    return render(request, 'tukuja/dashboard.html', context)


@login_required
def tukuja_converted(request):
    context = _dashboard_context(
        request,
        Rsvp.STATUS_CONVERTED,
        'Converted',
        'No converted leads yet.',
        include_whatsapp=True,
    )
    return render(request, 'tukuja/dashboard.html', context)


@login_required
def export_tukuja_excel(request):
    status_value = request.GET.get('status', Rsvp.STATUS_PENDING)
    if status_value not in (Rsvp.STATUS_PENDING, Rsvp.STATUS_CONVERTED):
        status_value = Rsvp.STATUS_PENDING
    leads_qs, _ = _filtered_leads(request, status_value)
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Tu Kuja Registrations'
    headers = [
        'ID', 'Name', 'Phone Number', 'Attending Members', 'Attending Children',
        'Total', 'Status', 'Submitted',
    ]
    sheet.append(headers)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    for lead in leads_qs:
        sheet.append([
            lead.registration_id,
            lead.name,
            lead.phone_number,
            lead.attending_members,
            lead.attending_children,
            lead.total_attending,
            lead.get_status_display(),
            lead.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename=tukuja-{status_value}.xlsx'
    workbook.save(response)
    return response


@login_required
def tukuja_food_batch(request):
    # Backfill any converted leads missing a batch number.
    missing = Rsvp.objects.filter(status=Rsvp.STATUS_CONVERTED, food_batch__isnull=True).order_by('created_at', 'id')
    for lead in missing:
        Rsvp.assign_food_batch(lead)
        lead.save(update_fields=['food_batch', 'updated_at'])

    batches = Rsvp.all_food_batches()
    converted = Rsvp.objects.filter(status=Rsvp.STATUS_CONVERTED)
    pending_count = Rsvp.objects.filter(status=Rsvp.STATUS_PENDING).count()
    converted_count = converted.count()
    totals = converted.aggregate(
        members=Sum('attending_members'),
        children=Sum('attending_children'),
    )
    seats_used = (totals['members'] or 0) + (totals['children'] or 0)
    size_counts = Rsvp.family_size_counts(converted)

    return render(request, 'tukuja/food_batch.html', {
        'nav_page': 'food_batch',
        'batches': batches,
        'batch_count': len(batches),
        'seat_capacity': Rsvp.FOOD_SEAT_CAPACITY,
        'stats': {
            'total_registrations': pending_count + converted_count,
            'pending_count': pending_count,
            'converted_count': converted_count,
            'seats_used': seats_used,
            'size_counts': size_counts,
        },
    })


@login_required
def edit_tukuja_lead(request, pk):
    lead = get_object_or_404(Rsvp, pk=pk)
    redirect_name = (
        'tukuja_converted'
        if lead.status == Rsvp.STATUS_CONVERTED
        else 'tukuja_leads'
    )
    error = ''

    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        phone_raw = request.POST.get('phone_number') or ''
        members = request.POST.get('attending_members')
        children = request.POST.get('attending_children')
        new_status = request.POST.get('status', lead.status)

        phone, phone_error = _normalize_phone(phone_raw)
        try:
            members = int(members)
            children = int(children)
        except (TypeError, ValueError):
            members = -1
            children = -1

        if len(name) < 2:
            error = 'Please enter a valid name.'
        elif phone_error:
            error = phone_error
        elif Rsvp.objects.filter(phone_number=phone).exclude(pk=lead.pk).exists():
            error = 'This phone number is already registered.'
        elif members < 1:
            error = 'Attending members must be at least 1.'
        elif children < 0:
            error = 'Children count cannot be negative.'
        elif members + children > 5:
            error = 'Only 5 members allowed.'
        elif new_status not in (Rsvp.STATUS_PENDING, Rsvp.STATUS_CONVERTED):
            error = 'Invalid status.'
        else:
            lead.name = name
            lead.phone_number = phone
            lead.attending_members = members
            lead.attending_children = children
            lead.status = new_status
            if new_status == Rsvp.STATUS_CONVERTED:
                batch_number, _ = Rsvp.assign_food_batch(lead)
                lead.food_batch = batch_number
            else:
                lead.food_batch = None
            lead.save()
            if new_status == Rsvp.STATUS_CONVERTED:
                if _ensure_coupon(request, lead, force=True) is None:
                    messages.warning(request, f'{lead.registration_id} saved, but coupon image could not be generated.')
            messages.success(request, f'{lead.registration_id} updated.')
            if new_status == Rsvp.STATUS_CONVERTED:
                return redirect('tukuja_converted')
            return redirect('tukuja_leads')

        lead.name = name
        lead.attending_members = max(members, 0) if isinstance(members, int) else lead.attending_members
        lead.attending_children = max(children, 0) if isinstance(children, int) else lead.attending_children
        lead.status = new_status if new_status in (Rsvp.STATUS_PENDING, Rsvp.STATUS_CONVERTED) else lead.status

    return render(request, 'tukuja/edit_lead.html', {
        'lead': lead,
        'error': error,
        'redirect_name': redirect_name,
    })


@login_required
def mark_tukuja_converted(request, pk):
    lead = get_object_or_404(Rsvp, pk=pk)
    if lead.status != Rsvp.STATUS_CONVERTED:
        batch_number, usage = Rsvp.assign_food_batch(lead)
        lead.status = Rsvp.STATUS_CONVERTED
        lead.food_batch = batch_number
        lead.save(update_fields=['status', 'food_batch', 'updated_at'])
        if _ensure_coupon(request, lead, force=True) is None:
            messages.warning(request, f'{lead.registration_id} converted, but coupon image could not be generated.')
        filled = usage['used'] + lead.total_attending
        messages.success(
            request,
            (
                f'{lead.registration_id} converted into Food Batch {batch_number}. '
                f'Seats in this batch: {min(filled, Rsvp.FOOD_SEAT_CAPACITY)}/{Rsvp.FOOD_SEAT_CAPACITY}.'
            ),
        )
    return redirect('tukuja_converted')


@login_required
def send_tukuja_whatsapp(request, pk):
    lead = get_object_or_404(Rsvp, pk=pk, status=Rsvp.STATUS_CONVERTED)
    if not lead.whatsapp_sent_at:
        lead.whatsapp_sent_at = timezone.now()
        lead.save(update_fields=['whatsapp_sent_at', 'updated_at'])
    return redirect(_whatsapp_share_url(request, lead))


@login_required
def mark_tukuja_pending(request, pk):
    lead = get_object_or_404(Rsvp, pk=pk)
    lead.status = Rsvp.STATUS_PENDING
    lead.food_batch = None
    lead.whatsapp_sent_at = None
    lead.save(update_fields=['status', 'food_batch', 'whatsapp_sent_at', 'updated_at'])
    messages.success(request, f'{lead.registration_id} moved back to leads.')
    return redirect('tukuja_leads')


@login_required
def delete_tukuja_rsvp(request, pk):
    lead = get_object_or_404(Rsvp, pk=pk)
    was_converted = lead.status == Rsvp.STATUS_CONVERTED
    lead.delete()
    return redirect('tukuja_converted' if was_converted else 'tukuja_leads')
