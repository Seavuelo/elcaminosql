"""Tokenización sin pérdida y colores compartidos por los ejemplos y el editor"""
import re
from game.rendering import make_font

KEYWORDS = set("SELECT DISTINCT FROM WHERE AND OR NOT IN IS NULL AS ORDER BY ASC DESC LIMIT OFFSET GROUP HAVING JOIN INNER LEFT OUTER ON INSERT INTO VALUES UPDATE SET DELETE CREATE TABLE VIEW INDEX IF EXISTS PRIMARY KEY INTEGER TEXT REAL BLOB DEFAULT UNIQUE REFERENCES FOREIGN BEGIN TRANSACTION COMMIT ROLLBACK EXPLAIN QUERY PLAN COUNT SUM AVG MIN MAX WITH UNION ALL CASE WHEN THEN ELSE END LIKE BETWEEN".split())
PATTERN = re.compile(r"(?P<comment>--[^\n]*|/\*[\s\S]*?(?:\*/|$))|(?P<string>'(?:''|[^'])*(?:'|$))|(?P<identifier>\"(?:\"\"|[^\"])*(?:\"|$)|\x60[^\x60]*\x60|\[[^\]]*\])|(?P<number>\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|(?P<word>[\w]+)|(?P<space>\s+)|(?P<operator><=|>=|<>|!=|==|\|\||[-+*/%=<>])|(?P<punctuation>.)")
COLORS = {"keyword": (89,162,255), "identifier": (244,247,255), "string": (145,220,150), "number": (255,195,110), "operator": (255,100,120), "punctuation": (255,100,120), "comment": (150,175,160), "space": (244,247,255)}


def tokenize(sql):
    for match in PATTERN.finditer(sql):
        kind, value = match.lastgroup, match.group()
        if kind == "word":
            kind = "keyword" if value.upper() in KEYWORDS else "identifier"
        yield kind, value


def code_font(size, bold=False):
    font = make_font(size)
    font.base.set_bold(bold)
    font.detailed.set_bold(bold)
    return font


def token_font(font, kind):
    bold = kind in {"keyword", "identifier", "operator"}
    if not hasattr(font, "sql_fonts"):
        font.sql_fonts = {}
    if bold not in font.sql_fonts:
        font.sql_fonts[bold] = code_font(font.point_size, bold)
    return font.sql_fonts[bold]


def sql_width(text, font):
    return sum(token_font(font,kind).size(value)[0] for kind,value in tokenize(text))


def draw_sql(surface, text, pos, font, visible=None, light=False):
    """Tokeniza todo antes de revelar caracteres, sin recolorear tokens parciales"""
    x0, y = pos
    x = x0
    remaining = len(text) if visible is None else visible
    for kind, token in tokenize(text):
        shown = token[:max(0, remaining)]
        remaining -= len(token)
        selected = token_font(font,kind)
        for i, part in enumerate(shown.split('\n')):
            if i:
                x, y = x0, y + font.get_linesize() + 1
            if part:
                color = COLORS[kind]
                if light:
                    color = {"keyword": (25,80,155), "identifier": (35,40,50), "string": (35,110,55), "number": (145,75,10), "operator": (175,35,55), "punctuation": (175,35,55), "comment": (85,110,90)}.get(kind, (35,40,50))
                surface.blit(selected.render(part, True, color), (x,y))
                x += selected.size(part)[0]
