# El Camino SQL 🎓💻
### *"Para todo buen final, hay un inicio..."*
*Desarrollado por Seavuelo*

Un videojuego educativo de rol y aventura en **pixel art retro**, donde todo el aprendizaje, misiones y progresión se basa en **consultas SQL reales** ejecutadas en una base de datos local SQLite.

---

## ⚙️ Menú de Ajustes y Configuración (`[O]` o `[F2]`)

Al iniciar o durante la partida, puedes presionar la tecla **`[O]`** o **`[F2]`** para configurar:
- **Modo de Pantalla**: `Ventana`, `Pantalla Completa` o `Ventana sin Bordes`.
- **Resolución**: `960x600` (Retro x2), `1280x720` (HD) o `1366x768` (Nativa de tu pantalla).
- **Volumen de Música**: Música de fondo lo-fi relajante para estudiar/concentrarse.
- **Volumen de Efectos**: Sonidos de teclado mecánico, campanilla de éxito satisfactoria y tiza de pizarra.
- **Persistencia**: Tus ajustes se guardan automáticamente en `~/.config/sql-quest/config.json`.

---

## 🏛️ Dinámica Pedagógica: La Semana Universitaria (Días 1 al 5)

Cada día de la semana tiene una estructura clara:
1. **La Clase Teórica en la Pizarra**:
   - El **Profesor Turing** explica el concepto en la pizarra con diagramas de tiza, tablas de datos y ejemplos de sintaxis.
2. **El Laboratorio Práctico**:
   - Te sientas en tu estación de trabajo y abres tu **Terminal SQL** para resolver la misión del día.
3. **El Ciclo Académico**:
   - **Día 1**: Introducción al modelo relacional, `SELECT` y `FROM`.
   - **Día 2**: Filtros de condición con `WHERE` y operadores numéricos/texto.
   - **Día 3**: Ordenamiento de registros con `ORDER BY` (`ASC` / `DESC`).
   - **Día 4**: Límites y combinación de `WHERE` + `ORDER BY` + `LIMIT`.
   - **Día 5 (Viernes de Examen Parcial)**:
     - 3 desafíos integradores sin pistas.
     - Calificación oficial en escala chilena de **1.0 a 7.0** (nota de aprobación: **4.0**).
     - **Si apruebas (>= 4.0)**: ¡Te titulas del Curso 1 y desbloqueas el Capítulo 2!
     - **Si repruebas (< 4.0)**: Repites la semana. El profesor Turing te recibe con su clásico: *"¡Vaya, veo caras conocidas! Un gusto verte de nuevo por aquí... parece que le tomaste cariño a la materia."*

---

## 📊 Visualizador de Tablas y Base de Datos

En la Terminal SQL:
- **Salto de línea responsivo**: Los textos y explicaciones nunca se desbordan de sus marcos.
- **Data Grid Visual**: Cuadrícula con celdas, índice de filas (`#`), líneas divisorias y rayado de cebra.
- **Catálogo de Esquema (`[TAB]`)**: Permite navegar entre pestañas visuales (`[estudiantes]`, `[materias]`, `[notas_parcial]`, `[profesores]`) con las teclas `[1, 2, 3, 4]` para inspeccionar la estructura real de cada tabla.

---

## 🎮 Controles

- **`[W, A, S, D]` o `[Flechas]`**: Moverse por el aula.
- **`[E]` o `[ENTER]`**: Interactuar (PC, Profesor Turing, Biblioteca).
- **`[O]` o `[F2]`**: Abrir menú de ajustes y pantalla.
- **`[TAB]`**: Ver el catálogo visual de tablas en la terminal.
- **`[ENTER]`**: Ejecutar consulta SQL en la terminal.
- **`[FLECHAS ARRIBA / ABAJO]`**: Historial de consultas.
- **`[ESC]`**: Salir de menús o cerrar la terminal.
