-- VetLogic - Esquema definitivo de Base de Datos - PostgreSQL
-- NOTA: recrea las tablas. Usar sobre una base de prueba o con respaldo previo.

DROP TABLE IF EXISTS consulta CASCADE;
DROP TABLE IF EXISTS turno CASCADE;
DROP TABLE IF EXISTS paciente CASCADE;
DROP TABLE IF EXISTS veterinario CASCADE;
DROP TABLE IF EXISTS cliente CASCADE;

CREATE TABLE cliente (
    dni VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    apellido VARCHAR(60) NOT NULL,
    telefono VARCHAR(30) NOT NULL,
    mail VARCHAR(150),
    domicilio VARCHAR(200),
    estado VARCHAR(10) NOT NULL DEFAULT 'ACTIVO',
    CONSTRAINT ck_cliente_estado
        CHECK (estado IN ('ACTIVO', 'INACTIVO'))
);

CREATE TABLE veterinario (
    matricula_veterinario VARCHAR(30) PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    apellido VARCHAR(60) NOT NULL,
    contacto VARCHAR(30) NOT NULL,
    estado VARCHAR(10) NOT NULL DEFAULT 'ACTIVO',
    especialidad VARCHAR(100),
    domicilio VARCHAR(200),
    correo VARCHAR(150),
    contacto_emergencia VARCHAR(200),
    CONSTRAINT ck_veterinario_estado CHECK (estado IN ('ACTIVO', 'INACTIVO'))
);

CREATE TABLE paciente (
    id_paciente INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    especie VARCHAR(50) NOT NULL,
    raza VARCHAR(80),
    sexo VARCHAR(20),
    fecha_nacimiento DATE,
    peso NUMERIC(5,2),
    castrado BOOLEAN,
    dni VARCHAR(20) NOT NULL,
    estado VARCHAR(10) NOT NULL DEFAULT 'ACTIVO',
    CONSTRAINT ck_paciente_estado CHECK (estado IN ('ACTIVO', 'INACTIVO')),
    CONSTRAINT fk_paciente_cliente FOREIGN KEY (dni) REFERENCES cliente(dni)
);

CREATE TABLE turno (
    id_turno INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    motivo VARCHAR(20) NOT NULL,
    estado VARCHAR(15) NOT NULL DEFAULT 'PENDIENTE',
    id_paciente INTEGER NOT NULL,
    CONSTRAINT fk_turno_paciente FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente),
    CONSTRAINT ck_turno_hora CHECK (hora_fin > hora_inicio),
    CONSTRAINT ck_turno_duracion CHECK (hora_fin = hora_inicio + INTERVAL '40 minutes'),
    CONSTRAINT ck_turno_hora_inicio CHECK (hora_inicio IN (
        TIME '09:00', TIME '09:40', TIME '10:20', TIME '11:00', TIME '11:40', TIME '12:20',
        TIME '16:00', TIME '16:40', TIME '17:20', TIME '18:00', TIME '18:40', TIME '19:20'
    )),
    CONSTRAINT ck_turno_motivo CHECK (motivo IN ('CLINICA', 'VACUNACION', 'CIRUGIA', 'OTROS')),
    CONSTRAINT ck_turno_estado CHECK (estado IN ('PENDIENTE', 'ATENDIDO', 'CANCELADO', 'AUSENTE'))
);

-- Un solo turno activo por fecha y horario. CANCELADO libera el horario.
CREATE UNIQUE INDEX uq_turno_fecha_hora_activo
    ON turno (fecha, hora_inicio)
    WHERE estado <> 'CANCELADO';

CREATE TABLE consulta (
    id_consulta INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fecha DATE NOT NULL,
    motivo_consulta VARCHAR(200) NOT NULL,
    observaciones TEXT,
    tratamiento TEXT,
    id_paciente INTEGER NOT NULL,
    matricula_veterinario VARCHAR(30) NOT NULL,
    id_turno INTEGER UNIQUE,
    CONSTRAINT fk_consulta_paciente FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente),
    CONSTRAINT fk_consulta_veterinario FOREIGN KEY (matricula_veterinario) REFERENCES veterinario(matricula_veterinario),
    CONSTRAINT fk_consulta_turno FOREIGN KEY (id_turno) REFERENCES turno(id_turno)
);

-- Reglas a implementar en la aplicación:
-- 1) Al registrar CONSULTA con turno, verificar que el paciente coincida.
-- 2) Al registrar CONSULTA con turno, cambiar automáticamente TURNO a ATENDIDO.
-- 3) CONSULTA.id_turno puede ser NULL para atenciones sin turno.
-- 4) TURNO puede no generar CONSULTA si queda CANCELADO o AUSENTE.
-- 5) No existe relación VETERINARIO-TURNO.
-- 6) Baja de veterinario = cambio a INACTIVO; se conserva el historial.
-- 7) No se almacena rol porque actualmente no determina permisos/procesos.


