"""Panel flotante de misiones y objetivos actuales del jugador"""
import math
import pygame
from game.rendering import draw, make_font
from game.ui_helpers import draw_fitted_text
from game.visuals import panel, draw_pixel_icon, GOLD, MINT, MUTED, TEXT, CRIMSON, EMERALD, AZURE


class MissionsOverlay:
    def __init__(self):
        self.active = False
        self.rect = pygame.Rect(266, 10, 24, 17)
        self.font_title = make_font(13)
        self.font_item = make_font(11)
        self.font_sub = make_font(9)

    def toggle(self):
        self.close() if self.active else self.open()

    def open(self):
        self.active = True
        if hasattr(self,'save'):
            records=self.save.data.setdefault('seen_missions',{})
            records[self.context]=sorted(set(records.get(self.context,[]))|set(self.current_titles))
            self.save.save()

    def close(self):
        self.active = False

    def handle_event(self, event, current_state):
        if event.type == pygame.KEYDOWN:
            if self.active and event.key == pygame.K_ESCAPE:
                self.close()
                return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.toggle()
                return True
            if self.active:
                box_rect = pygame.Rect(90, 34, 300, 230)
                if not box_rect.collidepoint(event.pos):
                    self.close()
                    return True
        return False

    def get_missions(self, current_state, curriculum, foundations, save):
        if current_state == 'foundations':
            lecture = bool(foundations.state.get('lectures', {}).get(str(foundations.day)))
            record = foundations.state.get('kashut', {}).get(str(foundations.day), {})
            quiz = bool(record.get('complete'))
            reviewed = bool(record.get('reviewed'))
            missions=[('Hablar con Marco para empezar la clase',lecture,'Acércate al profesor junto a la pizarra')]
            workshop=foundations.task_checklist()['is_complete']
            if lecture:
                missions.append(('Ir al computador para hacer Kashut',quiz,'En tu PC, pulsa Kashut para responder'))
            if quiz:
                missions.append(('Revisar las respuestas',reviewed,'Termina el repaso o sal del podio si acertaste todas'))
            if reviewed and foundations.day>1:
                missions.append(('Tarea del modelador',workshop,'Crea el modelo en tu computador, revisa Tarea'))
            ready=lecture and quiz and reviewed and workshop
        elif current_state == 'game':
            lecture = curriculum.lecture_done_for_day
            exam = curriculum.current_day == 5
            work = curriculum.exam_finished if exam else curriculum.day_task_completed
            if exam:
                subtitle = f'{len(curriculum.get_current_exam_questions())} desafíos, puedes probar antes de entregar'
            else:
                total = curriculum.get_total_tasks_today()
                done = total if work else curriculum.current_task_idx
                subtitle = f'{done}/{total} ejercicios terminados, revisa el objetivo en tu PC'
            missions=[('Clase con Marco',lecture,'Habla con el profesor antes del laboratorio')]
            if lecture:missions.append(('Prueba de la semana' if exam else 'Ejercicios SQL',work,subtitle))
            ready = lecture and work
        else:
            return []
        if ready:
            missions.append(('Hablar con Marco para cerrar la jornada', False, 'Vuelve a su escritorio para continuar'))
        return missions

    def has_pending(self, current_state, curriculum, foundations, save):
        context=f'intro_{foundations.day}' if current_state=='foundations' else f'career_{curriculum.current_year}_{curriculum.current_day}'
        seen=save.data.get('seen_missions',{}).get(context,[])
        return any(not done and title not in seen for title,done,_ in self.get_missions(current_state,curriculum,foundations,save))

    def draw_button(self, surface, current_state, curriculum, foundations, save):
        self.save=save
        self.context=f'intro_{foundations.day}' if current_state=='foundations' else f'career_{curriculum.current_year}_{curriculum.current_day}'
        self.current_titles=[title for title,_,_ in self.get_missions(current_state,curriculum,foundations,save)]
        if self.active and self.has_pending(current_state,curriculum,foundations,save):self.open()
        pending = self.has_pending(current_state, curriculum, foundations, save)
        p = (math.sin(pygame.time.get_ticks() / 140.0) + 1.0) * 0.5 if pending else 0
        fill = (38, 30, 16) if pending else (24, 34, 46)
        accent = GOLD if pending else MUTED
        if pending:
            fill = tuple(round(x + (y - x) * 0.3 * p) for x, y in zip(fill, accent))

        panel(surface, self.rect, fill=fill, accent=accent, shadow=True, radius=3, selected=self.active)
        draw_pixel_icon(surface, "!", self.rect.centerx, self.rect.centery, GOLD if pending else TEXT)

    def draw_overlay(self, surface, current_state, curriculum, foundations, save):
        if not self.active:
            return

        box_rect = pygame.Rect(90, 34, 300, 232)
        # Fondo oscuro semitransparente que no estorba
        overlay = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        overlay.fill((10, 16, 26, 228))
        surface.blit(overlay, box_rect.topleft)

        draw.rect(surface, GOLD, box_rect, 1, border_radius=4)
        draw.rect(surface, (20, 32, 48), (box_rect.x + 2, box_rect.y + 2, box_rect.width - 4, 22), border_radius=3)
        draw_pixel_icon(surface, "!", box_rect.x + 12, box_rect.y + 13, GOLD)

        title_surf = self.font_title.render("MISIONES Y OBJETIVOS", True, GOLD)
        surface.blit(title_surf, (box_rect.x + 22, box_rect.y + 5))

        missions = self.get_missions(current_state, curriculum, foundations, save)
        y = box_rect.y + 30

        for title, is_done, sub in missions[:5]:
            draw.rect(surface, (15, 24, 36), (box_rect.x + 8, y, box_rect.width - 16, 34), border_radius=2)
            border_c = EMERALD if is_done else ((60, 90, 120) if not sub.startswith("¡") else GOLD)
            draw.rect(surface, border_c, (box_rect.x + 8, y, box_rect.width - 16, 34), 1, border_radius=2)

            # Casilla de estado
            box_sq = pygame.Rect(box_rect.x + 12, y + 10, 14, 14)
            draw.rect(surface, (18, 30, 42), box_sq, border_radius=2)
            draw.rect(surface, border_c, box_sq, 1, border_radius=2)
            if is_done:
                draw_pixel_icon(surface, "check", box_sq.centerx, box_sq.centery, EMERALD)
            else:
                draw_pixel_icon(surface, "!", box_sq.centerx, box_sq.centery, GOLD if not is_done else MUTED)

            t_color = (200, 245, 220) if is_done else TEXT
            draw_fitted_text(surface,title,pygame.Rect(box_rect.x+32,y+3,box_rect.width-42,14),self.font_item,t_color,padding=0)
            draw_fitted_text(surface,sub,pygame.Rect(box_rect.x+32,y+17,box_rect.width-42,14),self.font_sub,MUTED,padding=0)
            y += 37

        # Pie con atajo para cerrar
        draw.rect(surface, (16, 26, 38), (box_rect.x + 8, box_rect.bottom - 20, box_rect.width - 16, 16), border_radius=2)
        hint_surf = self.font_sub.render("Clic fuera del panel o Esc para cerrar", True, MUTED)
        surface.blit(hint_surf, (box_rect.centerx - hint_surf.get_width() // 2, box_rect.bottom - 18))
