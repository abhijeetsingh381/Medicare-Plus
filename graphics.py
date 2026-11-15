"""
Graphics & Visualization Engine for Medicare Plus Hospital Management System.
Uses Pillow (PIL) to generate retina-sharp, anti-aliased UI components,
donut ring gauges, sparkline trend charts, and rounded badges.
"""

from PIL import Image, ImageDraw, ImageTk, ImageFilter, ImageFont
import math


def render_donut_chart(size=140, percentage=41, color='#0F766E', bg_track='#e2e8f0', thickness=14, center_number=None, center_label=None):
    """
    Renders an anti-aliased donut ring gauge with supersampling.
    """
    scale = 3  # 3x supersampling for ultra-crisp antialiasing
    s = size * scale
    th = thickness * scale

    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Outer bounding box
    pad = th // 2 + 2 * scale
    bbox = [pad, pad, s - pad, s - pad]

    # Background track circle
    draw.arc(bbox, start=0, end=360, fill=bg_track, width=th)

    # Active progress arc
    angle = int(360 * (percentage / 100.0))
    if angle > 0:
        draw.arc(bbox, start=-90, end=-90 + angle, fill=color, width=th)

    # Resize down with Lanczos resampling
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


def render_trend_chart(width=340, height=85, values=None, line_color='#0F766E', fill_color='#e0f2fe'):
    """
    Renders a smooth 7-day admissions trend curve with soft area fill.
    """
    if not values:
        values = [14, 21, 18, 29, 24, 34, 31]

    scale = 2
    w, h = width * scale, height * scale
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad_x = 18 * scale
    pad_y = 14 * scale
    max_v = max(values)
    min_v = min(values)
    rng = max_v - min_v if max_v != min_v else 1

    points = []
    n = len(values)
    step_x = (w - 2 * pad_x) / (n - 1)

    for i, v in enumerate(values):
        x = pad_x + i * step_x
        y = h - pad_y - ((v - min_v) / rng) * (h - 2 * pad_y)
        points.append((x, y))

    # Area fill polygon
    poly = [(points[0][0], h)] + points + [(points[-1][0], h)]
    draw.polygon(poly, fill=fill_color)

    # Line connecting points
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=line_color, width=3*scale)
        # Point dot
        r = 3 * scale
        draw.ellipse([points[i][0]-r, points[i][1]-r, points[i][0]+r, points[i][1]+r], fill='#ffffff', outline=line_color, width=2*scale)

    r = 3 * scale
    draw.ellipse([points[-1][0]-r, points[-1][1]-r, points[-1][0]+r, points[-1][1]+r], fill='#ffffff', outline=line_color, width=2*scale)

    img = img.resize((width, height), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


def render_pill_badge(width, height, radius=None, bg_color='#CCFBF1', border_color=None):
    """
    Renders a supersampled rounded pill container.
    """
    scale = 2
    w, h = width * scale, height * scale
    r = (height // 2) * scale if radius is None else radius * scale

    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([0, 0, w-1, h-1], radius=r, fill=bg_color, outline=border_color, width=1*scale if border_color else 0)

    img = img.resize((width, height), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)
