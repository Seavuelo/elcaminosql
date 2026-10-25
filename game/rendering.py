"""Coordenadas lógicas para el juego, texto dibujado con tres veces más detalle"""
import pygame
import math

DETAIL = 3


class TextSurface(pygame.Surface):
    def __new__(cls, logical, detailed):
        return super().__new__(cls, logical.get_size(), pygame.SRCALPHA)

    def __init__(self, logical, detailed):
        pygame.Surface.__init__(self, logical.get_size(), pygame.SRCALPHA)
        pygame.Surface.blit(self, logical, (0, 0))
        self.detailed = detailed


class ReadableFont:
    def __init__(self, size):
        self.point_size = size
        self.base = pygame.font.Font(None, size)
        self.detailed = pygame.font.Font(None, size * DETAIL)

    def __getattr__(self, name):
        return getattr(self.base, name)

    def size(self, text):
        width, height = self.detailed.size(str(text))
        return math.ceil(width / DETAIL), math.ceil(height / DETAIL)

    def get_height(self):
        return math.ceil(self.detailed.get_height() / DETAIL)

    def get_linesize(self):
        return math.ceil(self.detailed.get_linesize() / DETAIL)

    def render(self, text, antialias, color, background=None):
        detailed = self.detailed.render(str(text), True, color, background)
        size = self.size(text)
        logical = pygame.transform.smoothscale(detailed, size) if all(size) else self.base.render(str(text), True, color, background)
        return TextSurface(logical, detailed)


def make_font(size):
    return ReadableFont(size)


class Canvas(pygame.Surface):
    def __new__(cls, size):
        return super().__new__(cls, (size[0] * DETAIL, size[1] * DETAIL))

    def __init__(self, size):
        pygame.Surface.__init__(self, (size[0] * DETAIL, size[1] * DETAIL))

    def blit(self, source, dest, area=None, special_flags=0):
        position = dest.topleft if isinstance(dest, pygame.Rect) else dest[:2]
        detailed = source.detailed if isinstance(source, TextSurface) else source
        target_size = (source.get_width() * DETAIL, source.get_height() * DETAIL)
        if detailed.get_size() != target_size:
            scaler = pygame.transform.smoothscale if isinstance(source, TextSurface) else pygame.transform.scale
            detailed = scaler(detailed, target_size)
        physical_area = None if area is None else scale_rect(area)
        result = pygame.Surface.blit(self, detailed, scale_point(position), physical_area, special_flags)
        return logical_rect(result)

    def fill(self, color, rect=None, special_flags=0):
        return logical_rect(pygame.Surface.fill(self, color, None if rect is None else scale_rect(rect), special_flags))

    def get_clip(self):
        return logical_rect(pygame.Surface.get_clip(self))

    def set_clip(self, rect=None):
        pygame.Surface.set_clip(self, None if rect is None else scale_rect(rect))


def scale_point(point):
    return tuple(round(value * DETAIL) for value in point)


def scale_rect(rect):
    return pygame.Rect(*(round(value * DETAIL) for value in pygame.Rect(rect)))


def logical_rect(rect):
    return pygame.Rect(*(round(value / DETAIL) for value in rect))


class Draw:
    def rect(self, surface, color, rect, width=0, **kwargs):
        if isinstance(surface, Canvas):
            kwargs = {key: value * DETAIL if value >= 0 else value for key, value in kwargs.items()}
            return logical_rect(pygame.draw.rect(surface, color, scale_rect(rect), width * DETAIL, **kwargs))
        return pygame.draw.rect(surface, color, rect, width, **kwargs)

    def line(self, surface, color, start, end, width=1):
        if isinstance(surface, Canvas):
            return logical_rect(pygame.draw.line(surface, color, scale_point(start), scale_point(end), width * DETAIL))
        return pygame.draw.line(surface, color, start, end, width)

    def circle(self, surface, color, center, radius, width=0):
        if isinstance(surface, Canvas):
            return logical_rect(pygame.draw.circle(surface, color, scale_point(center), radius * DETAIL, width * DETAIL))
        return pygame.draw.circle(surface, color, center, radius, width)

    def ellipse(self, surface, color, rect, width=0):
        if isinstance(surface, Canvas):
            return logical_rect(pygame.draw.ellipse(surface, color, scale_rect(rect), width * DETAIL))
        return pygame.draw.ellipse(surface, color, rect, width)

    def polygon(self, surface, color, points, width=0):
        if isinstance(surface, Canvas):
            return logical_rect(pygame.draw.polygon(surface, color, list(map(scale_point, points)), width * DETAIL))
        return pygame.draw.polygon(surface, color, points, width)


draw = Draw()


def draw_caret(surface, x, y, height, color):
    if isinstance(surface, Canvas):
        return pygame.draw.line(surface, color, scale_point((x, y)),
                                scale_point((x, y + height - 1)), 1)
    return pygame.draw.line(surface, color, (round(x), round(y)),
                            (round(x), round(y + height - 1)), 1)
