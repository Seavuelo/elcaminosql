import pygame
from game.rendering import draw, make_font
from game.constants import *

_CACHED_TABLE_FONT = None
_CACHED_BADGE_FONT = None

def _get_badge_font():
    global _CACHED_BADGE_FONT
    if _CACHED_BADGE_FONT is None:
        _CACHED_BADGE_FONT = make_font(11)
    return _CACHED_BADGE_FONT

def _get_default_table_font():
    global _CACHED_TABLE_FONT
    if _CACHED_TABLE_FONT is None:
        _CACHED_TABLE_FONT = make_font(14)
    return _CACHED_TABLE_FONT

def wrap_text_lines(text, font, width):
    lines = []
    for paragraph in str(text).split("\n"):
        line = ""
        for word in paragraph.split():
            while font.size(word)[0] > width:
                if line:
                    lines.append(line)
                    line = ""
                end = 1
                while end < len(word) and font.size(word[:end + 1])[0] <= width:
                    end += 1
                lines.append(word[:end])
                word = word[end:]
            candidate = f"{line} {word}" if line else word
            if line and font.size(candidate)[0] > width:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    return lines


def paginate_text(text, font, width, height, line_spacing=2):
    lines = wrap_text_lines(text, font, width)
    count = max(1, (height + line_spacing) // (font.get_linesize() + line_spacing))
    return ["\n".join(lines[i:i + count]) for i in range(0, len(lines), count)] or [""]


def fit_text(text, font, width):
    if font.size(text)[0] <= width:
        return text
    while text and font.size(text + "...")[0] > width:
        text = text[:-1]
    return text + "..."


def render_wrapped_text(surface, text, rect, font, color=COLOR_WHITE, line_spacing=2, padding=4):
    width = rect.width - padding * 2
    if width <= 0:
        return
    old_clip = surface.get_clip()
    surface.set_clip(old_clip.clip(rect))
    y = rect.y + padding
    for line in wrap_text_lines(text, font, width):
        if y + font.get_linesize() > rect.bottom - padding:
            break
        surface.blit(font.render(line, True, color), (rect.x + padding, y))
        y += font.get_linesize() + line_spacing
    surface.set_clip(old_clip)


def draw_panel(surface, rect, bg_color=(14, 18, 28, 240), border_color=COLOR_CYAN, border_width=1, title="", font=None, title_color=COLOR_AMBER):
    from game.visuals import panel, mix
    rect=pygame.Rect(rect)
    panel(surface,rect,bg_color,border_color)

    if title and font:
        header_h = 20
        draw.rect(surface, mix(bg_color,border_color,.09), (rect.x + 2, rect.y + 2, rect.width - 4, header_h-2),border_radius=3)
        draw.line(surface, mix(bg_color,border_color,.28), (rect.x+6, rect.y + header_h), (rect.right-6, rect.y + header_h), 1)
        t_surf = font.render(fit_text(title, font, rect.width - 16), True, title_color)
        surface.blit(t_surf, (rect.x + 8, rect.y + 4))

def fitted_text_layout(text, font, width, min_size=8):
    """Reduce primero la fuente y luego envuelve, sin eliminar caracteres"""
    text = str(text)
    point_size = getattr(font, "point_size", 12)
    selected = font
    for size in range(point_size, min_size - 1, -1):
        selected = font if size == point_size else make_font(size)
        if selected.size(text)[0] <= width:
            break
    lines = wrap_text_lines(text, selected, max(1, width))
    return selected, lines


def draw_fitted_text(surface, text, rect, font, color=COLOR_WHITE, padding=4):
    rect = pygame.Rect(rect)
    selected, lines = fitted_text_layout(text, font, rect.width - padding * 2)
    height = len(lines) * selected.get_linesize()
    top = rect.y + max(padding, (rect.height - height) // 2)
    render_wrapped_text(surface, "\n".join(lines), pygame.Rect(rect.x + padding, top,
                        max(1, rect.width - padding * 2), height), selected,
                        color=color, line_spacing=0, padding=0)


def draw_sql_grid_table(surface, rect, columns, rows, col_types=None, font=None, max_rows=7):
    font = font or _get_default_table_font()
    x, y, w, h = rect
    parent_clip = surface.get_clip()
    surface.set_clip(parent_clip.clip(rect))
    draw.rect(surface, (12, 16, 25), rect)
    draw.rect(surface, (45, 65, 95), rect, 1)
    if not columns:
        draw_fitted_text(surface, "No hay columnas ni datos para mostrar", rect, font, COLOR_GRAY)
        surface.set_clip(parent_clip)
        return

    def value_text(value):
        return "NULL" if value is None else str(value)

    index_width = 24
    available = max(1, w - index_width - 4)
    desired = [max(40, font.size(str(name))[0] + 12,
                   max((font.size(value_text(row[i]))[0] + 12 for row in rows[:max_rows]
                        if i < len(row)), default=0)) for i, name in enumerate(columns)]
    total = sum(desired)
    widths = [max(1, int(width * available / total)) for width in desired]
    widths[-1] += available - sum(widths)
    positions = []
    current = x + index_width
    for width in widths:
        positions.append(current)
        current += width

    def content_height(values):
        heights = []
        for text, width in zip(values, widths):
            cell_font, lines = fitted_text_layout(text, font, max(1, width - 8))
            heights.append(len(lines) * cell_font.get_linesize() + 8)
        return max(17, *heights)

    header_h = max(22, content_height(columns))
    footer_y = y + h - 16
    draw.rect(surface, (24, 36, 56), (x + 1, y + 1, w - 2, header_h))
    draw_fitted_text(surface, "#", pygame.Rect(x + 1, y, index_width - 2, header_h), font, COLOR_GRAY)
    for i, column in enumerate(columns):
        draw_fitted_text(surface, column, pygame.Rect(positions[i], y, widths[i], header_h), font, COLOR_CYAN)
    draw.line(surface, (60, 85, 125), (x, y + header_h), (x + w, y + header_h))

    shown = 0
    row_y = y + header_h + 1
    for index, row in enumerate(rows[:max_rows]):
        values = [value_text(value) for value in row]
        row_h = content_height(values)
        if row_y + row_h > footer_y:
            break
        background = (16, 22, 34) if index % 2 == 0 else (21, 28, 44)
        draw.rect(surface, background, (x + 1, row_y, w - 2, row_h))
        draw_fitted_text(surface, str(index + 1), pygame.Rect(x + 1, row_y, index_width - 2, row_h), font, COLOR_GRAY)
        for col_index, value in enumerate(row[:len(columns)]):
            color = (255, 120, 100) if value is None else ((160, 240, 180) if isinstance(value, (int, float)) else COLOR_WHITE)
            draw_fitted_text(surface, value_text(value), pygame.Rect(positions[col_index], row_y,
                              widths[col_index], row_h), font, color)
        draw.line(surface, (30, 42, 65), (x + 1, row_y + row_h), (x + w - 1, row_y + row_h))
        row_y += row_h
        shown += 1
    for col_x in positions:
        draw.line(surface, (40, 60, 90), (col_x, y), (col_x, footer_y))
    draw.rect(surface, (18, 25, 40), (x + 1, footer_y, w - 2, 15))
    footer = f"Mostrando {shown} de {len(rows)} filas | {len(columns)} columnas"
    draw_fitted_text(surface, footer, pygame.Rect(x + 4, footer_y, w - 8, 15), font, COLOR_AMBER, padding=1)
    surface.set_clip(parent_clip)


def paginate_grid_rows(columns, rows, font, width, height):
    """Usa las mismas medidas del grid para no ocultar registros en una clase"""
    def fits(chunk):
        desired = [max(40, font.size(str(name))[0]+12, max((font.size('NULL' if row[i] is None else str(row[i]))[0]+12 for row in chunk), default=0)) for i,name in enumerate(columns)]
        available = width-28
        widths = [max(1,int(value*available/sum(desired))) for value in desired]
        widths[-1] += available-sum(widths)
        def row_height(values):
            sizes = []
            for value,w in zip(values,widths):
                selected,lines = fitted_text_layout('NULL' if value is None else str(value),font,max(1,w-8))
                sizes.append(len(lines)*selected.get_linesize()+8)
            return max(17,*sizes)
        return max(22,row_height(columns)) + 1 + sum(row_height(row) for row in chunk) <= height-16
    pages, current = [], []
    for row in rows:
        if current and (len(current) == 5 or not fits(current+[row])):
            pages.append(current)
            current = []
        current.append(row)
    return pages+[current] if current else pages or [[]]