-- Insertar datos de prueba para Vetlogic

-- 1. Tabla cliente
INSERT INTO cliente (dni, nombre, apellido, telefono, mail, domicilio) VALUES
('12345678', 'Silvia', 'Moreno', '1122334455', 'silvia.moreno@gmail.com', 'Av. Corrientes 1234'),
('23456789', 'Martin', 'Sanchez', '1133445566', 'martin.sanchez@hotmail.com', 'Calle Falsa 123'),
('34567890', 'Calvin', 'Klein', '1144556677', 'calvin@fashion.com', 'Av. Libertador 4500'),
('45678901', 'Clark', 'Kent', '1155667788', 'clark.kent@dailyplanet.com', 'Metrópolis 987'),
('56789012', 'Maria', 'del Barrio', '1166778899', 'mariadelbarrio@yahoo.com', 'Rivadavia 7890'),
('67890123', 'Esteban', 'Caracas', '1177889900', 'esteban.caracas@gmail.com', 'Suipacha 450'),
('78901234', 'Philomena', 'Cunk', '1188990011', 'cunk@bbc.co.uk', 'Belgrano 321'),
('89012345', 'Lydia', 'Deetz', '1199001122', 'lydia.art@gmail.com', 'San Juan 654'),
('90123456', 'Sabrina', 'Carpintera', '1122112211', 'sabrina@music.com', 'Mitre 1500'),
('01234567', 'Britney', 'Lanzas', '1133223322', 'britney@pop.com', 'Pueyrredón 888');

-- 2. Tabla veterinario
INSERT INTO veterinario (matricula_veterinario, nombre, apellido, contacto, estado, especialidad, domicilio, correo, contacto_emergencia) VALUES
('MP-1234', 'Carlos', 'Gómez', '1144556677', 'ACTIVO', 'Clinica General', 'Mitre 100', 'carlos@vet.com', 'Emergencia 1'),
('MP-2345', 'María', 'Pérez', '1155667788', 'ACTIVO', 'Cirugía', 'Belgrano 200', 'maria@vet.com', 'Emergencia 2'),
('MP-3456', 'Esteban', 'Quito', '1166778899', 'ACTIVO', 'Dermatología', 'San Martin 300', 'esteban@vet.com', 'Emergencia 3'),
('MP-4567', 'Lucía', 'Fernández', '1177889900', 'ACTIVO', 'Felinos', 'Rivadavia 400', 'lucia@vet.com', 'Emergencia 4'),
('MP-5678', 'Martín', 'Bosco', '1188990011', 'ACTIVO', 'Traumatología', 'Alvear 500', 'martin@vet.com', 'Emergencia 5'),
('MP-6789', 'Valeria', 'Mazza', '1199001122', 'ACTIVO', 'Cardiología', 'Sarmiento 600', 'valeria@vet.com', 'Emergencia 6'),
('MP-7890', 'Jorge', 'Rivas', '1122334455', 'ACTIVO', 'Oftalmología', 'Urquiza 700', 'jorge@vet.com', 'Emergencia 7'),
('MP-8901', 'Ana', 'Sosa', '1133445566', 'ACTIVO', 'Neurología', 'España 800', 'ana@vet.com', 'Emergencia 8'),
('MP-9012', 'Federico', 'López', '1144332211', 'ACTIVO', 'Oncología', 'Ituzaingó 900', 'federico@vet.com', 'Emergencia 9'),
('MP-0123', 'Sofía', 'Díaz', '1155443322', 'ACTIVO', 'Exóticos', 'Paso 1000', 'sofia@vet.com', 'Emergencia 10');

-- 3. Tabla paciente
INSERT INTO paciente (nombre, especie, raza, sexo, fecha_nacimiento, peso, castrado, dni) VALUES
('Luna', 'Gato', 'Siamés', 'Hembra', '2023-01-15', 4.20, true, '12345678'),
('Milo', 'Gato', 'Shorthair', 'Macho', '2024-05-10', 3.80, false, '23456789'),
('Thor', 'Perro', 'Ovejero Alemán', 'Macho', '2021-08-20', 28.50, true, '34567890'),
('Homero', 'Perro', 'Golden Retriever', 'Macho', '2022-03-12', 30.00, true, '45678901'),
('Otto', 'Gato', 'Persa', 'Macho', '2020-11-05', 5.10, true, '56789012'),
('Rafa', 'Perro', 'Caniche', 'Macho', '2023-09-01', 6.50, false, '67890123'),
('Ara', 'Gato', 'Angora', 'Hembra', '2024-02-14', 3.20, false, '78901234'),
('Uma', 'Perro', 'Pitbull', 'Hembra', '2022-07-30', 24.00, true, '89012345'),
('Corcho', 'Perro', 'Beagle', 'Macho', '2019-12-10', 12.00, true, '90123456'),
('Simba', 'Gato', 'Maine Coon', 'Macho', '2021-06-25', 7.50, true, '01234567');

