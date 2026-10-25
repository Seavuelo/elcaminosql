import os
import sqlite3
from contextlib import closing

from game.save_system import SAVE_DIR
from database.seed_universidad import add_practice_data


class DatabaseManager:
    """Ejecuta SQL en la base de práctica, separada de los datos originales."""

    CORE_TABLES = {"estudiantes", "materias", "notas_parcial", "profesores", "tutorias"}
    WRITE_ACTIONS = {
        sqlite3.SQLITE_CREATE_TABLE, sqlite3.SQLITE_CREATE_INDEX,
        sqlite3.SQLITE_CREATE_VIEW, sqlite3.SQLITE_INSERT,
        sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE,
    }

    def __init__(self, db_path=None):
        self.seed_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                      "database", "universidad.db")
        self.db_path = db_path or os.path.join(SAVE_DIR, "universidad.db")
        if os.path.normcase(os.path.realpath(self.db_path)) == os.path.normcase(os.path.realpath(self.seed_path)):
            raise ValueError("La plantilla del curso no se puede usar como base de práctica")
        if db_path is None and not os.path.exists(self.db_path):
            self.reset()
        elif db_path is None:
            with closing(self.get_connection()) as conn:
                add_practice_data(conn)
                conn.commit()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def reset(self):
        """Restaura los datos de una nueva partida sin modificar la plantilla."""
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with closing(sqlite3.connect(self.seed_path)) as source:
            with closing(self.get_connection()) as target:
                source.backup(target)
                add_practice_data(target)
                target.commit()

    def _authorizer(self, allow_write, writes):
        read_actions = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ,
                        sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
        schema_actions = {sqlite3.SQLITE_DROP_TABLE, sqlite3.SQLITE_DROP_INDEX,
                          sqlite3.SQLITE_DROP_VIEW, sqlite3.SQLITE_ALTER_TABLE,
                          sqlite3.SQLITE_REINDEX, sqlite3.SQLITE_ANALYZE}

        def authorize(action, arg1, arg2, database, trigger):
            if action in read_actions:
                return sqlite3.SQLITE_OK
            if not allow_write or database != "main":
                return sqlite3.SQLITE_DENY
            if action == sqlite3.SQLITE_DROP_TABLE and arg1.lower() in self.CORE_TABLES:
                return sqlite3.SQLITE_DENY
            if action == sqlite3.SQLITE_ALTER_TABLE and arg2.lower() in self.CORE_TABLES:
                return sqlite3.SQLITE_DENY
            if action in self.WRITE_ACTIONS:
                if arg1 not in {"sqlite_master", "sqlite_sequence"}:
                    writes.add((action, arg1, arg2))
                return sqlite3.SQLITE_OK
            if action in schema_actions:
                return sqlite3.SQLITE_OK
            # ATTACH, PRAGMA, transacciones y acceso a otras bases quedan fuera del aula.
            return sqlite3.SQLITE_DENY

        return authorize

    @staticmethod
    def _state(conn):
        """Compara estructura y datos, independientemente del formato del SQL."""
        state = []
        objects = conn.execute("SELECT type, name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name").fetchall()
        for kind, name in objects:
            quoted = name.replace('"', '""')
            if kind == "index":
                info = conn.execute(f'PRAGMA index_xinfo("{quoted}")').fetchall()
                state.append((kind, name, info))
            else:
                info = conn.execute(f'PRAGMA table_info("{quoted}")').fetchall()
                rows = conn.execute(f'SELECT * FROM "{quoted}"').fetchall()
                indexes = conn.execute(f'PRAGMA index_list("{quoted}")').fetchall()
                foreign_keys = conn.execute(f'PRAGMA foreign_key_list("{quoted}")').fetchall()
                state.append((kind, name, info, sorted(map(repr, rows)), indexes, foreign_keys))
        return state

    def execute_query(self, query: str, allow_write: bool = False,
                      expected_query=None, commit=True) -> dict:
        """Valida los efectos de los ejercicios de escritura antes de confirmarlos."""
        if not query.strip():
            return {"success": False, "error": "La consulta está vacía. Escribe una sentencia SQL."}
        try:
            with closing(self.get_connection()) as conn:
                with closing(sqlite3.connect(":memory:")) as reference:
                    if expected_query:
                        conn.backup(reference)
                    # La transacción incluye DDL para poder deshacer respuestas incorrectas.
                    conn.execute("BEGIN")
                    writes = set()
                    conn.set_authorizer(self._authorizer(allow_write and bool(expected_query), writes))
                    steps = 0

                    def limit_execution():
                        nonlocal steps
                        steps += 1
                        return steps > 1000

                    conn.set_progress_handler(limit_execution, 1000)
                    cur = conn.execute(query)
                    columns = [desc[0] for desc in cur.description] if cur.description else []
                    rows = cur.fetchmany(1001) if cur.description else []
                    if len(rows) > 1000:
                        raise sqlite3.OperationalError("Demasiados resultados: usa LIMIT 1000 o un filtro WHERE.")
                    affected = cur.rowcount
                    conn.set_authorizer(None)
                    conn.set_progress_handler(None, 0)

                    if expected_query:
                        expected_writes = set()
                        reference.execute("BEGIN")
                        reference.set_authorizer(self._authorizer(True, expected_writes))
                        reference.execute(expected_query)
                        reference.set_authorizer(None)
                        if (writes != expected_writes or
                                self._state(conn) != self._state(reference)):
                            return {"success": False, "validation_failed": True, "error": "La operación no produce los cambios solicitados. Se deshizo para que puedas corregirla."}

                    if commit:
                        conn.commit()
                    if not columns:
                        columns = ["Estado", "Filas Afectadas"]
                        rows = [["Operación completada con éxito", max(affected, 0)]]
                    return {"success": True, "columns": columns, "rows": rows,
                            "row_count": len(rows), "error": None,
                            "write_validated": expected_query is not None}
        except sqlite3.Error as exc:
            message = str(exc)
            if "one statement at a time" in message:
                message = "Ejecuta una sola sentencia SQL, puedes distribuirla en varias líneas"
            elif "no such table" in message:
                message = f"La tabla '{message.split(':')[-1].strip()}' no existe. Revisa el catálogo [F2]."
            elif "no such column" in message:
                message = f"La columna '{message.split(':')[-1].strip()}' no existe en la tabla consultada."
            elif "not authorized" in message or "prohibited" in message:
                message = ("Acceso restringido: solo el ejercicio activo puede autorizar cambios validados, "
                           "las consultas de lectura no permiten modificar datos ni estructuras")
            elif "interrupted" in message:
                message = "La consulta excedió el límite de trabajo. Simplifica los JOIN o los filtros."
            return {"success": False, "error": f"Error SQLite: {message}"}

    def get_schema(self) -> dict:
        """Incluye tablas y vistas creadas por el estudiante."""
        with closing(self.get_connection()) as conn:
            schema = {}
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%'")
            for (name,) in tables.fetchall():
                quoted = name.replace('"', '""')
                try:
                    schema[name] = [{"name": row[1], "type": row[2]}
                                    for row in conn.execute(f'PRAGMA table_info("{quoted}")')]
                except sqlite3.Error:
                    # SQLite permite crear vistas que apuntan a tablas inexistentes.
                    continue
            return schema
