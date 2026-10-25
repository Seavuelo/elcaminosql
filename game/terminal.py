from game.visuals import panel, button, GOLD, MINT, MUTED
import pygame
from game.rendering import draw, make_font, draw_caret
from game.constants import *
from game.ui_helpers import draw_panel, draw_sql_grid_table, render_wrapped_text, fit_text, draw_fitted_text, fitted_text_layout
from game.dialog import DialogBox
from game.sql_syntax import draw_sql, sql_width
from game.sql_editor import SQLBuffer

class SQLTerminal:
    def __init__(self, db_manager, audio_manager, curriculum):
        self.db = db_manager
        self.audio = audio_manager
        self.curriculum = curriculum
        self.active = False

        # Editor de consulta
        self.input_text = "SELECT * FROM estudiantes;"
        self.cursor_pos = len(self.input_text)
        self.history = ["SELECT * FROM estudiantes;"]
        self.history_index = 0

        # Resultados
        self.last_result = None
        self.feedback_message = None
        self.feedback_is_success = False

        # Visor de Tablas del Esquema
        self.show_schema = False
        self.schema_tabs = ["estudiantes", "materias", "notas_parcial", "profesores"]
        self.current_tab_idx = 0
        self.tab_cache = {}

        # Fuentes compactas y nítidas
        self.font_header = make_font(14)
        self.font_code = make_font(13)
        self.font_table = make_font(12)
        self.font_msg = make_font(12)
        self.font_hint = make_font(11)

        self.request_notebook = False
        self.details = DialogBox(audio_manager)
        self.repeat_key = None
        self.repeat_elapsed = 0.0
        self.caret_visible_until = 0
        self.buffer = SQLBuffer()
        self.editor_scroll = 0
        self.hint_levels = {}
        self.repeat_mod = 0
        self.editor_rect = None
        self.editor_scroll_x = 0

    def open(self):
        self.active = True
        self.repeat_key = None
        self.show_schema = False
        self.tab_cache.clear()
        if self.curriculum.current_day == 5 and not self.curriculum.exam_finished:
            self.feedback_message = "CTRL+ENTER: probar, CTRL+SHIFT+ENTER: entregar, ENTER: nueva línea, Se aprueba con 3 de 5 aciertos."
            self.feedback_is_success = True
        self.audio.play_key()
        # Actualizar pestañas por si el estudiante creó una tabla en Año 2
        schema_dict = self.db.get_schema()
        self.schema_tabs = list(schema_dict.keys())
        if not self.schema_tabs:
            self.schema_tabs = ["estudiantes", "materias", "notas_parcial", "profesores"]
        self.current_tab_idx = min(self.current_tab_idx, len(self.schema_tabs) - 1)

    def close(self):
        self.active = False
        self.repeat_key = None

    def update(self, dt, enabled=True):
        if not enabled or not self.active or self.details.active:
            self.repeat_key = None
            return
        if self.repeat_key is not None:
            self.repeat_elapsed += dt
            while self.repeat_elapsed >= 0:
                self.repeat_elapsed -= 0.04
                self.handle_event(pygame.event.Event(pygame.KEYDOWN, key=self.repeat_key, unicode="", mod=self.repeat_mod))

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type == pygame.KEYUP and event.key == self.repeat_key:
            self.repeat_key = None
            return True
        if event.type == pygame.WINDOWFOCUSLOST:
            self.repeat_key = None
            return False
        if event.type == pygame.KEYDOWN:
            self.caret_visible_until = pygame.time.get_ticks() + 500
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_BACKSPACE, pygame.K_DELETE):
                if self.repeat_key != event.key:
                    self.repeat_key = event.key
                    self.repeat_elapsed = -0.3
        if self.details.active:
            self.details.handle_event(event)
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F6:
            if self.last_result and self.last_result.get("success"):
                text = " | ".join(self.last_result['columns'])
                text += "\n\n" + "\n\n".join(f"Fila {index}\n" + "\n".join(f"{name}: {'NULL' if value is None else value}" for name,value in zip(self.last_result['columns'],row)) for index,row in enumerate(self.last_result['rows'],1))
                self.details.show("Resultado completo",text,speaker="SQLite")
                self.repeat_key = None
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
            if self.show_schema and self.schema_tabs:
                name = self.schema_tabs[self.current_tab_idx]
                quoted = name.replace('"', '""')
                result = self.tab_cache.get(name) or self.db.execute_query(f'SELECT * FROM "{quoted}" LIMIT 10')
                text = f"Tabla: {name}"
                if result.get("success"):
                    for index, row in enumerate(result["rows"], 1):
                        text += f"\n\nFila {index}\n" + "\n".join(
                            f"{column}: {'NULL' if value is None else value}"
                            for column, value in zip(result["columns"], row))
                else:
                    text += "\n" + result.get("error", "No se pudo consultar la tabla")
                self.details.show("Datos completos", text, speaker="Catálogo")
                return True
            task = (self.curriculum.get_current_exam_question() if self.curriculum.current_day == 5
                    else self.curriculum.get_current_task())
            text = task.objective if task else "Jornada completada."
            if task and self.curriculum.current_day < 5:
                key = (task.year, task.day, task.task_idx)
                level = min(3, self.hint_levels.get(key, 0) + 1)
                self.hint_levels[key] = level
                text += f"\n\nPista {level}/3\n{task.progressive_hint(level)}"
                if level == 3 and not task.is_write:
                    reference = self.db.execute_query(task.canonical_query)
                    if reference.get("success"):
                        text += "\n\nResultado calculado en tu base\n" + " | ".join(reference["columns"])
                        text += "\n" + "\n".join(" | ".join("NULL" if value is None else str(value) for value in row) for row in reference["rows"])
            if self.feedback_message:
                text += f"\n\n{self.feedback_message}"
            self.repeat_key = None
            self.details.show("Texto completo", text, speaker="Terminal")
            return True

        # Abrir Cuaderno de Apuntes con F1 o clic en la pestaña física
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            self.request_notebook = True
            self.audio.play_key()
            return True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            tab_r = pygame.Rect(12 + 456 - 86, 8 + 2, 82, 17)
            if tab_r.collidepoint(event.pos):
                self.request_notebook = True
                self.audio.play_key()
                return True
            if not self.show_schema and self.editor_rect and self.editor_rect.collidepoint(event.pos):
                lines = self.input_text.split("\n")
                row = min(len(lines)-1, self.editor_scroll + (event.pos[1]-self.editor_rect.y)//(self.font_code.get_linesize()+1))
                x = event.pos[0]-self.editor_rect.x+self.editor_scroll_x
                col = min(range(len(lines[row])+1), key=lambda i: abs(sql_width(lines[row][:i],self.font_code)-x))
                self.cursor_pos = sum(len(line)+1 for line in lines[:row])+col
                self.buffer.anchor = None
                self.caret_visible_until = pygame.time.get_ticks()+500
                return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return True

            elif event.key == pygame.K_F2:
                self.show_schema = not self.show_schema
                self.audio.play_key()
                return True

            if self.show_schema:
                if pygame.K_1 <= event.key <= pygame.K_9:
                    idx = event.key - pygame.K_1
                    if idx < len(self.schema_tabs):
                        self.current_tab_idx = idx
                        self.audio.play_key()
                    return True
                elif event.key == pygame.K_LEFT:
                    self.current_tab_idx = (self.current_tab_idx - 1) % len(self.schema_tabs)
                    self.audio.play_key()
                    return True
                elif event.key == pygame.K_RIGHT:
                    self.current_tab_idx = (self.current_tab_idx + 1) % len(self.schema_tabs)
                    self.audio.play_key()
                    return True
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    self.show_schema = False
                    return True
                return True

            # Enter edita, ejecutar y entregar requieren acciones diferentes
            mod = getattr(event, "mod", 0)
            ctrl, shift = bool(mod & pygame.KMOD_CTRL), bool(mod & pygame.KMOD_SHIFT)
            if event.key == pygame.K_F5 or (event.key == pygame.K_RETURN and ctrl):
                self.execute(submit=self.curriculum.current_day != 5 or (ctrl and shift))
                return True
            if ctrl and event.key == pygame.K_a:
                self.buffer.anchor, self.cursor_pos = 0, len(self.input_text)
                return True
            if ctrl and event.key in (pygame.K_c, pygame.K_x, pygame.K_v):
                try:
                    if not pygame.scrap.get_init():
                        pygame.scrap.init()
                    start, end = self.buffer.selection(self.cursor_pos)
                    if event.key == pygame.K_v:
                        value = pygame.scrap.get(pygame.SCRAP_TEXT)
                        if value:
                            self.input_text, self.cursor_pos = self.buffer.replace(self.input_text, self.cursor_pos, value.rstrip(b"\0").decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n").expandtabs(4))
                    elif start != end:
                        pygame.scrap.put(pygame.SCRAP_TEXT, self.input_text[start:end].encode("utf-8") + b"\0")
                        if event.key == pygame.K_x:
                            self.input_text, self.cursor_pos = self.buffer.replace(self.input_text, self.cursor_pos, "")
                except pygame.error:
                    self.feedback_message = "No se pudo acceder al portapapeles"
                return True
            if event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                if self.history:
                    step = -1 if event.key == pygame.K_PAGEUP else 1
                    self.history_index = min(len(self.history), max(0, self.history_index + step))
                    self.input_text = self.history[self.history_index] if self.history_index < len(self.history) else ""
                    self.cursor_pos = len(self.input_text)
                    self.buffer.anchor = None
                return True
            movements = {pygame.K_LEFT: "left", pygame.K_RIGHT: "right", pygame.K_UP: "up", pygame.K_DOWN: "down", pygame.K_HOME: "home", pygame.K_END: "end"}
            if event.key in movements:
                self.cursor_pos = self.buffer.move(self.input_text, self.cursor_pos, movements[event.key], shift, ctrl)
                return True
            if event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                start, end = self.buffer.selection(self.cursor_pos)
                if start == end:
                    if event.key == pygame.K_BACKSPACE:
                        self.buffer.anchor = max(0, self.cursor_pos - 1)
                    else:
                        self.buffer.anchor = min(len(self.input_text), self.cursor_pos + 1)
                self.input_text, self.cursor_pos = self.buffer.replace(self.input_text, self.cursor_pos, "")
                return True
            if event.key == pygame.K_RETURN:
                line = self.input_text[self.input_text.rfind("\n", 0, self.cursor_pos) + 1:self.cursor_pos]
                value = "\n" + line[:len(line) - len(line.lstrip(" "))]
            elif event.key == pygame.K_TAB:
                value = "    "
            elif not ctrl and event.unicode and event.unicode.isprintable():
                value = event.unicode
            else:
                return False
            self.input_text, self.cursor_pos = self.buffer.replace(self.input_text, self.cursor_pos, value)
            self.audio.play_key()
            return True

        return False

    def execute(self, submit=True):
        query = self.input_text.strip()
        if not query:
            return

        if not self.history or self.history[-1] != query:
            self.history.append(query)
        self.history_index = len(self.history)

        exam = self.curriculum.current_day == 5
        question = self.curriculum.get_current_exam_question() if exam else None
        task = self.curriculum.get_current_task()
        allow_write = bool(question and question.is_write) if exam else bool(
            task and task.is_write and not self.curriculum.day_task_completed)
        expected_query = (task.canonical_query if task and task.is_write
                          and not self.curriculum.day_task_completed else None)
        if question and question.is_write:
            expected_query = question.canonical_query
        result = self.db.execute_query(query, allow_write=allow_write,
                                       expected_query=expected_query, commit=not exam or submit)
        self.last_result = result

        # Invalidar caché de pestañas si hubo modificación
        if result["success"]:
            self.tab_cache.clear()
            self.schema_tabs = list(self.db.get_schema().keys())
            self.current_tab_idx = min(self.current_tab_idx, max(0, len(self.schema_tabs) - 1))

        if not result["success"]:
            if exam and submit and result.get("validation_failed"):
                is_done, approved = self.curriculum.advance_exam_question(False)
                self.feedback_is_success = approved if is_done else False
                self.feedback_message = (f"Examen finalizado. Nota: {self.curriculum.exam_final_grade:.1f}. Habla con Marco."
                                         if is_done else "Entrega incorrecta. Cambios deshechos; continúa con la siguiente pregunta.")
                self.audio.play_error()
                return
            self.audio.play_error()
            self.feedback_is_success = False
            raw_err = result.get("error", "Error desconocido")

            # Ayuda pedagógica para errores comunes
            err_lower = raw_err.lower()
            if 'near "from"' in err_lower or "syntax error" in err_lower and "from" in err_lower:
                tip = " (Pista: ¿Pusiste una coma justo antes de FROM? En SQL no debe haber coma al final de las columnas)."
            elif "no such column" in err_lower:
                tip = " (Pista: Una columna no existe. Pulsa [F2] para revisar el nombre exacto de las columnas)."
            elif "no such table" in err_lower:
                tip = " (Pista: La tabla no existe. Pulsa [F2] para consultar el esquema de la base de datos)."
            elif "incomplete input" in err_lower:
                tip = " (Pista: Revisa si olvidaste cerrar una comilla simple o un paréntesis)."
            else:
                tip = ""

            self.feedback_message = f"Error SQL: {raw_err}{tip}"
            return

        if exam and not submit:
            self.feedback_message = "Prueba sin nota. Revisa el resultado; CTRL+SHIFT+ENTER entrega tu respuesta definitiva"
            self.feedback_is_success = True
            return

        # Días 1 al 4: Tareas Diarias (Múltiples ejercicios por día)
        if self.curriculum.current_day <= 4:
            if not self.curriculum.day_task_completed:
                task = self.curriculum.get_current_task()
                if task:
                    is_valid, msg = task.validate(self.db, result, user_query=query)
                    if is_valid:
                        self.audio.play_success()
                        is_day_done, next_task = self.curriculum.advance_daily_task()
                        self.feedback_is_success = True
                        if is_day_done:
                            self.feedback_message = "¡EXCELENTE! Has completado todos los ejercicios de hoy. Sal con [ESC] y habla con el Profesor Marco para finalizar la jornada."
                        else:
                            curr_idx = self.curriculum.current_task_idx + 1
                            total = self.curriculum.get_total_tasks_today()
                            self.feedback_message = f"¡CORRECTO! (Completado {curr_idx - 1} de {total}). Siguiente reto: {next_task.title}"
                        if self.curriculum.last_xp_award:
                            self.feedback_message = f"+{self.curriculum.last_xp_award} XP · {self.feedback_message}"
                    else:
                        self.audio.play_error()
                        self.feedback_is_success = False
                        self.feedback_message = f"Revisa tu consulta: {msg}"
            else:
                self.audio.play_key()
                self.feedback_is_success = True
                self.feedback_message = f"¡Jornada de hoy completada! Pulsa [ESC] para salir del PC y habla con el Profesor Marco."
        else:
            # Día 5: Examen
            q = self.curriculum.get_current_exam_question()
            if q and not self.curriculum.exam_finished:
                is_valid, msg = q.validate(self.db, result)
                if is_valid:
                    self.audio.play_success()
                    is_done, approved = self.curriculum.advance_exam_question(was_correct=True)
                    if is_done:
                        self.feedback_is_success = approved
                        nota = self.curriculum.exam_final_grade
                        status_str = "¡APROBADO!" if approved else "REPROBADO"
                        self.feedback_message = f"¡Examen finalizado! Nota: {nota:.1f} ({status_str}). Sal con [ESC] y habla con Marco."
                    else:
                        next_q = self.curriculum.get_current_exam_question()
                        self.feedback_is_success = True
                        self.feedback_message = f"¡Pregunta correcta! Siguiente: {next_q.title}"
                else:
                    self.audio.play_error()
                    is_done, approved = self.curriculum.advance_exam_question(was_correct=False)
                    self.feedback_is_success = False
                    if is_done:
                        nota = self.curriculum.exam_final_grade
                        self.feedback_is_success = approved
                        self.feedback_message = f"Examen finalizado. Nota: {nota:.1f}. Sal con [ESC] y habla con Marco."
                    else:
                        next_q = self.curriculum.get_current_exam_question()
                        self.feedback_message = f"Respuesta incorrecta: {msg} Siguiente: {next_q.title}"

    def draw(self, surface, tick):
        if not self.active:
            return

        tx, ty, tw, th = 12, 8, 456, 284

        panel_rect = pygame.Rect(tx, ty, tw, th)
        draw_panel(surface, panel_rect, bg_color=(10, 14, 22, 250), border_color=(0, 229, 255), border_width=2,
                   title=f"SQL | Año {self.curriculum.current_year} Día {self.curriculum.current_day}",
                   font=self.font_header, title_color=(0, 229, 255))

        # Pestaña física estilo libreta de apuntes en el borde superior derecho
        tab_r = pygame.Rect(tx + tw - 86, ty + 2, 82, 17)
        draw.rect(surface, (180, 135, 75), tab_r, border_radius=3)
        draw.rect(surface, (248, 245, 235), (tab_r.x + 8, tab_r.y + 1, tab_r.width - 9, tab_r.height - 2), border_radius=2)
        for sy in [tab_r.y + 4, tab_r.y + 8, tab_r.y + 12]:
            draw.circle(surface, (70, 70, 80), (tab_r.x + 4, sy), 2)
            draw.circle(surface, (230, 230, 240), (tab_r.x + 4, sy), 1)
        nb_txt = self.font_hint.render("Apuntes", True, (30, 45, 70))
        surface.blit(nb_txt, (tab_r.x + 11, tab_r.y + 3))

        if self.show_schema:
            self._draw_schema_inspector(surface, tx, ty, tw, th)
            if self.details.active:
                self.details.draw(surface)
            return

        # 1. Panel de Tarea o Examen Activo (Con Word-Wrap)
        top_box_y = ty + 25
        top_box_h = 64
        top_rect = pygame.Rect(tx + 8, top_box_y, tw - 16, top_box_h)

        if self.curriculum.current_day <= 4:
            if self.curriculum.day_task_completed:
                # Banner verde de felicitaciones y aviso claro de salida
                draw.rect(surface, (12, 38, 24), top_rect)
                draw.rect(surface, (0, 255, 136), top_rect, 1)
                done_title = self.font_header.render("✓ ¡TODOS LOS EJERCICIOS DEL DÍA COMPLETADOS!", True, (0, 255, 136))
                surface.blit(done_title, (tx + 14, top_box_y + 4))
                done_sub = self.font_table.render("Presiona [ESC] para salir del PC e interactúa con el Profesor Marco [E] para avanzar.", True, COLOR_WHITE)
                surface.blit(done_sub, (tx + 14, top_box_y + 24))
            else:
                task = self.curriculum.get_current_task()
                if task:
                    panel(surface,top_rect,(23,37,50),GOLD,shadow=False)

                    curr_idx = self.curriculum.current_task_idx + 1
                    total = self.curriculum.get_total_tasks_today()
                    status_badge = f"[Progreso: {curr_idx}/{total}]"
                    t_title = self.font_header.render(fit_text(task.title, self.font_header, tw - 32), True, COLOR_AMBER)
                    surface.blit(t_title, (tx + 14, top_box_y + 3))

                    obj_rect = pygame.Rect(tx + 14, top_box_y + 17, tw - 32, 44)
                    render_wrapped_text(surface, task.objective, obj_rect, self.font_table, color=COLOR_WHITE, line_spacing=1, padding=0)
        else:
            panel(surface,top_rect,(23,37,50),GOLD,shadow=False)
            q = self.curriculum.get_current_exam_question()
            if q and not self.curriculum.exam_finished:
                e_title = self.font_header.render(fit_text(f"{q.q_num}/{len(self.curriculum.get_current_exam_questions())}: {q.title}", self.font_header, tw - 32), True, COLOR_AMBER)
                surface.blit(e_title, (tx + 14, top_box_y + 3))
                obj_rect = pygame.Rect(tx + 14, top_box_y + 17, tw - 32, 44)
                render_wrapped_text(surface, q.objective, obj_rect, self.font_table, color=COLOR_WHITE, line_spacing=1, padding=0)
            else:
                nota = self.curriculum.exam_final_grade
                status_txt = "¡AÑO APROBADO!" if nota >= 4.0 else "AÑO REPROBADO (Debes repetir año)"
                col = COLOR_GREEN if nota >= 4.0 else COLOR_RED
                e_title = self.font_header.render(f"RESULTADO: NOTA {nota:.1f} - {status_txt}", True, col)
                surface.blit(e_title, (tx + 14, top_box_y + 5))
                hint_end = self.font_table.render("Cierra la terminal [ESC] y habla con el Profesor Marco.", True, COLOR_WHITE)
                surface.blit(hint_end, (tx + 14, top_box_y + 24))

        # 2. Caja de Entrada SQL
        input_y = top_box_y + top_box_h + 6
        input_h = 62
        panel(surface,pygame.Rect(tx+8,input_y,tw-16,input_h),(13,25,37),MINT,shadow=False)

        input_rect = pygame.Rect(tx + 32, input_y + 3, tw - 46, input_h - 14)
        self.editor_rect = input_rect
        lines = self.input_text.split("\n")
        row = self.input_text[:self.cursor_pos].count("\n")
        column = self.cursor_pos - (self.input_text.rfind("\n", 0, self.cursor_pos) + 1)
        line_h = self.font_code.get_linesize() + 1
        visible_rows = max(1, input_rect.height // line_h)
        self.editor_scroll = min(self.editor_scroll, row)
        self.editor_scroll = max(self.editor_scroll, row - visible_rows + 1)
        cursor_offset = sql_width(lines[row][:column], self.font_code)
        scroll_x = max(0, cursor_offset - input_rect.width + 4)
        self.editor_scroll_x = scroll_x
        old_clip = surface.get_clip()
        surface.set_clip(old_clip.clip(input_rect))
        selection_start, selection_end = self.buffer.selection(self.cursor_pos)
        offset = sum(len(line) + 1 for line in lines[:self.editor_scroll])
        for idx in range(self.editor_scroll, min(len(lines), self.editor_scroll + visible_rows)):
            line = lines[idx]
            y = input_rect.y + (idx - self.editor_scroll) * line_h
            if idx == row:
                draw.rect(surface, (24, 38, 52), (input_rect.x,y,input_rect.width,line_h))
            a, b = max(0,selection_start-offset), min(len(line),selection_end-offset)
            if b > a:
                left = sql_width(line[:a], self.font_code)
                width = sql_width(line[:b], self.font_code) - left
                draw.rect(surface, (50,75,110), (input_rect.x+left-scroll_x,y,width,line_h))
            offset += len(line)+1
        draw_sql(surface, self.input_text, (input_rect.x-scroll_x, input_rect.y-self.editor_scroll*line_h), self.font_code)
        if (tick // 30) % 2 == 0 or pygame.time.get_ticks() < self.caret_visible_until:
            draw_caret(surface, input_rect.x+cursor_offset-scroll_x, input_rect.y+(row-self.editor_scroll)*line_h+1, max(2,self.font_code.get_height()-2), (0,255,136))
        surface.set_clip(old_clip)
        surface.blit(self.font_hint.render(f'{row+1}:{column+1}',True,MUTED),(tx+13,input_y+input_h-10))
        # 3. Mensaje de Feedback
        fb_y = input_y + input_h + 4
        fb_h = 28
        if self.feedback_message:
            fb_rect = pygame.Rect(tx + 8, fb_y, tw - 16, fb_h)
            fb_bg = (15, 30, 22) if self.feedback_is_success else (35, 16, 20)
            fb_border = COLOR_GREEN if self.feedback_is_success else COLOR_RED
            panel(surface,fb_rect,fb_bg,fb_border,shadow=False)
            render_wrapped_text(surface, self.feedback_message, fb_rect, self.font_msg, color=fb_border, padding=4)

        # 4. Tabla Visual Data Grid
        grid_y = fb_y + fb_h + 4
        grid_h = th - (grid_y - ty) - 8
        grid_rect = pygame.Rect(tx + 8, grid_y, tw - 16, grid_h)

        if self.last_result and self.last_result.get("success"):
            cols = self.last_result.get("columns", [])
            rows = self.last_result.get("rows", [])
            draw_sql_grid_table(surface, grid_rect, cols, rows, font=self.font_table, max_rows=6)
        else:
            panel(surface,grid_rect,(14,25,37),MINT,shadow=False)
            hint_txt = "Escribe tu consulta SQL arriba y pulsa [CTRL+ENTER] para ejecutarla en la base de datos real."
            render_wrapped_text(surface,hint_txt,grid_rect.inflate(-20,-12),self.font_table,color=MUTED,padding=0)

        if self.details.active:
            self.details.draw(surface)

    def _draw_schema_inspector(self, surface, tx, ty, tw, th):
        box_y = ty + 26
        box_h = th - 34
        inspector_rect = pygame.Rect(tx + 8, box_y, tw - 16, box_h)
        panel(surface,inspector_rect,(18,30,44),MINT,shadow=False)

        if not self.schema_tabs:
            return
        per_row = min(5, len(self.schema_tabs))
        tab_w = (tw - 24) // per_row
        tab_row_h = 24
        for i, name in enumerate(self.schema_tabs):
            tab_font, lines = fitted_text_layout(f"[{i + 1}] {name}", self.font_table, tab_w - 12)
            tab_row_h = max(tab_row_h, len(lines) * tab_font.get_linesize() + 8)
        tab_rows = (len(self.schema_tabs) + per_row - 1) // per_row
        tab_bar_h = tab_row_h * tab_rows
        draw.rect(surface, (20, 28, 44), (tx + 9, box_y + 1, tw - 18, tab_bar_h))
        for i, t_name in enumerate(self.schema_tabs):
            tab_x = tx + 12 + (i % per_row) * tab_w
            tab_y = box_y + (i // per_row) * tab_row_h
            is_active = i == self.current_tab_idx
            rect = pygame.Rect(tab_x, tab_y + 2, tab_w - 4, tab_row_h - 2)
            button(surface,t_name,rect,self.font_table,selected=is_active,accent=MINT)
            if is_active:
                draw.line(surface, COLOR_AMBER, (rect.left, rect.bottom), (rect.right, rect.bottom), 1)

        sel_table = self.schema_tabs[self.current_tab_idx]
        if sel_table not in self.tab_cache:
            quoted = sel_table.replace('"', '""')
            res = self.db.execute_query(f'SELECT * FROM "{quoted}" LIMIT 10;')
            self.tab_cache[sel_table] = res

        cached = self.tab_cache[sel_table]
        grid_rect = pygame.Rect(tx + 14, box_y + tab_bar_h + 8, tw - 28, box_h - tab_bar_h - 26)
        if cached.get("success"):
            draw_sql_grid_table(surface, grid_rect, cached["columns"], cached["rows"], font=self.font_table, max_rows=8)
