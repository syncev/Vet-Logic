-- Migra el esquema inicial de Vet Logic al esquema actual sin borrar registros.
-- Ejecutar dentro de una transaccion y despues de crear un respaldo.

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM cliente
        WHERE btrim(nombre_y_apellido) = ''
           OR length(split_part(btrim(nombre_y_apellido), ' ', 1)) > 60
           OR length(
               CASE
                   WHEN position(' ' IN btrim(nombre_y_apellido)) > 0
                   THEN btrim(substring(
                       btrim(nombre_y_apellido)
                       FROM position(' ' IN btrim(nombre_y_apellido)) + 1
                   ))
                   ELSE ''
               END
           ) > 60
    ) THEN
        RAISE EXCEPTION 'Hay nombres de clientes vacios o demasiado largos.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM veterinario
        WHERE btrim(nombre_y_apellido) = ''
           OR length(split_part(btrim(nombre_y_apellido), ' ', 1)) > 60
           OR length(
               CASE
                   WHEN position(' ' IN btrim(nombre_y_apellido)) > 0
                   THEN btrim(substring(
                       btrim(nombre_y_apellido)
                       FROM position(' ' IN btrim(nombre_y_apellido)) + 1
                   ))
                   ELSE ''
               END
           ) > 60
    ) THEN
        RAISE EXCEPTION 'Hay nombres de veterinarios vacios o demasiado largos.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM paciente
        WHERE NULLIF(btrim(peso), '') IS NOT NULL
          AND btrim(peso) !~ '^[0-9]+([.,][0-9]{1,2})?$'
    ) THEN
        RAISE EXCEPTION 'Hay pesos que no se pueden convertir a NUMERIC(5,2).';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM paciente
        WHERE lower(btrim(estado_reproductivo)) NOT IN (
            'castrado', 'castrada', 'esterilizado', 'esterilizada',
            'si', 'sí', 'true', '1', 'entero', 'entera', 'no', 'false', '0'
        )
    ) THEN
        RAISE EXCEPTION 'Hay estados reproductivos sin conversion conocida.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM turno
        WHERE translate(upper(btrim(motivo)), 'áéíóúÁÉÍÓÚ', 'AEIOUAEIOU') NOT IN (
            'CLINICA', 'CONSULTA', 'VACUNACION', 'VACUNA',
            'CIRUGIA', 'OTRO', 'OTROS'
        )
           OR translate(upper(btrim(estado)), 'áéíóúÁÉÍÓÚ', 'AEIOUAEIOU') NOT IN (
               'PENDIENTE', 'ATENDIDO', 'COMPLETADO', 'COMPLETADA',
               'CANCELADO', 'CANCELADA', 'AUSENTE', 'NO ASISTIO'
           )
           OR hora_fin <= hora_inicio
           OR hora_fin <> hora_inicio + INTERVAL '40 minutes'
           OR hora_inicio NOT IN (
               TIME '09:00', TIME '09:40', TIME '10:20', TIME '11:00',
               TIME '11:40', TIME '12:20', TIME '16:00', TIME '16:40',
               TIME '17:20', TIME '18:00', TIME '18:40', TIME '19:20'
           )
    ) THEN
        RAISE EXCEPTION 'Hay turnos incompatibles con las reglas actuales.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM turno
        WHERE upper(btrim(estado)) <> 'CANCELADO'
        GROUP BY fecha, hora_inicio
        HAVING count(*) > 1
    ) THEN
        RAISE EXCEPTION 'Hay horarios activos duplicados en la misma fecha.';
    END IF;
END
$$;

ALTER TABLE paciente DROP CONSTRAINT paciente_dni_fkey;
ALTER TABLE consulta DROP CONSTRAINT consulta_matricula_veterinario_fkey;
ALTER TABLE turno DROP CONSTRAINT turno_matricula_veterinario_fkey;

ALTER TABLE cliente ADD COLUMN nombre VARCHAR(60);
ALTER TABLE cliente ADD COLUMN apellido VARCHAR(60);
UPDATE cliente
SET nombre = split_part(btrim(nombre_y_apellido), ' ', 1),
    apellido = CASE
        WHEN position(' ' IN btrim(nombre_y_apellido)) > 0
        THEN btrim(substring(
            btrim(nombre_y_apellido)
            FROM position(' ' IN btrim(nombre_y_apellido)) + 1
        ))
        ELSE ''
    END;
