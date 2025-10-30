"""
Seeder completo para el microservicio estudiantil
Ejecuta todo el script SQL proporcionado en el orden exacto
Ejecutar: python seeder_completo.py
"""

import psycopg2
import sys
import os
from datetime import datetime

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'topicos-xd.i.aivencloud.com',
    'port': '18069',
    'database': 'defaultdb',
    'user': 'avnadmin',
    'password': 'AVNS_6kmcp-nNyDI2rk7mUHg'
}

def get_db_connection():
    """Establece conexión con la base de datos"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        sys.exit(1)

def execute_complete_sql(cursor):
    """Ejecuta todo el script SQL completo"""
    print("🚀 Ejecutando script SQL completo...")
    
    complete_sql = """
-- ============================================================
-- CREAR TABLAS
-- ============================================================

CREATE TABLE carrera (
    codigo_carrera VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE plan_estudio (
    codigo_plan VARCHAR(20) PRIMARY KEY,
    plan VARCHAR(20),
    cant_semestre INT NOT NULL,
    codigo_carrera VARCHAR(20) REFERENCES carrera(codigo_carrera)
);

CREATE TABLE nivel (
    nivel INT PRIMARY KEY
);

CREATE TABLE materia (
    sigla VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    creditos INT NOT NULL,
    es_electiva BOOLEAN DEFAULT FALSE
);

CREATE TABLE prerequisito (
    sigla_prerequisito VARCHAR(20) REFERENCES materia(sigla),
    sigla_materia VARCHAR(20) REFERENCES materia(sigla),
    PRIMARY KEY (sigla_prerequisito, sigla_materia)
);

CREATE TABLE plan_materia (
    codigo_plan VARCHAR(20) REFERENCES plan_estudio(codigo_plan),
    sigla_materia VARCHAR(20) REFERENCES materia(sigla),
    nivel INT REFERENCES nivel(nivel),
    PRIMARY KEY (codigo_plan, sigla_materia)
);

CREATE TABLE docente (
    codigo_docente VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(50),
    apellido VARCHAR(50),
    ci VARCHAR(20),
    correo VARCHAR(100),
    telefono VARCHAR(20)
);

CREATE TABLE aula (
    codigo_aula VARCHAR(20) PRIMARY KEY,
    modulo VARCHAR(10),
    aula VARCHAR(10),
    capacidad INT,
    ubicacion VARCHAR(100)
);

CREATE TABLE horario (
    codigo_horario VARCHAR(20) PRIMARY KEY,
    dias_semana TEXT[] NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL
);

CREATE TABLE grupo (
    codigo_grupo VARCHAR(20) PRIMARY KEY,
    sigla_materia VARCHAR(20) REFERENCES materia(sigla),
    codigo_docente VARCHAR(20) REFERENCES docente(codigo_docente),
    codigo_aula VARCHAR(20) REFERENCES aula(codigo_aula),
    codigo_horario VARCHAR(20) REFERENCES horario(codigo_horario),
    descripcion VARCHAR(150),
    cupo INT DEFAULT 40,
    inscritos_actuales INT DEFAULT 0
);

CREATE TABLE periodo_academico (
    codigo_periodo VARCHAR(20) PRIMARY KEY,
    semestre VARCHAR(20),
    fecha_inicio DATE,
    fecha_fin DATE,
    estado VARCHAR(20)
);

CREATE TABLE estudiante (
    codigo_carrera VARCHAR(20) REFERENCES carrera(codigo_carrera),
    registro_academico VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    ci VARCHAR(20) UNIQUE,
    correo VARCHAR(100),
    contrasena TEXT NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(150),
    estado_academico VARCHAR(20) DEFAULT 'REGULAR'
);

CREATE TABLE inscripcion (
    codigo_inscripcion VARCHAR(20) PRIMARY KEY,
    registro_academico VARCHAR(20) REFERENCES estudiante(registro_academico),
    codigo_periodo VARCHAR(20) REFERENCES periodo_academico(codigo_periodo),
    fecha_inscripcion DATE DEFAULT CURRENT_DATE
);

CREATE TABLE detalle_inscripcion (
    codigo_detalle VARCHAR(20) PRIMARY KEY,
    codigo_inscripcion VARCHAR(20) REFERENCES inscripcion(codigo_inscripcion),
    codigo_grupo VARCHAR(20) REFERENCES grupo(codigo_grupo)
);

CREATE TABLE pago (
    codigo_pago VARCHAR(20) PRIMARY KEY,
    registro_academico VARCHAR(20) REFERENCES estudiante(registro_academico),
    descripcion VARCHAR(100),
    monto NUMERIC(10,2),
    fecha_pago DATE DEFAULT CURRENT_DATE
);

CREATE TABLE bloqueo (
    codigo_bloqueo VARCHAR(20) PRIMARY KEY,
    registro_academico VARCHAR(20) REFERENCES estudiante(registro_academico),
    descripcion VARCHAR(100)
);

-- ============================================================
-- 🧾 HISTORIAL ACADÉMICO
-- ============================================================

CREATE TABLE historial_academico (
    id_historial SERIAL PRIMARY KEY,
    registro_academico VARCHAR(20) REFERENCES estudiante(registro_academico),
    sigla_materia VARCHAR(20) REFERENCES materia(sigla),
    codigo_periodo VARCHAR(20) REFERENCES periodo_academico(codigo_periodo),
    nota_final NUMERIC(5,2) CHECK (nota_final BETWEEN 0 AND 100),
    estado VARCHAR(20) CHECK (estado IN ('APROBADA','REPROBADA','RETIRADA')),
    observacion VARCHAR(200),
    fecha_registro DATE DEFAULT CURRENT_DATE
);

-- ============================================================
-- 📘 VISTAS DE APOYO
-- ============================================================

CREATE OR REPLACE VIEW vista_materias_aprobadas AS
SELECT * FROM historial_academico WHERE estado = 'APROBADA';

CREATE OR REPLACE VIEW vista_materias_reprobadas AS
SELECT * FROM historial_academico WHERE estado = 'REPROBADA';

-- ============================================================
-- 🧩 SEEDER BASE: CARRERA Y PLAN DE ESTUDIO
-- ============================================================

INSERT INTO carrera (codigo_carrera, nombre)
VALUES ('INF187', 'Ingeniería Informática');

INSERT INTO plan_estudio (codigo_plan, cant_semestre, plan, codigo_carrera)
VALUES ('187-3', 10, '187-3', 'INF187');

-- ============================================================
-- 📘 MATERIAS DEL PLAN 187-3
-- ============================================================

INSERT INTO materia (sigla, nombre, creditos, es_electiva) VALUES
-- SEM 1
('MAT101','Cálculo I',5,false),
('INF119','Estructuras Discretas',4,false),
('INF110','Introducción a la Informática',3,false),
('FIS100','Física I',4,false),
('LIN100','Inglés Técnico I',2,false),

-- SEM 2
('MAT102','Cálculo II',5,false),
('MAT103','Álgebra Lineal',4,false),
('INF120','Programación I',4,false),
('FIS102','Física II',4,false),
('LIN101','Inglés Técnico II',2,false),

-- SEM 3
('MAT207','Ecuaciones Diferenciales',4,false),
('INF210','Programación II',4,false),
('INF211','Arquitectura de Computadoras',4,false),
('FIS200','Física III',4,false),
('ADM100','Administración',3,false),

-- SEM 4
('MAT202','Probabilidades y Estadísticas I',4,false),
('MAT205','Métodos Numéricos',4,false),
('INF220','Estructura de Datos I',4,false),
('INF221','Programación Ensamblador',4,false),
('ADM200','Contabilidad',3,false),

-- SEM 5
('MAT302','Probabilidades y Estadísticas II',4,false),
('INF318','Programación Lógica y Funcional',4,false),
('INF310','Estructura de Datos II',4,false),
('INF312','Base de Datos I',4,false),
('INF319','Lenguajes Formales',4,false),

-- SEM 6
('MAT329','Investigación Operativa I',4,false),
('INF342','Sistemas de Información I',4,false),
('INF323','Sistemas Operativos I',4,false),
('INF322','Base de Datos II',4,false),
('INF329','Compiladores',4,false),

-- SEM 7
('MAT419','Investigación Operativa II',4,false),
('INF418','Inteligencia Artificial',4,false),
('INF413','Sistemas Operativos II',4,false),
('INF433','Redes I',4,false),
('INF412','Sistemas de Información II',4,false),

-- SEM 8
('ECO449','Preparación y Evaluación de Proyectos',3,false),
('INF428','Sistemas Expertos',4,false),
('INF442','Sistemas de Información Geográfica',4,false),
('INF423','Redes II',4,false),
('INF422','Ingeniería de Software I',4,false),

-- SEM 9
('INF511','Taller de Grado I',3,false),
('INF512','Ingeniería de Software II',4,false),
('INF513','Tecnología Web',4,false),
('INF552','Arquitectura del Software',4,false),

-- SEM 10
('GRL001','Modalidad de Titulación / Licenciatura',0,false),

-- Electivas
('ELC101','Modelación y Simulación de Sistemas',4,true),
('ELC102','Programación Gráfica',4,true),
('ELC103','Tópicos Avanzados de Programación',4,true),
('ELC104','Programación de Aplicaciones de Tiempo Real',4,true),
('ELC105','Sistemas Distribuidos',4,true),
('ELC106','Interacción Hombre-Computador',4,true),
('ELC107','Criptografía y Seguridad',4,true),
('ELC108','Control y Automatización',4,true);

-- ============================================================
-- 🔗 PRERREQUISITOS (sin errores de integridad)
-- ============================================================

INSERT INTO prerequisito (sigla_prerequisito, sigla_materia) VALUES
         -- 2do. SEMESTRE
        ('MAT101','MAT102'),
        ('FIS100','FIS102'),
        ('LIN100','LIN101'),
        ('INF119','MAT103'),
        ('INF110','INF120'),
		
		 -- 3er. SEMESTRE
        ('INF120','INF210'),
        ('MAT103','INF210'),
        ('FIS102','INF211'),
        ('INF120','INF211'),
        ('MAT102','MAT207'),
        ('FIS102','FIS200'),
		
	     -- 4to. SEMESTRE
        ('ADM100','ADM200'),
        ('INF210','INF220'),
        ('MAT101','INF220'),
        ('INF211','INF221'),
        ('MAT102','MAT202'),
        ('MAT207','MAT205'),
		
        -- 5to. SEMESTRE
        ('INF220','INF310'),
        ('INF220','INF312'),
        ('INF220','INF318'),
        ('INF220','INF319'),
        ('MAT202','MAT302'),
		
		 -- 6to. SEMESTRE
        ('INF312','INF322'),
        ('INF310','INF323'),
        ('INF310','INF329'),
        ('INF319','INF329'),
        ('INF312','INF342'),
        ('MAT302','MAT329'),
		
		  -- 7mo. SEMESTRE
        ('INF322','INF412'),
        ('INF342','INF412'),
        ('INF323','INF413'),
        ('INF310','INF418'),
        ('INF318','INF418'),
        ('INF323','INF433'),
        ('MAT329','MAT419'),
		
		 -- 8vo. SEMESTRE
        ('MAT419','ECO449'),
        ('INF412','INF422'),
        ('INF433','INF423'),
        ('INF412','INF428'),
        ('INF418','INF428'),
        ('INF412','INF442'),
		
		 -- 9no. SEMESTRE 
        ('ECO449','INF511'),
        ('INF422','INF511'),
        ('INF423','INF511'),
        ('INF428','INF511'),
        ('INF442','INF511'),

        ('ECO449','INF512'),
        ('INF422','INF512'),
        ('INF423','INF512'),
        ('INF428','INF512'),
        ('INF442','INF512'),

        ('ECO449','INF513'),
        ('INF422','INF513'),
        ('INF423','INF513'),
        ('INF428','INF513'),
        ('INF442','INF513'),

        ('ECO449','INF552'),
        ('INF422','INF552'),
        ('INF423','INF552'),
        ('INF428','INF552'),
        ('INF442','INF552'),
		
       -- Modalidad de graduación 
	     ('INF511','GRL001'),
        ('INF512','GRL001'),
        ('INF513','GRL001'),
        ('INF552','GRL001');

-- ============================================================
-- 🧱 NIVELES (Semestres del 0 al 10)
-- ============================================================

INSERT INTO nivel (nivel)
SELECT generate_series(0, 10);

-- ============================================================
-- 🧑‍🏫 DOCENTES (3 por materia regular, 1 por electiva)
-- ============================================================

-- 🔹 Generar docentes para materias regulares (54 materias * 3 = 162 docentes aprox.)
INSERT INTO docente (codigo_docente, nombre, apellido, ci, correo, telefono)
VALUES
-- SEM 1
('DOC0001','María','Gonzales','700001','maria.gonzales@uagrm.edu.bo','70010001'),
('DOC0002','Carlos','Pérez','700002','carlos.perez@uagrm.edu.bo','70010002'),
('DOC0003','Lucía','Mendoza','700003','lucia.mendoza@uagrm.edu.bo','70010003'),
('DOC0004','Roberto','Flores','700004','roberto.flores@uagrm.edu.bo','70010004'),
('DOC0005','Ana','Vargas','700005','ana.vargas@uagrm.edu.bo','70010005'),
('DOC0006','Fernando','Roca','700006','fernando.roca@uagrm.edu.bo','70010006'),
('DOC0007','Roxana','Fernández','700007','roxana.fernandez@uagrm.edu.bo','70010007'),
('DOC0008','Héctor','Gómez','700008','hector.gomez@uagrm.edu.bo','70010008'),
('DOC0009','Sonia','Méndez','700009','sonia.mendez@uagrm.edu.bo','70010009'),
('DOC0010','Mario','Aguilera','700010','mario.aguilera@uagrm.edu.bo','70010010'),
('DOC0011','Verónica','Ruiz','700011','veronica.ruiz@uagrm.edu.bo','70010011'),
('DOC0012','David','Suárez','700012','david.suarez@uagrm.edu.bo','70010012'),
('DOC0013','Patricia','Guzmán','700013','patricia.guzman@uagrm.edu.bo','70010013'),
('DOC0014','Raúl','Montes','700014','raul.montes@uagrm.edu.bo','70010014'),
('DOC0015','Elena','Rojas','700015','elena.rojas@uagrm.edu.bo','70010015'),
('DOC0016','Javier','Molina','700016','javier.molina@uagrm.edu.bo','70010016'),
('DOC0017','Gabriela','Paz','700017','gabriela.paz@uagrm.edu.bo','70010017'),
('DOC0018','Pablo','Roca','700018','pablo.roca@uagrm.edu.bo','70010018'),
('DOC0019','Carla','Aguilar','700019','carla.aguilar@uagrm.edu.bo','70010019'),
('DOC0020','José','Rivera','700020','jose.rivera@uagrm.edu.bo','70010020'),
('DOC0021','Rosa','Camacho','700021','rosa.camacho@uagrm.edu.bo','70010021'),
('DOC0022','Luis','Soruco','700022','luis.soruco@uagrm.edu.bo','70010022'),
('DOC0023','Martha','Calderón','700023','martha.calderon@uagrm.edu.bo','70010023'),
('DOC0024','Alejandro','Castro','700024','alejandro.castro@uagrm.edu.bo','70010024'),
('DOC0025','Natalia','Soto','700025','natalia.soto@uagrm.edu.bo','70010025'),
('DOC0026','Julio','Fernández','700026','julio.fernandez@uagrm.edu.bo','70010026'),
('DOC0027','Liliana','Ruiz','700027','liliana.ruiz@uagrm.edu.bo','70010027'),
('DOC0028','Oscar','Campos','700028','oscar.campos@uagrm.edu.bo','70010028'),
('DOC0029','Silvia','Menacho','700029','silvia.menacho@uagrm.edu.bo','70010029'),
('DOC0030','Rodolfo','Villalobos','700030','rodolfo.villalobos@uagrm.edu.bo','70010030'),
('DOC0031','Beatriz','Ortiz','700031','beatriz.ortiz@uagrm.edu.bo','70010031'),
('DOC0032','Jorge','Salvatierra','700032','jorge.salvatierra@uagrm.edu.bo','70010032'),
('DOC0033','Carmen','Mamani','700033','carmen.mamani@uagrm.edu.bo','70010033'),
('DOC0034','Andrés','Roca','700034','andres.roca@uagrm.edu.bo','70010034'),
('DOC0035','Jessica','Gutiérrez','700035','jessica.gutierrez@uagrm.edu.bo','70010035'),
('DOC0036','Enrique','Ruiz','700036','enrique.ruiz@uagrm.edu.bo','70010036'),
('DOC0037','Andrea','Salazar','700037','andrea.salazar@uagrm.edu.bo','70010037'),
('DOC0038','Freddy','Molina','700038','freddy.molina@uagrm.edu.bo','70010038'),
('DOC0039','Carolina','Peredo','700039','carolina.peredo@uagrm.edu.bo','70010039'),
('DOC0040','Miguel','Vallejos','700040','miguel.vallejos@uagrm.edu.bo','70010040'),
('DOC0041','Estefanía','López','700041','estefania.lopez@uagrm.edu.bo','70010041'),
('DOC0042','Rodrigo','Arévalo','700042','rodrigo.arevalo@uagrm.edu.bo','70010042'),
('DOC0043','Nora','Carrasco','700043','nora.carrasco@uagrm.edu.bo','70010043'),
('DOC0044','Fabián','Montenegro','700044','fabian.montenegro@uagrm.edu.bo','70010044'),
('DOC0045','Paola','Pérez','700045','paola.perez@uagrm.edu.bo','70010045'),
('DOC0046','Hugo','Barba','700046','hugo.barba@uagrm.edu.bo','70010046'),
('DOC0047','Daniela','Velarde','700047','daniela.velarde@uagrm.edu.bo','70010047'),
('DOC0048','Rafael','Cruz','700048','rafael.cruz@uagrm.edu.bo','70010048'),
('DOC0049','Luciana','Becerra','700049','luciana.becerra@uagrm.edu.bo','70010049'),
('DOC0050','Víctor','Morales','700050','victor.morales@uagrm.edu.bo','70010050'),
('DOC0051','Karen','Téllez','700051','karen.tellez@uagrm.edu.bo','70010051'),
('DOC0052','Esteban','Quispe','700052','esteban.quispe@uagrm.edu.bo','70010052'),
('DOC0053','Patricia','Ortubé','700053','patricia.ortube@uagrm.edu.bo','70010053'),
('DOC0054','Eddy','Reyes','700054','eddy.reyes@uagrm.edu.bo','70010054'),
('DOC0055','Ruth','Mendoza','700055','ruth.mendoza@uagrm.edu.bo','70010055'),
('DOC0056','Carlos','Arancibia','700056','carlos.arancibia@uagrm.edu.bo','70010056'),
('DOC0057','Denise','Pereira','700057','denise.pereira@uagrm.edu.bo','70010057'),
('DOC0058','Víctor','Cárdenas','700058','victor.cardenas@uagrm.edu.bo','70010058'),
('DOC0059','Mónica','Rosales','700059','monica.rosales@uagrm.edu.bo','70010059'),
('DOC0060','Henry','Torrico','700060','henry.torrico@uagrm.edu.bo','70010060');

-- ============================================================
-- 🏫 AULAS — Módulo 236
-- ============================================================

INSERT INTO aula (codigo_aula, modulo, aula, capacidad, ubicacion) VALUES
('236A11','236','A11',40,'Módulo 236 - A11'),
('236A12','236','A12',40,'Módulo 236 - A12'),
('236A13','236','A13',40,'Módulo 236 - A13'),
('236A14','236','A14',40,'Módulo 236 - A14'),
('236A15','236','A15',40,'Módulo 236 - A15'),
('236A16','236','A16',40,'Módulo 236 - A16'),
('236A17','236','A17',40,'Módulo 236 - A17'),
('236A21','236','A21',40,'Módulo 236 - A21'),
('236A22','236','A22',40,'Módulo 236 - A22'),
('236A23','236','A23',40,'Módulo 236 - A23'),
('236A24','236','A24',40,'Módulo 236 - A24'),
('236A25','236','A25',40,'Módulo 236 - A25'),
('236A26','236','A26',40,'Módulo 236 - A26'),
('236A31','236','A31',40,'Módulo 236 - A31'),
('236A32','236','A32',40,'Módulo 236 - A32'),
('236A33','236','A33',40,'Módulo 236 - A33'),
('236A34','236','A34',40,'Módulo 236 - A34'),
('236A35','236','A35',40,'Módulo 236 - A35'),
('236A36','236','A36',40,'Módulo 236 - A36'),
('236L41','236','LAB41',25,'Módulo 236 - LAB41'),
('236L42','236','LAB42',25,'Módulo 236 - LAB42'),
('236L43','236','LAB43',25,'Módulo 236 - LAB43'),
('236L44','236','LAB44',25,'Módulo 236 - LAB44'),
('236L45','236','LAB45',25,'Módulo 236 - LAB45'),
('236L46','236','LAB46',25,'Módulo 236 - LAB46');

-- ============================================================
-- 🎓 ESTUDIANTES (10 estudiantes base)
-- ============================================================

INSERT INTO estudiante (codigo_carrera, registro_academico, nombre, apellido, ci, correo, contrasena, telefono, direccion, estado_academico)
VALUES
('INF187','RA0001','Jorge','Rojas','1234567','jorge.rojas@uagrm.edu.bo','1234567','70020001','Av. Busch #45','REGULAR'),
('INF187','RA0002','María','López','2345678','maria.lopez@uagrm.edu.bo','2345678','70020002','B/ San Jorge','REGULAR'),
('INF187','RA0003','Luis','Gutiérrez','3456789','luis.gutierrez@uagrm.edu.bo','3456789','70020003','Av. Centenario','REGULAR'),
('INF187','RA0004','Paola','Crespo','4567890','paola.crespo@uagrm.edu.bo','4567890','70020004','B/ Las Palmas','REGULAR'),
('INF187','RA0005','Carlos','Rivera','5678901','carlos.rivera@uagrm.edu.bo','5678901','70020005','Av. Alemana','REGULAR'),
('INF187','RA0006','Daniel','Torres','6789012','daniel.torres@uagrm.edu.bo','6789012','70020006','B/ Equipetrol','REGULAR'),
('INF187','RA0007','Sofía','Mendoza','7890123','sofia.mendoza@uagrm.edu.bo','7890123','70020007','Av. Santos Dumont','REGULAR'),
('INF187','RA0008','Andrea','Suárez','8901234','andrea.suarez@uagrm.edu.bo','8901234','70020008','Av. Mutualista','REGULAR'),
('INF187','RA0009','Kevin','López','9012345','kevin.lopez@uagrm.edu.bo','9012345','70020009','Av. Beni','REGULAR'),
('INF187','RA0010','Gabriela','Paz','1023456','gabriela.paz@uagrm.edu.bo','1023456','70020010','Av. Virgen de Luján','REGULAR');

-- ============================================================
-- 🔐 ENCRIPTACIÓN DE CONTRASEÑAS (basadas en CI)
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

UPDATE estudiante
SET contrasena = ENCODE(DIGEST(ci, 'sha256'), 'hex');

-- ============================================================
-- 🗓️ PERIODOS ACADÉMICOS
-- ============================================================
INSERT INTO periodo_academico (codigo_periodo, semestre, fecha_inicio, fecha_fin, estado)
VALUES 
    -- 2021
    ('1-2021','1/2021','2021-02-08','2021-07-18','FINALIZADO'),
    ('2-2021','2/2021','2021-08-02','2021-12-17','FINALIZADO'),

    -- 2022
    ('1-2022','1/2022','2022-02-07','2022-07-17','FINALIZADO'),
    ('2-2022','2/2022','2022-08-01','2022-12-16','FINALIZADO'),

    -- 2023
    ('1-2023','1/2023','2023-02-06','2023-07-16','FINALIZADO'),
    ('2-2023','2/2023','2023-08-07','2023-12-22','FINALIZADO'),

    -- 2024
    ('1-2024','1/2024','2024-02-05','2024-07-15','FINALIZADO'),
    ('2-2024','2/2024','2024-08-05','2024-12-20','FINALIZADO'),

    -- 2025
    ('1-2025','1/2025','2025-02-10','2025-10-30','ACTIVO'),
    ('2-2025','2/2025','2025-08-04','2025-12-20','FINALIZADO');

-- ============================================================
-- ⏰ HORARIOS (usando dias_semana)
-- ============================================================
INSERT INTO horario (codigo_horario, dias_semana, hora_inicio, hora_fin)
VALUES
-- Lunes, Miércoles, Viernes (1h30)
('H001','{LUN,MIE,VIE}','07:00','08:30'),
('H002','{LUN,MIE,VIE}','08:30','10:00'),
('H003','{LUN,MIE,VIE}','10:00','11:30'),
('H004','{LUN,MIE,VIE}','11:30','13:00'),
('H005','{LUN,MIE,VIE}','13:00','14:30'),
('H006','{LUN,MIE,VIE}','14:30','16:00'),
('H007','{LUN,MIE,VIE}','16:00','17:30'),
('H008','{LUN,MIE,VIE}','17:30','19:00'),
('H009','{LUN,MIE,VIE}','19:00','20:30'),
('H010','{LUN,MIE,VIE}','20:30','22:00'),

-- Martes, Jueves (2h15)
('H011','{MAR,JUE}','07:00','09:15'),
('H012','{MAR,JUE}','09:15','11:30'),
('H013','{MAR,JUE}','11:30','13:45'),
('H014','{MAR,JUE}','13:45','16:00'),
('H015','{MAR,JUE}','16:00','18:15'),
('H016','{MAR,JUE}','18:15','20:30'),
('H017','{MAR,JUE}','20:30','22:45');

ALTER TABLE grupo
ALTER COLUMN codigo_grupo TYPE VARCHAR(20);

-- ============================================================
-- 👩‍🏫 GRUPOS (ajustado a tu modelo)
-- ============================================================

-- Para este ejemplo: 3 grupos por materia regular y 1 por electiva.
-- Campos: codigo_grupo, sigla_materia, codigo_docente, codigo_aula, codigo_horario, descripcion, cupo, inscritos_actuales

DO $$
DECLARE 
    materias RECORD;
    docente_index INT := 1;
    aula_index INT := 1;
    horario_index INT := 1;
    cod_aula TEXT;
    cod_horario TEXT;
    cod_docente TEXT;
    letras TEXT[] := ARRAY['A','B','C'];
BEGIN
    -- === Materias regulares ===
    FOR materias IN SELECT sigla FROM materia WHERE es_electiva = false ORDER BY sigla LOOP
        FOR i IN 1..3 LOOP
            cod_docente := 'DOC' || LPAD(docente_index::TEXT,4,'0');
            cod_aula := (SELECT codigo_aula FROM aula ORDER BY codigo_aula LIMIT 1 OFFSET aula_index-1);
            cod_horario := (SELECT codigo_horario FROM horario ORDER BY codigo_horario LIMIT 1 OFFSET horario_index-1);

            INSERT INTO grupo (codigo_grupo, sigla_materia, codigo_docente, codigo_aula, codigo_horario, descripcion, cupo, inscritos_actuales)
            VALUES (
                'G-' || materias.sigla || '-' || letras[i],
                materias.sigla,
                cod_docente,
                cod_aula,
                cod_horario,
                'Grupo ' || letras[i] || ' - Periodo 2025-1',
                40,
                0
            );

            docente_index := docente_index + 1;
            aula_index := aula_index + 1;
            horario_index := horario_index + 1;
            IF docente_index > (SELECT COUNT(*) FROM docente) THEN docente_index := 1; END IF;
            IF aula_index > (SELECT COUNT(*) FROM aula) THEN aula_index := 1; END IF;
            IF horario_index > 10 THEN horario_index := 1; END IF;
        END LOOP;
    END LOOP;

    -- === Electivas (solo 1 grupo) ===
    aula_index := 1;
    horario_index := 11;
    FOR materias IN SELECT sigla FROM materia WHERE es_electiva = true ORDER BY sigla LOOP
        cod_docente := 'DOC' || LPAD(docente_index::TEXT,4,'0');
        cod_aula := (SELECT codigo_aula FROM aula ORDER BY codigo_aula LIMIT 1 OFFSET aula_index-1);
        cod_horario := (SELECT codigo_horario FROM horario ORDER BY codigo_horario LIMIT 1 OFFSET horario_index-11);

        INSERT INTO grupo (codigo_grupo, sigla_materia, codigo_docente, codigo_aula, codigo_horario, descripcion, cupo, inscritos_actuales)
        VALUES (
            'G-' || materias.sigla || '-E',
            materias.sigla,
            cod_docente,
            cod_aula,
            cod_horario,
            'Electiva - Periodo 2025-1',
            25,
            0
        );

        docente_index := docente_index + 1;
        aula_index := aula_index + 1;
        horario_index := horario_index + 1;
        IF docente_index > (SELECT COUNT(*) FROM docente) THEN docente_index := 1; END IF;
        IF aula_index > (SELECT COUNT(*) FROM aula) THEN aula_index := 1; END IF;
        IF horario_index > 17 THEN horario_index := 11; END IF;
    END LOOP;
END $$;

-- ============================================================
-- PLAN-MATERIA – Ingeniería Informática (Plan 187-3)
-- ============================================================

INSERT INTO plan_materia (codigo_plan, sigla_materia, nivel) VALUES
-- Semestre 1
('187-3','MAT101',1),
('187-3','INF119',1),
('187-3','INF110',1),
('187-3','FIS100',1),
('187-3','LIN100',1),

-- Semestre 2
('187-3','MAT102',2),
('187-3','MAT103',2),
('187-3','INF120',2),
('187-3','FIS102',2),
('187-3','LIN101',2),

-- Semestre 3
('187-3','MAT207',3),
('187-3','INF210',3),
('187-3','INF211',3),
('187-3','FIS200',3),
('187-3','ADM100',3),

-- Semestre 4
('187-3','MAT202',4),
('187-3','MAT205',4),
('187-3','INF220',4),
('187-3','INF221',4),
('187-3','ADM200',4),

-- Semestre 5
('187-3','MAT302',5),
('187-3','INF318',5),
('187-3','INF310',5),
('187-3','INF312',5),
('187-3','INF319',5),

-- Semestre 6
('187-3','MAT329',6),
('187-3','INF342',6),
('187-3','INF323',6),
('187-3','INF322',6),
('187-3','INF329',6),

-- Semestre 7
('187-3','MAT419',7),
('187-3','INF418',7),
('187-3','INF413',7),
('187-3','INF433',7),
('187-3','INF412',7),

-- Semestre 8
('187-3','ECO449',8),
('187-3','INF428',8),
('187-3','INF442',8),
('187-3','INF423',8),
('187-3','INF422',8),

-- Semestre 9
('187-3','INF511',9),
('187-3','INF512',9),
('187-3','INF513',9),
('187-3','INF552',9),

-- Semestre 10
('187-3','GRL001',10),

-- Electivas
('187-3','ELC101',0),
('187-3','ELC102',0),
('187-3','ELC103',0),
('187-3','ELC104',0),
('187-3','ELC105',0),
('187-3','ELC106',0),
('187-3','ELC107',0),
('187-3','ELC108',0);

-- Historial académico del estudiante RA0001
INSERT INTO historial_academico (registro_academico, sigla_materia, codigo_periodo, nota_final, estado, observacion)
VALUES
('RA0001', 'MAT101', '1-2021', 85.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'INF119', '1-2021', 90.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),
('RA0001', 'INF110', '1-2021', 88.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'FIS100', '1-2021', 80.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'LIN100', '1-2021', 92.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),

('RA0001', 'MAT102', '2-2021', 87.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'MAT103', '2-2021', 85.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'INF120', '2-2021', 91.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),
('RA0001', 'FIS102', '2-2021', 79.00, 'APROBADA', 'Materia aprobada con rendimiento regular'),
('RA0001', 'LIN101', '2-2021', 94.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),

('RA0001', 'MAT207', '1-2022', 85.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'INF210', '1-2022', 88.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'INF211', '1-2022', 87.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'FIS200', '1-2022', 90.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),
('RA0001', 'ADM100', '1-2022', 80.00, 'APROBADA', 'Materia aprobada con rendimiento regular'),

('RA0001', 'MAT202', '2-2022', 89.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'MAT205', '2-2022', 90.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),
('RA0001', 'INF220', '2-2022', 92.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),
('RA0001', 'INF221', '2-2022', 84.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'ADM200', '2-2022', 91.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),

('RA0001', 'MAT302', '1-2023', 86.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'INF318', '1-2023', 88.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'INF310', '1-2023', 89.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'INF312', '1-2023', 92.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),
('RA0001', 'INF319', '1-2023', 91.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),

('RA0001', 'MAT329', '2-2023', 84.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'INF342', '2-2023', 90.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),
('RA0001', 'INF323', '2-2023', 85.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'INF322', '2-2023', 92.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),
('RA0001', 'INF329', '2-2023', 89.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),

('RA0001', 'MAT419', '1-2024', 86.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'INF418', '1-2024', 90.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),
('RA0001', 'INF413', '1-2024', 88.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'INF433', '1-2024', 92.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),
('RA0001', 'INF412', '1-2024', 91.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),

('RA0001', 'ECO449', '2-2024', 90.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),
('RA0001', 'INF428', '2-2024', 88.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'INF442', '2-2024', 91.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),
('RA0001', 'INF423', '2-2024', 87.00, 'APROBADA', 'Materia aprobada con buen rendimiento'),
('RA0001', 'INF422', '2-2024', 93.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),

('RA0001', 'INF511', '1-2025', 90.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),
('RA0001', 'INF512', '1-2025', 91.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),
('RA0001', 'INF513', '1-2025', 93.00, 'APROBADA', 'Materia aprobada con excelente rendimiento'),
('RA0001', 'INF552', '1-2025', 90.00, 'APROBADA', 'Materia aprobada con excelente rendimiento');
    """
    
    cursor.execute(complete_sql)
    print("✅ Script SQL ejecutado exitosamente")

def main():
    """Función principal del seeder"""
    print("🌱 Iniciando seeder completo del microservicio estudiantil...")
    print(f"⏰ Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Preguntar al usuario si desea continuar
    print("🚨 ADVERTENCIA: Este script ejecutará el SQL completo.")
    print("   - Creará todas las tablas desde cero")
    print("   - Insertará todos los datos de ejemplo")
    print("   - Sobrescribirá datos existentes si los hay")
    print()
    
    respuesta = input("¿Desea continuar? (s/N): ").lower()
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Operación cancelada.")
        return
    
    conn = None
    try:
        # Conectar a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("🚀 Iniciando ejecución del script completo...")
        
        # Ejecutar todo el script SQL
        execute_complete_sql(cursor)
        
        # Confirmar cambios
        conn.commit()
        
        print("=" * 70)
        print("✅ Seeder completo ejecutado exitosamente!")
        print("📊 Verificando datos insertados:")
        
        # Mostrar estadísticas
        try:
            cursor.execute("SELECT COUNT(*) FROM carrera")
            print(f"   - Carreras: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT COUNT(*) FROM materia")
            print(f"   - Materias: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT COUNT(*) FROM docente")
            print(f"   - Docentes: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT COUNT(*) FROM estudiante")
            print(f"   - Estudiantes: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT COUNT(*) FROM grupo")
            print(f"   - Grupos: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT COUNT(*) FROM historial_academico")
            print(f"   - Registros historial: {cursor.fetchone()[0]}")
            
        except Exception as e:
            print(f"   ⚠️ Error al obtener estadísticas: {e}")
        
        print("=" * 70)
        print("🎉 Base de datos poblada correctamente!")
        print("📝 Todos los datos han sido insertados según el script proporcionado.")
        
    except psycopg2.Error as e:
        print(f"❌ Error de base de datos: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    main()