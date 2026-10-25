"""Compañeros presentes en el taller y en su Kashut"""
INTRO_NAMES=('Moshi','Carlos','Sofía','Matías')
DESKS=((98,128),(210,128),(322,128))
DIALOGUES={
'Carlos':(
 ['Vine porque decía introducción, si partíamos escribiendo código me hacía el que se equivocó de sala',
  'Ahora entiendo lo de guardar el teléfono como texto, llevo años mirándolo y nunca se me ocurrió sumarlo, algo estaba haciendo bien',
  'Me gusta que el ID no se repita, con mi nombre siempre contestamos tres cuando pasan la lista',
  'Moshi tiene dos tutorías y yo ya necesito una para entender cómo anotaron las tutorías, vamos escalando',
  'Hoy dicen que hay que probar errores, por fin una actividad para la que llegué preparado'],
 ['En el Kashut me quedé mirando una respuesta que sabía, como cuando abres el refri y esperas que aparezca algo nuevo',
  'El NULL no era cero, me lo voy a anotar antes de que mi cabeza lo vuelva a convertir en cero',
  'Ya dejé el ID como identificador, el nombre lo voy a dejar normal por si aparece otro Carlos, seguramente aparece',
  'Al final sí pude unir las tablas, ahora falta unir mis ganas de estudiar con mi capacidad de no distraerme',
  'Se entiende harto más después de ver qué acepta y qué rechaza, igual mañana me siento cerca tuyo por si acaso']),
'Sofía':(
 ['Traje un cuaderno para esta semana, prometí no llenarlo de títulos bonitos y dejar las explicaciones para después',
  'Separé los tipos con ejemplos, el ejemplo me ayuda más que aprenderme el nombre y después no saber dónde usarlo',
  'Si se repite el nombre no pasa nada, si se repite el ID sí, eso lo anoté grande porque me conozco',
  'Estoy leyendo la relación en los dos sentidos para ver si tiene sentido, si suena raro hablando, algo dibujé raro',
  'Quiero revisar el modelo antes de probarlo, me gusta encontrar el error cuando todavía no hay nada importante guardado'],
 ['¿Cómo te fue? Yo en una apreté antes de terminar de leer, el cuaderno no te salva de ser apurada',
  'El código con ceros al principio me quedó clarísimo, un número puede verse igual y estar representando otra cosa',
  'Ya me quedó el identificador, ahora voy a revisar que no haya marcado todo obligatorio por costumbre',
  'La tabla intermedia me hizo sentido con las inscripciones, cada fila representa que alguien se anotó en algo',
  'Voy a guardar estos apuntes, cuando empiece el curso seguro vuelvo a buscar algo que juraba que ya sabía']),
'Matías':(
 ['Somos pocos, si nadie responde una pregunta voy a tener que mirar el techo con mucha convicción',
  'Si le pongo tipo fecha al plazo de la tarea, ¿el computador me va a recordar que la dejé para el último día?',
  'Yo pensé que el ID era el número de la fila, menos mal vine a esta semana antes de inventar una base entera así',
  'La pata de gallo me ayudó a acordarme de muchos, dibujar no era tan mala idea al final',
  'Quiero que el modelo rechace lo malo, pero si pudiera aceptar mis nombres feos sin juzgar también se agradece'],
 ['Me puse nervioso con el temporizador y todavía no había leído la pregunta, la próxima respiro primero',
  'Ya vi por qué no iba todo como texto, era cómodo hasta que querías hacer cualquier cosa con los datos',
  'Me quedó la clave, ahora falta que me quede en la cabeza hasta mañana',
  'Hoy hubo más líneas en mi dibujo que en mis apuntes, pero al menos estas sí significan algo',
  'Terminamos la introducción, ahora puedo decir que estoy confundido con fundamentos, antes era confundido nomás']),
}


def create_intro_peers(classmate_type):
    peers=[]
    for index,(name,hair,shirt,style) in enumerate([('Carlos',(80,45,25),(50,120,180),2),('Sofía',(105,65,35),(130,85,160),1),('Matías',(55,35,25),(90,130,80),4)]):
        x,y=DESKS[index]
        peer=classmate_type('intro_'+name.lower(),name,x,y,12,0,4,(235,190,150),hair,shirt,{}, {},'',hair_style=style)
        peer.px,peer.py=x+20,y+13
        peer.reset_day()
        peers.append(peer)
    return peers


def speech_for(name,day,completed):
    return DIALOGUES[name][1 if completed else 0][day-1]