ALTER TABLE cliente ALTER COLUMN nombre SET NOT NULL;
ALTER TABLE cliente ALTER COLUMN apellido SET NOT NULL;
ALTER TABLE cliente ALTER COLUMN dni TYPE VARCHAR(20);
ALTER TABLE cliente ALTER COLUMN telefono TYPE VARCHAR(30);
ALTER TABLE cliente ALTER COLUMN mail TYPE VARCHAR(150);
ALTER TABLE cliente ALTER COLUMN domicilio TYPE VARCHAR(200);
ALTER TABLE cliente DROP COLUMN nombre_y_apellido;

ALTER TABLE veterinario ADD COLUMN nombre VARCHAR(60);
ALTER TABLE veterinario ADD COLUMN apellido VARCHAR(60);
ALTER TABLE veterinario ADD COLUMN contacto VARCHAR(30);
ALTER TABLE veterinario ADD COLUMN estado VARCHAR(10) NOT NULL DEFAULT 'ACTIVO';
ALTER TABLE veterinario ADD COLUMN especialidad VARCHAR(100);
ALTER TABLE veterinario ADD COLUMN domicilio VARCHAR(200);
ALTER TABLE veterinario ADD COLUMN correo VARCHAR(150);
ALTER TABLE veterinario ADD COLUMN contacto_emergencia VARCHAR(200);
UPDATE veterinario
SET nombre = split_part(btrim(nombre_y_apellido), ' ', 1),
    apellido = CASE
        WHEN position(' ' IN btrim(nombre_y_apellido)) > 0
        THEN btrim(substring(
            btrim(nombre_y_apellido)
            FROM position(' ' IN btrim(nombre_y_apellido)) + 1
        ))
        ELSE ''
    END,
    contacto = 'No informado';
ALTER TABLE veterinario ALTER COLUMN nombre SET NOT NULL;
ALTER TABLE veterinario ALTER COLUMN apellido SET NOT NULL;
ALTER TABLE veterinario ALTER COLUMN contacto SET NOT NULL;
ALTER TABLE veterinario ALTER COLUMN matricula_veterinario TYPE VARCHAR(30);
ALTER TABLE veterinario
    ADD CONSTRAINT ck_veterinario_estado
    CHECK (estado IN ('ACTIVO', 'INACTIVO'));

ALTER TABLE paciente ADD COLUMN castrado BOOLEAN;
UPDATE paciente
SET castrado = CASE lower(btrim(estado_reproductivo))
    WHEN 'castrado' THEN true
    WHEN 'castrada' THEN true
    WHEN 'esterilizado' THEN true
    WHEN 'esterilizada' THEN true
    WHEN 'si' THEN true
    WHEN 'sí' THEN true
    WHEN 'true' THEN true
    WHEN '1' THEN true
    WHEN 'entero' THEN false
    WHEN 'entera' THEN false
    WHEN 'no' THEN false
    WHEN 'false' THEN false
    WHEN '0' THEN false
END;
ALTER TABLE paciente ALTER COLUMN peso DROP NOT NULL;
ALTER TABLE paciente
    ALTER COLUMN peso TYPE NUMERIC(5,2)
    USING CASE
        WHEN NULLIF(btrim(peso), '') IS NULL THEN NULL
        ELSE replace(btrim(peso), ',', '.')::NUMERIC(5,2)
    END;
ALTER TABLE paciente ALTER COLUMN sexo DROP NOT NULL;
ALTER TABLE paciente ALTER COLUMN dni TYPE VARCHAR(20);
ALTER TABLE paciente DROP COLUMN estado_reproductivo;
ALTER TABLE paciente
    ADD CONSTRAINT fk_paciente_cliente
    FOREIGN KEY (dni) REFERENCES cliente(dni);

