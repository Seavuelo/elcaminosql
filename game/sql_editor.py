"""Edición multilínea independiente del estado del laboratorio"""
class SQLBuffer:
    def __init__(self):
        self.anchor = None
        self.preferred_column = None

    def selection(self, cursor):
        return sorted((self.anchor, cursor)) if self.anchor is not None else (cursor,cursor)

    def replace(self, text, cursor, value):
        start,end = self.selection(cursor)
        self.anchor = None
        self.preferred_column = None
        return text[:start] + value + text[end:], start + len(value)

    def move(self, text, cursor, key, select=False, ctrl=False):
        if select and self.anchor is None:
            self.anchor = cursor
        elif not select:
            self.anchor = None
        start = text.rfind('\n',0,cursor) + 1
        end = text.find('\n',cursor)
        if end < 0:
            end = len(text)
        if key in ('up','down'):
            column = cursor-start if self.preferred_column is None else self.preferred_column
            self.preferred_column = column
            if key == 'up' and start:
                previous = text.rfind('\n',0,start-1)+1
                return min(previous+column,start-1)
            if key == 'down' and end < len(text):
                next_end = text.find('\n',end+1)
                return min(end+1+column,len(text) if next_end<0 else next_end)
            return cursor
        self.preferred_column = None
        if key == 'home': return 0 if ctrl else start
        if key == 'end': return len(text) if ctrl else end
        if key == 'left': return max(0,cursor-1)
        if key == 'right': return min(len(text),cursor+1)
        return cursor