-- 4. Tabla turno
INSERT INTO turno (fecha, hora_inicio, hora_fin, motivo, estado, id_paciente) VALUES
('2026-08-12', '09:00:00', '09:40:00', 'CLINICA', 'ATENDIDO', 1),
('2026-09-01', '09:40:00', '10:20:00', 'CLINICA', 'ATENDIDO', 2),
('2026-10-09', '10:20:00', '11:00:00', 'CIRUGIA', 'ATENDIDO', 3),
('2026-09-15', '11:00:00', '11:40:00', 'VACUNACION', 'ATENDIDO', 4),
('2026-11-23', '11:40:00', '12:20:00', 'CLINICA', 'PENDIENTE', 5),
('2026-10-30', '16:00:00', '16:40:00', 'CLINICA', 'CANCELADO', 6),
('2026-11-20', '16:40:00', '17:20:00', 'CLINICA', 'PENDIENTE', 7),
('2026-10-16', '17:20:00', '18:00:00', 'VACUNACION', 'PENDIENTE', 8),
('2026-07-09', '18:00:00', '18:40:00', 'CLINICA', 'ATENDIDO', 9),
('2026-12-22', '18:40:00', '19:20:00', 'CLINICA', 'PENDIENTE', 10),
('2026-10-01', '10:20:00', '11:00:00', 'CLINICA', 'ATENDIDO', 1),
('2026-10-02', '16:40:00', '17:20:00', 'VACUNACION', 'ATENDIDO', 2),
('2026-10-05', '11:00:00', '11:40:00', 'CIRUGIA', 'ATENDIDO', 3),
('2026-10-06', '18:00:00', '18:40:00', 'CLINICA', 'ATENDIDO', 4),
('2026-10-07', '10:20:00', '11:00:00', 'VACUNACION', 'ATENDIDO', 5),
('2026-10-08', '12:20:00', '13:00:00', 'CLINICA', 'ATENDIDO', 6),
('2026-10-12', '09:40:00', '10:20:00', 'CLINICA', 'ATENDIDO', 7),
('2026-10-13', '16:00:00', '16:40:00', 'CIRUGIA', 'ATENDIDO', 8),
('2026-10-14', '09:00:00', '09:40:00', 'CLINICA', 'ATENDIDO', 9),
('2026-10-15', '10:20:00', '11:00:00', 'VACUNACION', 'ATENDIDO', 10),
('2026-10-19', '11:40:00', '12:20:00', 'CIRUGIA', 'PENDIENTE', 1),
('2026-10-20', '18:40:00', '19:20:00', 'CLINICA', 'PENDIENTE', 2),
('2026-10-21', '09:00:00', '09:40:00', 'CLINICA', 'PENDIENTE', 3),
('2026-10-22', '10:20:00', '11:00:00', 'VACUNACION', 'PENDIENTE', 4),
('2026-10-23', '16:40:00', '17:20:00', 'CIRUGIA', 'PENDIENTE', 5),
('2026-10-26', '18:00:00', '18:40:00', 'OTROS', 'PENDIENTE', 6),
('2026-10-27', '09:40:00', '10:20:00', 'CLINICA', 'PENDIENTE', 7),
('2026-10-28', '12:20:00', '13:00:00', 'VACUNACION', 'PENDIENTE', 8),
('2026-10-29', '16:00:00', '16:40:00', 'CLINICA', 'PENDIENTE', 9),
('2026-11-02', '18:40:00', '19:20:00', 'OTROS', 'PENDIENTE', 10),
('2026-11-03', '09:00:00', '09:40:00', 'VACUNACION', 'PENDIENTE', 1),
('2026-11-04', '11:00:00', '11:40:00', 'CLINICA', 'PENDIENTE', 2),
('2026-11-05', '16:40:00', '17:20:00', 'VACUNACION', 'PENDIENTE', 3),
('2026-11-06', '18:00:00', '18:40:00', 'CLINICA', 'PENDIENTE', 4),
('2026-11-09', '09:40:00', '10:20:00', 'CLINICA', 'PENDIENTE', 5),
('2026-11-10', '12:20:00', '13:00:00', 'CIRUGIA', 'PENDIENTE', 6),
('2026-11-11', '16:00:00', '16:40:00', 'VACUNACION', 'PENDIENTE', 7),
('2026-11-12', '19:20:00', '20:00:00', 'CLINICA', 'PENDIENTE', 8),
('2026-11-13', '10:20:00', '11:00:00', 'CLINICA', 'PENDIENTE', 9),
('2026-11-16', '16:00:00', '16:40:00', 'VACUNACION', 'PENDIENTE', 10),
('2026-11-17', '17:20:00', '18:00:00', 'CIRUGIA', 'PENDIENTE', 1),
('2026-11-18', '18:40:00', '19:20:00', 'CLINICA', 'PENDIENTE', 2),
('2026-11-19', '09:00:00', '09:40:00', 'CLINICA', 'PENDIENTE', 3),
('2026-11-24', '10:20:00', '11:00:00', 'VACUNACION', 'PENDIENTE', 4),
('2026-11-25', '16:40:00', '17:20:00', 'CLINICA', 'PENDIENTE', 5),
('2026-11-26', '19:20:00', '20:00:00', 'OTROS', 'PENDIENTE', 6),
('2026-11-27', '10:20:00', '11:00:00', 'CLINICA', 'PENDIENTE', 7),
('2026-11-30', '11:40:00', '12:20:00', 'VACUNACION', 'PENDIENTE', 8),
('2026-12-01', '16:40:00', '17:20:00', 'CIRUGIA', 'PENDIENTE', 9),
('2026-12-02', '19:20:00', '20:00:00', 'OTROS', 'PENDIENTE', 10),
('2026-12-03', '09:00:00', '09:40:00', 'CLINICA', 'PENDIENTE', 1),
('2026-12-04', '12:20:00', '13:00:00', 'VACUNACION', 'PENDIENTE', 2),
('2026-12-07', '17:20:00', '18:00:00', 'CLINICA', 'PENDIENTE', 3),
('2026-12-08', '18:40:00', '19:20:00', 'CIRUGIA', 'PENDIENTE', 4),
('2026-12-09', '09:40:00', '10:20:00', 'CLINICA', 'PENDIENTE', 5),
('2026-12-10', '11:40:00', '12:20:00', 'VACUNACION', 'PENDIENTE', 6),
('2026-12-11', '16:40:00', '17:20:00', 'CIRUGIA', 'PENDIENTE', 7),
('2026-12-14', '19:20:00', '20:00:00', 'CLINICA', 'PENDIENTE', 8),
('2026-12-15', '10:20:00', '11:00:00', 'CLINICA', 'PENDIENTE', 9),
('2026-12-16', '12:20:00', '13:00:00', 'VACUNACION', 'PENDIENTE', 10),
('2026-12-17', '16:00:00', '16:40:00', 'CIRUGIA', 'PENDIENTE', 1),
('2026-12-18', '18:40:00', '19:20:00', 'CLINICA', 'PENDIENTE', 2);

