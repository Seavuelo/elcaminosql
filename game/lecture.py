from game.visuals import board, backdrop, marco_portrait, button, GOLD, MINT
import pygame
from game.rendering import draw, make_font
from game.constants import *
from game.sql_syntax import draw_sql
from game.lessons import slides_for
from game.ui_helpers import render_wrapped_text, draw_panel, paginate_text, fit_text, draw_sql_grid_table, draw_fitted_text

class LectureScene:
    """Escena interactiva de clase en la pizarra del Profesor Marco adaptada a los 4 años de carrera."""
    def __init__(self, audio_manager, save_system):
        self.audio = audio_manager
        self.save = save_system
        self.active = False
        self.year = 1
        self.day = 1
        self.slide_index = 0
        self.slides = []
        self.on_finish_callback = None

        self.font_title = make_font(19)
        self.font_title.set_bold(True)
        self.font_body = make_font(13)
        self.font_code = make_font(13)
        self.font_chalk = make_font(12)
        self.font_code_label = make_font(10)
        self.font_page = make_font(11)

        # Animación de escritura progresiva en la pizarra y parpadeo de cátedra
        self.chalk_char_index = 0
        self.chalk_is_done = False
        self.tick_count = 0

    def start_lecture(self, year, day, attempts, on_finish):
        self.audio.stop_narration()
        self.year = year
        self.day = day
        self.active = True
        self.slide_index = 0
        self.on_finish_callback = on_finish
        self.slides = self._build_slides(year,day,attempts)
        self.chalk_char_index = 0
        self.chalk_is_done = False
        self.tick_count = 0
        self.audio.play_chalk()

    def _build_slides(self, year, day, attempts):
        if day < 5:
            pages = slides_for(year,day)
        else:
            pages = [dict(title=f"Examen de año {year}", chalk_title="Cinco desafíos de la semana", chalk_body="Sin límite de tiempo, catálogo y apuntes disponibles\n\nCtrl+Enter o F5: probar sin nota\nCtrl+Shift+Enter: entregar respuesta definitiva\n\nTres aciertos de cinco dan nota 4,0, cinco dan 7,0\nLos errores de sintaxis no consumen una respuesta", code_example="", turing="Hoy resolverás cinco desafíos de lo que practicamos. No hay límite de tiempo. Lee qué columnas, condiciones y orden te piden. Puedes consultar tus apuntes y probar antes de entregar. La entrega definitiva se hace con control, mayúsculas y enter. No habrá pistas con soluciones durante la prueba.")]
        from game.intro_voice_scripts import attach_voice_scripts
        slides=[]
        for page in pages:
            for index,speech in enumerate(paginate_text(page['turing'],self.font_body,394,52,2)):
                slide=dict(page,turing=speech)
                if page.get('code_example'):slide['code_focus']=min(index,len(page['code_example'].splitlines())-1)
                if page.get('illustration'):slide['illustration_variant']=index
                slides.append(slide)
        attach_voice_scripts(day,slides,year)
        return slides

    def handle_event(self, event):
        if not self.active:
            return False

        cur_slide = self.slides[self.slide_index] if self.slides else None
        total_chalk = len(cur_slide["chalk_body"]) + len(cur_slide.get("code_example", "")) if cur_slide else 0

        if cur_slide and cur_slide.get('narration_id'):
            toggle=event.type==pygame.KEYDOWN and event.key==pygame.K_F7
            repeat=event.type==pygame.KEYDOWN and event.key==pygame.K_F8
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                toggle=pygame.Rect(326,15,60,17).collidepoint(event.pos)
                repeat=pygame.Rect(392,15,64,17).collidepoint(event.pos)
            if toggle:
                self.audio.toggle_narration();return True
            if repeat:
                self.audio.repeat_narration(cur_slide);return True

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_RIGHT]:
                if not self.chalk_is_done:
                    # Primer toque: Completa la pizarra de inmediato
                    self.chalk_char_index = total_chalk
                    self.chalk_is_done = True
                    return True
                else:
                    # Segundo toque: Avanza a la siguiente diapositiva
                    self.audio.stop_narration()
                    self.slide_index += 1
                    self.chalk_char_index = 0
                    self.chalk_is_done = False
                    self.audio.play_chalk()
                    if self.slide_index >= len(self.slides):
                        self.active = False
                        if self.on_finish_callback:
                            self.on_finish_callback()
                    return True
            elif event.key == pygame.K_LEFT and self.slide_index > 0:
                self.audio.stop_narration()
                self.slide_index -= 1
                self.chalk_char_index = 0
                self.chalk_is_done = False
                self.audio.play_chalk()
                return True
            elif event.key == pygame.K_ESCAPE:
                self.audio.stop_narration()
                self.active = False
                return True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.chalk_is_done:
                self.chalk_char_index = total_chalk
                self.chalk_is_done = True
                return True
            else:
                self.audio.stop_narration()
                self.slide_index += 1
                self.chalk_char_index = 0
                self.chalk_is_done = False
                self.audio.play_chalk()
                if self.slide_index >= len(self.slides):
                    self.active = False
                    if self.on_finish_callback:
                        self.on_finish_callback()
                return True
        return False

    def draw(self, surface):
        if not self.active or not self.slides:
            return

        self.tick_count += 1
        cur_slide = self.slides[self.slide_index]
        self.audio.play_narration(cur_slide)
        backdrop(surface)

        # 1. Pizarra de Clase
        board_rect = pygame.Rect(12, 8, 456, 192)
        board(surface,board_rect,exam=self.day==5)

        # Título de tiza
        draw_fitted_text(surface,cur_slide['chalk_title'],pygame.Rect(26,12,292,27),self.font_title,COLOR_AMBER,padding=0)
        if cur_slide.get('narration_id'):
            enabled=bool(self.audio.config.get('narration_enabled',True))
            for label,rect in [('Voz '+('sí' if enabled else 'no'),pygame.Rect(326,15,60,17)),('Repetir',pygame.Rect(392,15,64,17))]:
                button(surface,label,rect,self.font_page,accent=MINT)

        # Escritura progresiva en la pizarra (efecto tiza en vivo)
        chalk_body = cur_slide["chalk_body"]
        code_text = cur_slide.get("code_example", "")
        total_chalk = len(chalk_body) + len(code_text)

        if not self.chalk_is_done:
            self.chalk_char_index += 2
            if self.chalk_char_index >= total_chalk:
                self.chalk_char_index = total_chalk
                self.chalk_is_done = True
            elif self.chalk_char_index % 24 in [0, 1]:
                self.audio.play_chalk()

        body_chars = min(self.chalk_char_index, len(chalk_body))
        if cur_slide.get('illustration'):
            from game.learning_diagrams import illustration
            draw_fitted_text(surface,chalk_body,pygame.Rect(28,42,424,44),self.font_chalk,(197,214,204),padding=0)
            diagram_rect=pygame.Rect(28,92,424,90)
            old_clip=surface.get_clip()
            reveal=1 if self.chalk_is_done else self.chalk_char_index/max(1,total_chalk)
            surface.set_clip(old_clip.clip(pygame.Rect(diagram_rect.x,diagram_rect.y-16,max(0,int(diagram_rect.width*reveal)),diagram_rect.height+16)))
            illustration(surface,cur_slide['illustration'],diagram_rect,variant=cur_slide.get('illustration_variant'))
            surface.set_clip(old_clip)
        elif "table_columns" in cur_slide:
            render_wrapped_text(surface, chalk_body, pygame.Rect(28,42,424,20), self.font_chalk, color=(197,214,204), padding=0)
            draw_sql_grid_table(surface, pygame.Rect(28,65,424,124), cur_slide["table_columns"], cur_slide["table_rows"], font=self.font_chalk, max_rows=5)
        else:
            body_height = 58 if code_text else 146
            render_wrapped_text(surface, chalk_body[:body_chars], pygame.Rect(28,42,424,body_height), self.font_chalk, color=(197,214,204), line_spacing=2, padding=0)
            if code_text:
                code_box = pygame.Rect(28,103,424,86)
                draw.rect(surface, (12,28,25), code_box)
                if 'code_focus' in cur_slide:
                    draw.rect(surface,(30,65,58),(32,107+cur_slide['code_focus']*(self.font_code.get_linesize()+1),414,self.font_code.get_linesize()+1))
                old_clip = surface.get_clip()
                surface.set_clip(old_clip.clip(code_box))
                draw_sql(surface, code_text, (34,108), self.font_code, visible=max(0,self.chalk_char_index-len(chalk_body)))
                surface.set_clip(old_clip)

        # 2. Caja de Diálogo del Profesor Marco abajo (Texto listo altiro con parpadeo)
        diag_rect = pygame.Rect(12, 204, 456, 88)
        
        # Parpadeo sutil en el estado de Marco
        turing_title = f"PROFESOR MARCO | {cur_slide['title']}"

        draw_panel(surface, diag_rect, bg_color=(14, 18, 28, 248), border_color=(0, 229, 255), border_width=1,
                   title="", font=self.font_body, title_color=COLOR_AMBER)
        draw.rect(surface,(22,34,45),(14,206,452,18),border_radius=2)
        draw_fitted_text(surface,turing_title,pygame.Rect(21,207,438,16),self.font_body,COLOR_AMBER,padding=0)

        # Avatar de Marco
        avatar_x = 18
        avatar_y = 228
        marco_portrait(surface,pygame.Rect(avatar_x,avatar_y,40,52))

        # Texto del profesor (visible inmediatamente, con tamaño compacto legible)
        t_box = pygame.Rect(66, 228, 394, 52)
        render_wrapped_text(surface, cur_slide["turing"], t_box, self.font_body, color=COLOR_WHITE, line_spacing=2, padding=0)

        page_txt=f'{self.slide_index+1:02} / {len(self.slides):02}'
        surface.blit(self.font_page.render(page_txt,True,MINT),(68,280))
        progress=(self.slide_index+1)/len(self.slides)
        draw.rect(surface,(41,57,64),(132,283,246,2),border_radius=1)
        draw.rect(surface,GOLD,(132,283,max(1,int(246*progress)),2),border_radius=1)
