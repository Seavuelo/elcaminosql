import pygame
from game.constants import *

_CACHED_TABLE_FONT = None
_CACHED_BADGE_FONT = None

def _get_badge_font():
    global _CACHED_BADGE_FONT
    if _CACHED_BADGE_FONT is None:
        _CACHED_BADGE_FONT = pygame.font.Font(None, 11)
    return _CACHED_BADGE_FONT

def _get_default_table_font():
    global _CACHED_TABLE_FONT
    if _CACHED_TABLE_FONT is None:
        _CACHED_TABLE_FONT = pygame.font.Font(None, 14)
    return _CACHED_TABLE_FONT

def render_wrapped_text(surface, text, rect, font, color=COLOR_WHITE, line_spacing=2, padding=4):
    """
    Renderiza texto garantizando que NUNCA se salga del marco (Word-wrap riguroso).
    Maneja saltos de línea explícitos ('\\n'), saltos automáticos por ancho de palabra
    y partición de palabras extra-largas si superan el ancho disponible.
    """
    x, y = rect.x + padding, rect.y + padding
    max_w, max_h = rect.width - (padding * 2), rect.height - (padding * 2)
    if max_w <= 10 or max_h <= 10:
        return

    current_y = y
    line_h = font.get_linesize()

    paragraphs = str(text).split("\n")
    for para in paragraphs:
        raw_words = para.split(" ")
        words = []
        # Asegurar que ninguna palabra individual sobrepase max_w
        for w in raw_words:
            if not w:
                continue
            if font.size(w)[0] > max_w:
                chunk = ""
                for char in w:
                    if font.size(chunk + char)[0] <= max_w:
                        chunk += char
                    else:
                        if chunk:
                            words.append(chunk)
                        chunk = char
                if chunk:
                    words.append(chunk)
            else:
                words.append(w)

        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            line_w = font.size(test_line)[0]
            if line_w <= max_w:
                current_line.append(word)
            else:
                if current_line:
                    line_surf = font.render(" ".join(current_line), True, color)
                    if current_y + line_h <= y + max_h:
                        surface.blit(line_surf, (x, current_y))
                        current_y += line_h + line_spacing
                    else:
                        return
                current_line = [word]

        if current_line:
            line_surf = font.render(" ".join(current_line), True, color)
            if current_y + line_h <= y + max_h:
                surface.blit(line_surf, (x, current_y))
                current_y += line_h + line_spacing
            else:
                return

def draw_panel(surface, rect, bg_color=(14, 18, 28, 240), border_color=COLOR_CYAN, border_width=1, title="", font=None, title_color=COLOR_AMBER):
    """Dibuja un panel retro profesional con borde y encabezado opcional."""
    if len(bg_color) == 4:
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill(bg_color)
        surface.blit(s, (rect.x, rect.y))
    else:
        pygame.draw.rect(surface, bg_color, rect)
        
    pygame.draw.rect(surface, border_color, rect, border_width)

    if title and font:
        header_h = 20
        pygame.draw.rect(surface, (25, 35, 55), (rect.x + 1, rect.y + 1, rect.width - 2, header_h))
        pygame.draw.line(surface, border_color, (rect.x, rect.y + header_h), (rect.x + rect.width, rect.y + header_h), 1)
        t_surf = font.render(title, True, title_color)
        surface.blit(t_surf, (rect.x + 8, rect.y + 4))

