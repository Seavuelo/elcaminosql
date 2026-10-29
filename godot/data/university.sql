BEGIN TRANSACTION;
CREATE TABLE estudiantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        carrera TEXT NOT NULL,
        semestre INTEGER NOT NULL,
        promedio REAL NOT NULL,
        estado TEXT NOT NULL
    );
INSERT INTO "estudiantes" VALUES(1,'Ignacio Perez','Ingenieria Informatica',2,6.2,'Activo');
INSERT INTO "estudiantes" VALUES(2,'Sofia Miranda','Ingenieria Informatica',3,6.8,'Activo');
INSERT INTO "estudiantes" VALUES(3,'Carlos Munoz','Ciencia de Datos',1,3.8,'Activo');
INSERT INTO "estudiantes" VALUES(4,'Valentina Rojas','Ingenieria Informatica',2,5.5,'Activo');
INSERT INTO "estudiantes" VALUES(5,'Matias Silva','Ciberseguridad',4,4.1,'Activo');
INSERT INTO "estudiantes" VALUES(6,'Camila Castro','Ciencia de Datos',2,6.5,'Activo');
INSERT INTO "estudiantes" VALUES(7,'Felipe Morales','Ingenieria Informatica',1,3.5,'Suspendido');
INSERT INTO "estudiantes" VALUES(8,'Daniela Herrera','Ciberseguridad',3,5.9,'Activo');
INSERT INTO "estudiantes" VALUES(9,'Lucas Gonzalez','Ingenieria Informatica',2,4.8,'Activo');
INSERT INTO "estudiantes" VALUES(10,'Constanza Soto','Ciencia de Datos',3,6.9,'Activo');
INSERT INTO "estudiantes" VALUES(11,'Diego Espinoza','Ingenieria Informatica',1,3.2,'Activo');
INSERT INTO "estudiantes" VALUES(12,'Javiera Diaz','Ingenieria Informatica',3,5.7,'Activo');
CREATE TABLE materias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL,
        creditos INTEGER NOT NULL,
        cupos INTEGER NOT NULL
    );
INSERT INTO "materias" VALUES(1,'BD101','Bases de Datos I',4,8);
INSERT INTO "materias" VALUES(2,'PROG101','Algoritmos y Estructuras',5,0);
INSERT INTO "materias" VALUES(3,'SO201','Sistemas Operativos',4,12);
INSERT INTO "materias" VALUES(4,'RED301','Redes y Comunicaciones',4,3);
INSERT INTO "materias" VALUES(5,'MAT102','Calculo Diferencial',5,0);
INSERT INTO "materias" VALUES(6,'SEG202','Fundamentos de Seguridad',3,15);
CREATE TABLE notas_parcial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estudiante_id INTEGER NOT NULL,
        estudiante_nombre TEXT NOT NULL,
        materia_codigo TEXT NOT NULL,
        nota REAL NOT NULL,
        FOREIGN KEY (estudiante_id) REFERENCES estudiantes (id)
    );
INSERT INTO "notas_parcial" VALUES(1,1,'Ignacio Perez','BD101',6.0);
INSERT INTO "notas_parcial" VALUES(2,2,'Sofia Miranda','BD101',6.8);
INSERT INTO "notas_parcial" VALUES(3,3,'Carlos Munoz','BD101',3.2);
INSERT INTO "notas_parcial" VALUES(4,4,'Valentina Rojas','BD101',5.4);
INSERT INTO "notas_parcial" VALUES(5,5,'Matias Silva','BD101',3.9);
INSERT INTO "notas_parcial" VALUES(6,6,'Camila Castro','BD101',6.1);
INSERT INTO "notas_parcial" VALUES(7,7,'Felipe Morales','BD101',2.8);
INSERT INTO "notas_parcial" VALUES(8,8,'Daniela Herrera','BD101',5.9);
INSERT INTO "notas_parcial" VALUES(9,9,'Lucas Gonzalez','BD101',4.2);
INSERT INTO "notas_parcial" VALUES(10,10,'Constanza Soto','BD101',7.0);
INSERT INTO "notas_parcial" VALUES(11,11,'Diego Espinoza','BD101',3.4);
INSERT INTO "notas_parcial" VALUES(12,12,'Javiera Diaz','BD101',5.6);
CREATE TABLE profesores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        departamento TEXT NOT NULL,
        oficina TEXT NOT NULL
    );
INSERT INTO "profesores" VALUES(1,'Profesor Marco','Ciencias de la Computacion','Lab 204');
INSERT INTO "profesores" VALUES(2,'Dra. Ada Lovelace','Arquitectura de Software','Lab 201');
INSERT INTO "profesores" VALUES(3,'Prof. Edgar Codd','Sistemas de Informacion','Lab 105');
CREATE TABLE tutorias (id INTEGER PRIMARY KEY, estudiante_id INTEGER NOT NULL, tema TEXT NOT NULL, asistencia INTEGER, FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id));
INSERT INTO "tutorias" VALUES(1,1,'Filtros',1);
INSERT INTO "tutorias" VALUES(2,1,'Ordenamiento',0);
INSERT INTO "tutorias" VALUES(3,2,'Subconsultas',NULL);
INSERT INTO "tutorias" VALUES(4,3,'Filtros',1);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('estudiantes',12);
INSERT INTO "sqlite_sequence" VALUES('materias',6);
INSERT INTO "sqlite_sequence" VALUES('notas_parcial',12);
INSERT INTO "sqlite_sequence" VALUES('profesores',3);
COMMIT;