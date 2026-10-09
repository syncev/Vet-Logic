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
    domicilio VARCHAR(200)
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
    matricula_veterinario VARCHAR(20) NOT NULL,

    CONSTRAINT turno_id_paciente_fkey
        FOREIGN KEY (id_paciente)
        REFERENCES paciente (id_paciente),

    CONSTRAINT turno_matricula_veterinario_fkey
        FOREIGN KEY (matricula_veterinario)
        REFERENCES veterinario (matricula_veterinario),

    CONSTRAINT turno_hora_fin_posterior_inicio_check
        CHECK (hora_fin > hora_inicio)
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