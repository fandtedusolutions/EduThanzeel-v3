from io import BytesIO
from pathlib import Path
import logging

import qrcode
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


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
    centered on the white stub area (right side).
    """
    out_path = coupon_cache_path(lead.registration_id)
    if out_path.exists() and not force:
        return out_path

    if not COUPON_TEMPLATE.exists():
        logger.error('Coupon template missing: %s', COUPON_TEMPLATE)
        raise FileNotFoundError(f'Coupon template not found: {COUPON_TEMPLATE}')

    try:
        base = Image.open(COUPON_TEMPLATE).convert('RGB')
    except OSError as exc:
        logger.exception('Could not open coupon template')
        raise exc
    # Measured white stub on coupon.jpeg (2207x827)
    stub_left, stub_right = 1375, 1835
    stub_top, stub_bottom = 132, 694
    stub_center_x = (stub_left + stub_right) // 2  # 1605
    stub_center_y = (stub_top + stub_bottom) // 2  # 413
    stub_width = stub_right - stub_left

    title_font = _font(28, bold=True)
    meta_font = _font(22, bold=False)

    name = (lead.name or '').strip()
    if len(name) > 22:
        name = name[:20] + '…'
    lines = [
        (lead.registration_id, title_font, '#5c0135'),
        (name, meta_font, '#1b0512'),
    ]

    line_gap = 8
    text_h = 0
    line_heights = []
    for text, font, _fill in lines:
        bbox = font.getbbox(text)
        lh = bbox[3] - bbox[1]
        line_heights.append(lh)
        text_h += lh
    text_h += line_gap * (len(lines) - 1)

    # QR itself is centered on the white stub; ID + name sit just under it.
    gap = 14
    bottom_pad = 28
    qr_size = min(260, stub_width - 64, 2 * (stub_center_y - stub_top - 20))
    while qr_size > 160:
        qr_bottom = stub_center_y + qr_size // 2
        if qr_bottom + gap + text_h + bottom_pad <= stub_bottom:
            break
        qr_size -= 8

    qr = _make_qr(scan_url, box_size=7, border=1).resize(
        (qr_size, qr_size), Image.Resampling.NEAREST
    )
    qr_x = stub_center_x - qr_size // 2
    qr_y = stub_center_y - qr_size // 2
    base.paste(qr, (qr_x, qr_y))

    draw = ImageDraw.Draw(base)
    y = qr_y + qr_size + gap
    for (text, font, fill), lh in zip(lines, line_heights):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((stub_center_x - tw // 2, y), text, font=font, fill=fill)
        y += lh + line_gap

    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        base.save(out_path, format='JPEG', quality=92, optimize=True)
    except OSError as exc:
        logger.exception('Could not save coupon image to %s', out_path)
        raise exc
    return out_path



def coupon_image_bytes(lead, scan_url, force=False):
    path = build_coupon_image(lead, scan_url, force=force)
    return path.read_bytes()