UPDATE turno
SET motivo = CASE translate(upper(btrim(motivo)), 'áéíóúÁÉÍÓÚ', 'AEIOUAEIOU')
        WHEN 'CLINICA' THEN 'CLINICA'
        WHEN 'CONSULTA' THEN 'CLINICA'
        WHEN 'VACUNA' THEN 'VACUNACION'
        WHEN 'VACUNACION' THEN 'VACUNACION'
        WHEN 'CIRUGIA' THEN 'CIRUGIA'
        WHEN 'OTRO' THEN 'OTROS'
        WHEN 'OTROS' THEN 'OTROS'
    END,
    estado = CASE translate(upper(btrim(estado)), 'áéíóúÁÉÍÓÚ', 'AEIOUAEIOU')
        WHEN 'PENDIENTE' THEN 'PENDIENTE'
        WHEN 'ATENDIDO' THEN 'ATENDIDO'
        WHEN 'COMPLETADO' THEN 'ATENDIDO'
        WHEN 'COMPLETADA' THEN 'ATENDIDO'
        WHEN 'CANCELADO' THEN 'CANCELADO'
        WHEN 'CANCELADA' THEN 'CANCELADO'
        WHEN 'AUSENTE' THEN 'AUSENTE'
        WHEN 'NO ASISTIO' THEN 'AUSENTE'
    END;
ALTER TABLE turno ALTER COLUMN motivo TYPE VARCHAR(20);
ALTER TABLE turno ALTER COLUMN estado TYPE VARCHAR(15);
ALTER TABLE turno ALTER COLUMN estado SET DEFAULT 'PENDIENTE';
ALTER TABLE turno ADD CONSTRAINT ck_turno_hora CHECK (hora_fin > hora_inicio);
ALTER TABLE turno
    ADD CONSTRAINT ck_turno_duracion
    CHECK (hora_fin = hora_inicio + INTERVAL '40 minutes');
ALTER TABLE turno
    ADD CONSTRAINT ck_turno_hora_inicio
    CHECK (hora_inicio IN (
        TIME '09:00', TIME '09:40', TIME '10:20', TIME '11:00',
        TIME '11:40', TIME '12:20', TIME '16:00', TIME '16:40',
        TIME '17:20', TIME '18:00', TIME '18:40', TIME '19:20'
    ));
ALTER TABLE turno
    ADD CONSTRAINT ck_turno_motivo
    CHECK (motivo IN ('CLINICA', 'VACUNACION', 'CIRUGIA', 'OTROS'));
ALTER TABLE turno
    ADD CONSTRAINT ck_turno_estado
    CHECK (estado IN ('PENDIENTE', 'ATENDIDO', 'CANCELADO', 'AUSENTE'));
ALTER TABLE turno DROP COLUMN matricula_veterinario;
CREATE UNIQUE INDEX uq_turno_fecha_hora_activo
    ON turno (fecha, hora_inicio)
    WHERE estado <> 'CANCELADO';

ALTER TABLE consulta ADD COLUMN observaciones TEXT;
UPDATE consulta
SET observaciones = NULLIF(concat_ws(
        E'\n',
        CASE WHEN NULLIF(btrim(examen_clinico), '') IS NOT NULL
            THEN 'Examen clinico: ' || btrim(examen_clinico) END,
        CASE WHEN NULLIF(btrim(diagnostico), '') IS NOT NULL
            THEN 'Diagnostico: ' || btrim(diagnostico) END
    ), ''),
    tratamiento = NULLIF(concat_ws(
        E'\n',
        NULLIF(btrim(tratamiento), ''),
        CASE WHEN NULLIF(btrim(receta), '') IS NOT NULL
            THEN 'Receta: ' || btrim(receta) END
    ), '');
ALTER TABLE consulta ALTER COLUMN matricula_veterinario TYPE VARCHAR(30);
ALTER TABLE consulta DROP COLUMN examen_clinico;
ALTER TABLE consulta DROP COLUMN diagnostico;
ALTER TABLE consulta DROP COLUMN receta;
ALTER TABLE consulta
    ADD CONSTRAINT fk_consulta_veterinario
    FOREIGN KEY (matricula_veterinario)
    REFERENCES veterinario(matricula_veterinario);