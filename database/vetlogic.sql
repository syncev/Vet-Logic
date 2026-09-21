-- ============================================================
-- VetLogic - Estructura de la base de datos
-- ============================================================
-- Este archivo define la estructura de la base de datos.
-- En esta etapa no incluye datos de prueba ni conexión con Python.
-- ============================================================


-- ============================================================
-- 1. CLIENTE
-- ============================================================

CREATE TABLE cliente (
    dni VARCHAR(10) PRIMARY KEY,
    nombre_y_apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    mail VARCHAR(100),
    domicilio VARCHAR(150)
);


-- ============================================================
-- 2. PACIENTE
-- ============================================================

CREATE TABLE paciente (
    id_paciente INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    raza VARCHAR(50),
    especie VARCHAR(50) NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    sexo VARCHAR(20) NOT NULL,
    fecha_nacimiento DATE,
    peso VARCHAR(20) NOT NULL,
    estado_reproductivo VARCHAR(50),
    dni VARCHAR(10) NOT NULL,

    CONSTRAINT paciente_dni_fkey
        FOREIGN KEY (dni)
        REFERENCES cliente (dni)
);


-- ============================================================
-- 3. VETERINARIO
-- ============================================================

CREATE TABLE veterinario (
    matricula_veterinario VARCHAR(20) PRIMARY KEY,
    nombre_y_apellido VARCHAR(100) NOT NULL
);


-- ============================================================
-- 4. TURNO
-- ============================================================

CREATE TABLE turno (
    id_turno INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    motivo VARCHAR(200) NOT NULL,
    estado VARCHAR(20) NOT NULL,
    id_paciente INTEGER NOT NULL,
    matricula_veterinario VARCHAR(20) NOT NULL,

    CONSTRAINT turno_id_paciente_fkey
        FOREIGN KEY (id_paciente)
        REFERENCES paciente (id_paciente),

    CONSTRAINT turno_matricula_veterinario_fkey
        FOREIGN KEY (matricula_veterinario)
        REFERENCES veterinario (matricula_veterinario)
);


-- ============================================================
-- 5. CONSULTA
-- ============================================================

CREATE TABLE consulta (
    id_consulta INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fecha DATE NOT NULL,
    motivo_consulta VARCHAR(200) NOT NULL,
    examen_clinico TEXT,
    diagnostico TEXT,
    tratamiento TEXT,
    receta TEXT,
    id_paciente INTEGER NOT NULL,
    matricula_veterinario VARCHAR(20) NOT NULL,
    id_turno INTEGER,

    CONSTRAINT consulta_id_paciente_fkey
        FOREIGN KEY (id_paciente)
        REFERENCES paciente (id_paciente),

    CONSTRAINT consulta_matricula_veterinario_fkey
        FOREIGN KEY (matricula_veterinario)
        REFERENCES veterinario (matricula_veterinario),

    CONSTRAINT consulta_id_turno_fkey
        FOREIGN KEY (id_turno)
        REFERENCES turno (id_turno),

    CONSTRAINT consulta_id_turno_key
        UNIQUE (id_turno)
);