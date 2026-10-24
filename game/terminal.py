import pygame
from game.constants import *
from game.ui_helpers import draw_panel, draw_sql_grid_table, render_wrapped_text

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
        self.font_header = pygame.font.Font(None, 14)
        self.font_code = pygame.font.Font(None, 13)
        self.font_table = pygame.font.Font(None, 12)
        self.font_msg = pygame.font.Font(None, 12)
        self.font_hint = pygame.font.Font(None, 11)

        self.request_notebook = False

    def open(self):
        self.active = True
        self.show_schema = False
        self.audio.play_key()
        # Actualizar pestañas por si el estudiante creó una tabla en Año 2
        schema_dict = self.db.get_schema()
        self.schema_tabs = list(schema_dict.keys())
        if not self.schema_tabs:
            self.schema_tabs = ["estudiantes", "materias", "notas_parcial", "profesores"]
        self.current_tab_idx = min(self.current_tab_idx, len(self.schema_tabs) - 1)

    def close(self):
        self.active = False

    def handle_event(self, event):
        if not self.active:
            return False

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

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return True

            elif event.key == pygame.K_TAB:
                self.show_schema = not self.show_schema
                self.audio.play_key()
                return True

            if self.show_schema:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
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

            # Edición de texto SQL
            if event.key == pygame.K_RETURN:
                self.execute()
                return True

            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.input_text = self.input_text[:self.cursor_pos - 1] + self.input_text[self.cursor_pos:]
                    self.cursor_pos -= 1
                    self.audio.play_key()
                return True

            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.input_text):
                    self.input_text = self.input_text[:self.cursor_pos] + self.input_text[self.cursor_pos + 1:]
                    self.audio.play_key()
                return True

            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                return True

            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.input_text):
                    self.cursor_pos += 1
                return True

            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
                return True

            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.input_text)
                return True

            elif event.key == pygame.K_UP:
                if self.history and self.history_index > 0:
                    self.history_index -= 1
                    self.input_text = self.history[self.history_index]
                    self.cursor_pos = len(self.input_text)
                    self.audio.play_key()
                return True

            elif event.key == pygame.K_DOWN:
                if self.history and self.history_index < len(self.history) - 1:
                    self.history_index += 1
                    self.input_text = self.history[self.history_index]
                    self.cursor_pos = len(self.input_text)
                    self.audio.play_key()
                elif self.history_index == len(self.history) - 1:
                    self.history_index = len(self.history)
                    self.input_text = ""
                    self.cursor_pos = 0
                return True

            else:
                if event.unicode and event.unicode.isprintable():
                    self.input_text = self.input_text[:self.cursor_pos] + event.unicode + self.input_text[self.cursor_pos:]
                    self.cursor_pos += len(event.unicode)
                    self.audio.play_key()
                    return True

        return False

    def execute(self):
        query = self.input_text.strip()
        if not query:
            return

        if not self.history or self.history[-1] != query:
            self.history.append(query)
        self.history_index = len(self.history)

        allow_write = (self.curriculum.current_year >= 2)
        result = self.db.execute_query(query, allow_write=allow_write)
        self.last_result = result

        # Invalidar caché de pestañas si hubo modificación
        if allow_write and any(k in query.upper() for k in ["CREATE", "INSERT", "UPDATE", "DELETE"]):
            self.tab_cache.clear()
            self.schema_tabs = list(self.db.get_schema().keys())

        if not result["success"]:
            self.audio.play_error()
            self.feedback_is_success = False
            raw_err = result.get("error", "Error desconocido")
            
            # Ayuda pedagógica para errores comunes
            err_lower = raw_err.lower()
            if 'near "from"' in err_lower or "syntax error" in err_lower and "from" in err_lower:
                tip = " (Pista: ¿Pusiste una coma justo antes de FROM? En SQL no debe haber coma al final de las columnas)."
            elif "no such column" in err_lower:
                tip = " (Pista: Una columna no existe. Pulsa [TAB] para revisar el nombre exacto de las columnas)."
            elif "no such table" in err_lower:
                tip = " (Pista: La tabla no existe. Pulsa [TAB] para consultar el esquema de la base de datos)."
            elif "incomplete input" in err_lower:
                tip = " (Pista: Revisa si olvidaste cerrar una comilla simple o un paréntesis)."
            else:
                tip = ""

            self.feedback_message = f"Error SQL: {raw_err}{tip}"
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
                            self.feedback_message = "¡EXCELENTE! Has completado todos los ejercicios de hoy. Sal con [ESC] y habla con el Prof. Turing para finalizar la jornada."
                        else:
                            curr_idx = self.curriculum.current_task_idx + 1
                            total = self.curriculum.get_total_tasks_today()
                            self.feedback_message = f"¡CORRECTO! (Completado {curr_idx - 1} de {total}). Siguiente reto: {next_task.title}"
                    else:
                        self.audio.play_error()
                        self.feedback_is_success = False
                        self.feedback_message = f"Revisa tu consulta: {msg}"
            else:
                self.audio.play_key()
                self.feedback_is_success = True
                self.feedback_message = f"¡Jornada de hoy completada! Pulsa [ESC] para salir del PC y habla con el Profesor Turing."
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
                        self.feedback_message = f"¡Examen finalizado! Nota: {nota:.1f} ({status_str}). Sal con [ESC] y habla con Turing."
                    else:
                        next_q = self.curriculum.get_current_exam_question()
                        self.feedback_is_success = True
                        self.feedback_message = f"¡Pregunta correcta! Siguiente: {next_q.title}"
                else:
                    self.audio.play_error()
                    self.feedback_is_success = False
                    self.feedback_message = f"Respuesta incorrecta: {msg}"

    def draw(self, surface, tick):
        if not self.active:
            return

        tx, ty, tw, th = 12, 8, 456, 284

        year_str = f"AÑO {self.curriculum.current_year}/4 (DÍA {self.curriculum.current_day}/5)"
        panel_rect = pygame.Rect(tx, ty, tw, th)
        draw_panel(surface, panel_rect, bg_color=(10, 14, 22, 250), border_color=(0, 229, 255), border_width=2,
                   title=f"SQL TERMINAL  |  {year_str}  |  [TAB] Tablas  |  [ESC] Salir",
                   font=self.font_header, title_color=(0, 229, 255))

        # Pestaña física estilo libreta de apuntes en el borde superior derecho
        tab_r = pygame.Rect(tx + tw - 86, ty + 2, 82, 17)
        pygame.draw.rect(surface, (180, 135, 75), tab_r, border_radius=3)
        pygame.draw.rect(surface, (248, 245, 235), (tab_r.x + 8, tab_r.y + 1, tab_r.width - 9, tab_r.height - 2), border_radius=2)
        for sy in [tab_r.y + 4, tab_r.y + 8, tab_r.y + 12]:
            pygame.draw.circle(surface, (70, 70, 80), (tab_r.x + 4, sy), 2)
            pygame.draw.circle(surface, (230, 230, 240), (tab_r.x + 4, sy), 1)
        nb_txt = self.font_hint.render("[F1] Apuntes", True, (30, 45, 70))
        surface.blit(nb_txt, (tab_r.x + 11, tab_r.y + 3))

        if self.show_schema:
            self._draw_schema_inspector(surface, tx, ty, tw, th)
            return

        # 1. Panel de Tarea o Examen Activo (Con Word-Wrap)
        top_box_y = ty + 25
        top_box_h = 46
        top_rect = pygame.Rect(tx + 8, top_box_y, tw - 16, top_box_h)

        if self.curriculum.current_day <= 4:
            if self.curriculum.day_task_completed:
                # Banner verde de felicitaciones y aviso claro de salida
                pygame.draw.rect(surface, (12, 38, 24), top_rect)
                pygame.draw.rect(surface, (0, 255, 136), top_rect, 1)
                done_title = self.font_header.render("✓ ¡TODOS LOS EJERCICIOS DEL DÍA COMPLETADOS!", True, (0, 255, 136))
                surface.blit(done_title, (tx + 14, top_box_y + 4))
                done_sub = self.font_table.render("Presiona [ESC] para salir del PC e interactúa con el Prof. Turing [E] para avanzar.", True, COLOR_WHITE)
                surface.blit(done_sub, (tx + 14, top_box_y + 24))
            else:
                task = self.curriculum.get_current_task()
                if task:
                    pygame.draw.rect(surface, (18, 26, 40), top_rect)
                    pygame.draw.rect(surface, COLOR_AMBER, top_rect, 1)

                    curr_idx = self.curriculum.current_task_idx + 1
                    total = self.curriculum.get_total_tasks_today()
                    status_badge = f"[Progreso: {curr_idx}/{total}]"
                    t_title = self.font_header.render(f"{task.title}  {status_badge}", True, COLOR_AMBER)
                    surface.blit(t_title, (tx + 14, top_box_y + 3))

                    obj_rect = pygame.Rect(tx + 14, top_box_y + 17, tw - 32, 26)
                    render_wrapped_text(surface, task.objective, obj_rect, self.font_table, color=COLOR_WHITE, line_spacing=1, padding=0)
        else:
            pygame.draw.rect(surface, (18, 26, 40), top_rect)
            pygame.draw.rect(surface, COLOR_AMBER, top_rect, 1)
            q = self.curriculum.get_current_exam_question()
            if q and not self.curriculum.exam_finished:
                e_title = self.font_header.render(f"EXAMEN: {q.title}  (Aciertos: {self.curriculum.exam_score}/3)", True, COLOR_AMBER)
                surface.blit(e_title, (tx + 14, top_box_y + 3))
                obj_rect = pygame.Rect(tx + 14, top_box_y + 17, tw - 32, 26)
                render_wrapped_text(surface, q.objective, obj_rect, self.font_table, color=COLOR_WHITE, line_spacing=1, padding=0)
            else:
                nota = self.curriculum.exam_final_grade
                status_txt = "¡AÑO APROBADO!" if nota >= 4.0 else "AÑO REPROBADO (Debes repetir año)"
                col = COLOR_GREEN if nota >= 4.0 else COLOR_RED
                e_title = self.font_header.render(f"RESULTADO: NOTA {nota:.1f} - {status_txt}", True, col)
                surface.blit(e_title, (tx + 14, top_box_y + 5))
                hint_end = self.font_table.render("Cierra la terminal [ESC] y habla con el Profesor Turing.", True, COLOR_WHITE)
                surface.blit(hint_end, (tx + 14, top_box_y + 24))

        # 2. Caja de Entrada SQL
        input_y = top_box_y + top_box_h + 6
        input_h = 24
        pygame.draw.rect(surface, (14, 18, 28), (tx + 8, input_y, tw - 16, input_h))
        pygame.draw.rect(surface, (0, 255, 136), (tx + 8, input_y, tw - 16, input_h), 1)

        prompt_surf = self.font_code.render("sql>", True, (0, 255, 136))
        surface.blit(prompt_surf, (tx + 14, input_y + 5))

        text_surf = self.font_code.render(self.input_text, True, COLOR_WHITE)
        surface.blit(text_surf, (tx + 50, input_y + 5))

        if (tick // 30) % 2 == 0:
            cursor_offset = self.font_code.size(self.input_text[:self.cursor_pos])[0]
            pygame.draw.rect(surface, (0, 255, 136), (tx + 50 + cursor_offset, input_y + 5, 2, 14))

        # 3. Mensaje de Feedback
        fb_y = input_y + input_h + 4
        fb_h = 24
        if self.feedback_message:
            fb_rect = pygame.Rect(tx + 8, fb_y, tw - 16, fb_h)
            fb_bg = (15, 30, 22) if self.feedback_is_success else (35, 16, 20)
            fb_border = COLOR_GREEN if self.feedback_is_success else COLOR_RED
            pygame.draw.rect(surface, fb_bg, fb_rect)
            pygame.draw.rect(surface, fb_border, fb_rect, 1)
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
            pygame.draw.rect(surface, (12, 16, 25), grid_rect)
            pygame.draw.rect(surface, (40, 55, 80), grid_rect, 1)
            hint_txt = "Escribe tu consulta SQL arriba y pulsa [ENTER] para ejecutarla en la base de datos real."
            hint_surf = self.font_table.render(hint_txt, True, (110, 130, 160))
            surface.blit(hint_surf, (tx + 18, grid_y + 16))

    def _draw_schema_inspector(self, surface, tx, ty, tw, th):
        box_y = ty + 26
        box_h = th - 34
        inspector_rect = pygame.Rect(tx + 8, box_y, tw - 16, box_h)
        pygame.draw.rect(surface, (14, 20, 32), inspector_rect)
        pygame.draw.rect(surface, (0, 229, 255), inspector_rect, 1)

        tab_bar_h = 24
        pygame.draw.rect(surface, (20, 28, 44), (tx + 9, box_y + 1, tw - 18, tab_bar_h))
        pygame.draw.line(surface, (45, 65, 95), (tx + 8, box_y + tab_bar_h), (tx + tw - 8, box_y + tab_bar_h), 1)

        if not self.schema_tabs:
            return

        tab_w = max(45, (tw - 30) // len(self.schema_tabs))
        for i, t_name in enumerate(self.schema_tabs):
            tab_x = tx + 12 + (i * tab_w)
            is_active = (i == self.current_tab_idx)
            tab_bg = (30, 48, 76) if is_active else (18, 25, 38)
            pygame.draw.rect(surface, tab_bg, (tab_x, box_y + 3, tab_w - 4, tab_bar_h - 3))
            if is_active:
                pygame.draw.line(surface, COLOR_AMBER, (tab_x, box_y + tab_bar_h), (tab_x + tab_w - 4, box_y + tab_bar_h), 2)
            
            t_label = self.font_table.render(f"[{i + 1}] {t_name[:10]}", True, COLOR_AMBER if is_active else (160, 180, 210))
            surface.blit(t_label, (tab_x + 4, box_y + 7))

        sel_table = self.schema_tabs[self.current_tab_idx]
        if sel_table not in self.tab_cache:
            res = self.db.execute_query(f"SELECT * FROM {sel_table} LIMIT 10;")
            self.tab_cache[sel_table] = res

        cached = self.tab_cache[sel_table]
        grid_rect = pygame.Rect(tx + 14, box_y + tab_bar_h + 8, tw - 28, box_h - tab_bar_h - 26)
        if cached.get("success"):
            draw_sql_grid_table(surface, grid_rect, cached["columns"], cached["rows"], font=self.font_table, max_rows=8)

        hint_str = "Pulsa [1, 2, 3...] o [FLECHAS] para cambiar de tabla  |  [TAB] o [ENTER] para volver a la terminal"
        h_surf = self.font_hint.render(hint_str, True, COLOR_GRAY)
        surface.blit(h_surf, (tx + 18, box_y + box_h - 15))
