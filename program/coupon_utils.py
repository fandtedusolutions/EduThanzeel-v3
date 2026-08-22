from io import BytesIO
from pathlib import Path

import qrcode
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont


COUPON_TEMPLATE = Path(settings.BASE_DIR) / 'static' / 'tukuja' / 'coupon.jpeg'
COUPON_CACHE_DIR = Path(settings.MEDIA_ROOT) / 'tukuja' / 'coupons'


def _font(size, bold=False):
    candidates = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _make_qr(data, box_size=8, border=2):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color='#1b0512', back_color='white').convert('RGB')


def coupon_cache_path(registration_id):
    COUPON_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return COUPON_CACHE_DIR / f'{registration_id}.jpg'


def build_coupon_image(lead, scan_url, force=False):
    """
    Compose personalized coupon from template with QR + guest details
    on the white stub area (right side).
    """
    out_path = coupon_cache_path(lead.registration_id)
    if out_path.exists() and not force:
        return out_path

    base = Image.open(COUPON_TEMPLATE).convert('RGB')
    width, height = base.size  # 2207 x 827

    # White stub roughly x: 1480–1830
    stub_left, stub_right = 1488, 1828
    stub_center_x = (stub_left + stub_right) // 2
    stub_width = stub_right - stub_left

    qr_size = min(300, stub_width - 40)
    qr = _make_qr(scan_url, box_size=7, border=1).resize((qr_size, qr_size), Image.Resampling.NEAREST)
    qr_x = stub_center_x - qr_size // 2
    qr_y = 95
    base.paste(qr, (qr_x, qr_y))

    draw = ImageDraw.Draw(base)
    title_font = _font(28, bold=True)
    meta_font = _font(22, bold=False)
    small_font = _font(18, bold=False)
    ink = '#1b0512'
    maroon = '#5c0135'

    def center_text(text, y, font, fill=ink):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((stub_center_x - tw // 2, y), text, font=font, fill=fill)

    text_top = qr_y + qr_size + 18
    center_text(lead.registration_id, text_top, title_font, maroon)

    name = (lead.name or '').strip()
    if len(name) > 22:
        name = name[:20] + '…'
    center_text(name, text_top + 36, meta_font, ink)

    batch_label = f'Food Batch {lead.food_batch}' if lead.food_batch else 'Food Batch —'
    center_text(batch_label, text_top + 68, small_font, maroon)

    seats = f'{lead.total_attending} seat{"s" if lead.total_attending != 1 else ""}'
    center_text(seats, text_top + 94, small_font, ink)

    base.save(out_path, format='JPEG', quality=92, optimize=True)
    return out_path


def coupon_image_bytes(lead, scan_url, force=False):
    path = build_coupon_image(lead, scan_url, force=force)
    return path.read_bytes()