-- 5. Tabla consulta
INSERT INTO consulta (fecha, motivo_consulta, observaciones, tratamiento, id_paciente, matricula_veterinario, id_turno) VALUES
('2026-10-15', 'Cirugía programada de esterilización', 'Ayuno previo completado', 'Medicación post-quirúrgica', 1, 'MP-3456', 1),
('2026-11-06', 'Aplicación de vacuna anual', 'Paciente tranquilo', 'Dosis séxtuple aplicada', 2, 'MP-4567', 2),
('2026-09-25', 'Cirugía programada de esterilización', 'Ayuno previo completado', 'Medicación post-quirúrgica', 3, 'MP-3456', 3),
('2026-11-05', 'Aplicación de vacuna anual', 'Paciente tranquilo', 'Dosis séxtuple aplicada', 4, 'MP-4567', 4),
('2026-06-07', 'Control preventivo general', 'Buen estado general de salud', 'Ninguno', 5, 'MP-5678', 5),
('2026-08-19', 'Gastroenteritis leve por dieta', 'Vómitos ocasionales', 'Dieta blanda y protector gástrico', 6, 'MP-6789', 6),
('2026-04-21', 'Chequeo dermatológico', 'Alergia estacional leve', 'Baño con shampoo medicado', 7, 'MP-7890', 7),
('2026-05-30', 'Vacunación antirrábica', 'Sin reacciones adversas', 'Aplicación correcta', 8, 'MP-8901', 8),
('2026-07-15', 'Revisión oftalmológica', 'Ojos limpios y sin lesiones', 'Gotas lubricantes', 9, 'MP-9012', 9),
('2026-05-12', 'Control geriátrico preventivo', 'Se solicitan análisis de sangre', 'Vitaminas y suplementos', 10, 'MP-0123', 10);