def draw_sql_grid_table(surface, rect, columns, rows, col_types=None, font=None, max_rows=7):
    """
    Renderizador visual de base de datos tipo DBeaver / Hoja de Cálculo:
    - Columna de índice de fila (#)
    - Etiquetas de tipo de dato [INT], [TXT], [NUM]
    - Cuadrícula con líneas divisorias
    - Rayado de cebra
    - Valores NULL estilizados
    """
    if font is None:
        font = _get_default_table_font()
    font_badge = _get_badge_font()

    x, y, w, h = rect.x, rect.y, rect.width, rect.height

    # Fondo base del visor
    pygame.draw.rect(surface, (12, 16, 25), rect)
    pygame.draw.rect(surface, (45, 65, 95), rect, 1)

    if not columns:
        empty_msg = font.render("(No hay columnas ni datos para mostrar)", True, COLOR_GRAY)
        surface.blit(empty_msg, (x + 15, y + 20))
        return

    # Ancho de la columna de índice (#)
    row_num_w = 26
    
    # Calcular anchos de columna adaptativos según el contenido real y nombres
    avail_w = w - row_num_w - 4
    num_cols = len(columns)
    visible_rows = rows[:max_rows]

    # Calcular ancho deseado por columna (mínimo el ancho del encabezado + padding)
    col_widths = []
    for c_idx, col_name in enumerate(columns):
        header_w = font.size(str(col_name))[0] + 16
        val_w = 0
        for r in visible_rows:
            if c_idx < len(r):
                val_str = f"{r[c_idx]:.1f}" if isinstance(r[c_idx], float) else str(r[c_idx] if r[c_idx] is not None else "NULL")
                val_w = max(val_w, font.size(val_str)[0] + 14)
        col_widths.append(max(60, header_w, val_w))

    total_req_w = sum(col_widths)
    if total_req_w < avail_w:
        # Distribuir espacio sobrante proporcionalmente
        extra = avail_w - total_req_w
        for i in range(num_cols):
            col_widths[i] += int(extra * (col_widths[i] / total_req_w))
    elif total_req_w > avail_w:
        # Escalar respetando un mínimo legible
        scale = avail_w / float(total_req_w)
        min_each = max(50, avail_w // num_cols)
        col_widths = [max(min_each, int(cw * scale)) for cw in col_widths]

    # Calcular posiciones X de cada columna
    col_x_positions = []
    curr_cx = x + row_num_w
    for cw in col_widths:
        col_x_positions.append(curr_cx)
        curr_cx += cw

    header_h = 22
    row_h = 17

    # 1. Cabecera estilo IDE de base de datos
    pygame.draw.rect(surface, (24, 36, 56), (x + 1, y + 1, w - 2, header_h))
    pygame.draw.line(surface, (60, 85, 125), (x, y + header_h), (x + w, y + header_h), 1)

    # Celda encabezado de índice (#)
    idx_header = font.render("#", True, (120, 140, 170))
    surface.blit(idx_header, (x + 8, y + 5))
    pygame.draw.line(surface, (60, 85, 125), (x + row_num_w, y), (x + row_num_w, y + h), 1)

    # Encabezados de columnas (con recorte seguro para no desbordar)
    old_clip = surface.get_clip()
    for c_idx, col_name in enumerate(columns):
        col_x = col_x_positions[c_idx]
        col_w = col_widths[c_idx]

        # Configurar recorte a la celda
        cell_rect = pygame.Rect(col_x + 2, y, col_w - 4, header_h)
        surface.set_clip(cell_rect)
        c_title = font.render(str(col_name), True, (0, 230, 255))
        surface.blit(c_title, (col_x + 6, y + 5))
        surface.set_clip(old_clip)

        # Línea divisoria vertical de columna
        if c_idx < num_cols - 1:
            pygame.draw.line(surface, (40, 60, 90), (col_x + col_w, y), (col_x + col_w, y + h - 16), 1)

    # 2. Filas de Datos (Celdas tipo Excel / Base de datos)
    for r_idx, row in enumerate(visible_rows):
        cur_y = y + header_h + 1 + (r_idx * row_h)
        
        # Rayado de cebra
        row_bg = (16, 22, 34) if r_idx % 2 == 0 else (21, 28, 44)
        pygame.draw.rect(surface, row_bg, (x + 1, cur_y, w - 2, row_h))
        
        # Línea divisoria horizontal entre filas
        pygame.draw.line(surface, (30, 42, 65), (x + 1, cur_y + row_h), (x + w - 1, cur_y + row_h), 1)

        # Número de fila (# 1, # 2, ...)
        r_num = font.render(str(r_idx + 1), True, (100, 120, 150))
        surface.blit(r_num, (x + 6, cur_y + 2))

        # Valores de celda
        for c_idx, val in enumerate(row):
            if c_idx >= num_cols:
                break
            col_x = col_x_positions[c_idx]
            col_w = col_widths[c_idx]
            
            if val is None:
                val_surf = font.render("NULL", True, (255, 120, 100))
            elif isinstance(val, float):
                val_surf = font.render(f"{val:.1f}", True, (160, 240, 180))
            else:
                val_surf = font.render(str(val), True, (230, 240, 250))
            
            cell_rect = pygame.Rect(col_x + 2, cur_y, col_w - 4, row_h)
            surface.set_clip(cell_rect)
            surface.blit(val_surf, (col_x + 6, cur_y + 2))
            surface.set_clip(old_clip)

    # 3. Barra de Estado inferior (Footer informativo)
    footer_y = y + h - 16
    pygame.draw.rect(surface, (18, 25, 40), (x + 1, footer_y, w - 2, 15))
    pygame.draw.line(surface, (45, 65, 95), (x, footer_y), (x + w, footer_y), 1)
    
    total_rows = len(rows)
    footer_txt = f"Mostrando {len(visible_rows)} de {total_rows} fila(s)  |  {num_cols} columna(s)"
    if total_rows > max_rows:
        footer_txt += f"  (▼ {total_rows - max_rows} más ocultas)"
    f_surf = font.render(footer_txt, True, COLOR_AMBER)
    surface.blit(f_surf, (x + 8, footer_y + 1))
