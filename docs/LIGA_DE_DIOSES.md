# Liga de Dioses

Un descanso opcional dentro de El Camino SQL, todas las partidas son locales, gratis y duran unos 42 segundos, los rangos avanzan con puntos de liga y los aumentos se compran con XP de las clases, ejercicios y pruebas

## Preparación

Hay nueve dioses, seis estrategias y seis reliquias gratuitas, 324 combinaciones antes de considerar los aumentos

Cada dios tiene afinidad con una estrategia, pesos propios para aprovechar sus aumentos y un perfil de daño, aguante y apoyo que modifica su desempeño

El plan muestra al próximo rival antes de jugar, los cuatro estilos alternan según las partidas completadas, cambiar de pestaña o cerrar el teléfono no cambia ese rival

Las reliquias suben algunas capacidades y reducen otras, no consumen XP, una reliquia afín añade una sinergia adicional, una buena preparación mejora las posibilidades pero no garantiza la victoria

La elección de dios, estrategia, reliquia y aumentos queda cerrada al iniciar una partida

## Precisión

Cada partida ofrece dos o tres oportunidades, con un aviso de 0,85 segundos antes de abrir la ventana

La ventana va de 0,3 a 1,3 segundos según el nivel del aumento correspondiente, el radio del objetivo crece de 9 a 23 unidades lógicas, el saldo de XP sin gastar no amplía la ventana

El anillo se aproxima a una banda exterior, pulsa dentro del círculo cuando entre en ella, la zona central de tiempo concede un resultado perfecto, también puedes usar Espacio o Enter como alternativa accesible de teclado

- Visión: una intercepción que habilita una asistencia
- Mecánicas: una baja adicional, puede completar una triple, cuadra o penta si esa cadena ya existe
- Posicionamiento: evita una muerte futura, o habilita una asistencia si no quedan muertes por evitar
- Objetivos: asegura un Guardián sin convertirlo artificialmente en una asistencia
- Maestría: conecta la definitiva y consigue una baja

Un acierto suma cuatro puntos porcentuales a las posibilidades de victoria, uno perfecto suma 6,5, el límite final es 95%, la precisión puede cambiar al ganador

Un fallo no quita XP ni inventa una muerte adicional, cerrar el teléfono deja seguir la simulación y omite las oportunidades, abrir Controles o perder el foco con el teléfono abierto pausa su avance

## Relato y marcador

El marcador usa las bajas, muertes y asistencias de eventos que ya ocurrieron, no una interpolación del resultado final

Torres y Guardianes son eventos de objetivo, las cadenas de bajas solo se anuncian cuando sus eventos contienen esas bajas, la penta suma únicamente el quinto rival después de una cuadra

Las unidades se desplazan entre los lugares de esas jugadas, las bajas retiran temporalmente a las unidades afectadas y los objetivos derribados dejan sus restos en el mapa

La simulación conserva un componente de azar para representar la oposición y al resto del equipo, no pretende ser un motor completo de combate MOBA

## Controles

F4 o el teléfono decorado abren Liga, Esc, P o F4 cierran el teléfono

1 abre Dioses, 2 Aumentos y 3 Plan, Tab recorre las pestañas, flechas laterales cambian de dios, S cambia estrategia y R cambia reliquia, Enter busca partida o compra el aumento seleccionado, durante combate sirve para la precisión

El botón F10 reúne los controles en el juego, las compras y los ajustes también funcionan con clic

## Guardado y validación

Se conservan XP, recompensas, rangos, maestrías originales y partidas en curso de la versión anterior, las maestrías de los dioses nuevos empiezan en cero

Los eventos se guardan resueltos para que recargar no duplique una recompensa, la comprobación del ejecutable incluye preparación, combate, precisión y resultado

Las partidas no generan XP repetible, estudiar sigue siendo la fuente de experiencia, la calibración final de dificultad necesita sesiones humanas con distintas combinaciones

Referencias de diseño: avisos previos para dar tiempo a interpretar una acción, [Enemy Attacks and Telegraphing](https://www.gamedeveloper.com/design/enemy-attacks-and-telegraphing), representación mediante [primitivas de Pygame](https://www.pygame.org/docs/ref/draw.html)
