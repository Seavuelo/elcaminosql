import sqlite3
import os

class DatabaseManager:
    """Administra la conexión SQLite, ejecución de consultas y sandbox universitario."""
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "universidad.db")
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def execute_query(self, query: str, allow_write: bool = False) -> dict:
        """
        Ejecuta una consulta SQL del estudiante y devuelve el resultado estructurado.
        Si allow_write es True (Año 2 en adelante), permite CREATE, INSERT, UPDATE, DELETE.
        """
        clean_query = query.strip()
        if not clean_query:
            return {"success": False, "error": "La consulta está vacía. Escribe una sentencia SQL."}

        query_upper = clean_query.upper()
        
        # Bloquear DROP de seguridad para no romper la base central
        if "DROP TABLE " in query_upper and any(t in query_upper for t in ["ESTUDIANTES", "MATERIAS", "NOTAS_PARCIAL", "PROFESORES"]):
            return {
                "success": False,
                "error": "Seguridad Académica: No tienes permisos para borrar las tablas oficiales de la universidad."
            }

        # En Año 1 solo permitimos lectura
        if not allow_write:
            if any(bad in query_upper for bad in ["CREATE ", "INSERT ", "UPDATE ", "DELETE ", "ALTER "]):
                return {
                    "success": False, 
                    "error": "Acceso restringido: En Año 1 solo tienes permisos de lectura (SELECT). La creación y modificación de tablas se desbloquea en Año 2."
                }

        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(clean_query)
            
            # Si fue una instrucción de modificación (INSERT, UPDATE, DELETE, CREATE), hacer commit
            is_write = any(w in query_upper for w in ["INSERT", "UPDATE", "DELETE", "CREATE", "ALTER"])
            if is_write:
                conn.commit()
                affected = cur.rowcount
                conn.close()
                return {
                    "success": True,
                    "columns": ["Estado", "Filas Afectadas"],
                    "rows": [["Operación completada con éxito", affected if affected >= 0 else 1]],
                    "row_count": 1,
                    "error": None
                }

            columns = [desc[0] for desc in cur.description] if cur.description else []
            rows = cur.fetchall()
            conn.close()

            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "error": None
            }
        except sqlite3.OperationalError as e:
            err_msg = str(e)
            if "no such table" in err_msg:
                table_name = err_msg.split(":")[-1].strip()
                return {"success": False, "error": f"Error: La tabla '{table_name}' no existe. Revisa el catálogo pulsando [TAB]."}
            elif "no such column" in err_msg:
                col_name = err_msg.split(":")[-1].strip()
                return {"success": False, "error": f"Error: La columna '{col_name}' no existe en la tabla consultada."}
            elif "syntax error" in err_msg:
                return {"success": False, "error": f"Error de sintaxis SQL: Revisa comas, palabras clave o comillas. Detalle: {err_msg}"}
            else:
                return {"success": False, "error": f"Error SQLite: {err_msg}"}
        except Exception as e:
            return {"success": False, "error": f"Error inesperado: {str(e)}"}

    def get_schema(self) -> dict:
        """Devuelve las tablas existentes y sus columnas para el catálogo visual."""
        schema = {}
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [row[0] for row in cur.fetchall()]

            for t in tables:
                cur.execute(f"PRAGMA table_info({t});")
                cols = [{"name": row[1], "type": row[2]} for row in cur.fetchall()]
                schema[t] = cols

            conn.close()
        except Exception as e:
            print(f"[DatabaseManager] Error leyendo esquema: {e}")
        return schema
