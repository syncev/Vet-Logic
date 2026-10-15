def obtener_historias(conexion):
    consulta = """
        SELECT
            cl.nombre || ' ' || cl.apellido AS cliente,
            p.nombre AS paciente,
            p.especie,
            p.id_paciente AS hc,
            cl.telefono AS contacto,
            MIN(co.fecha) AS primera_consulta,
            MAX(co.fecha) AS ultima_visita
        FROM paciente AS p
        JOIN cliente AS cl
            ON cl.dni = p.dni
        JOIN consulta AS co
            ON co.id_paciente = p.id_paciente
        GROUP BY
            p.id_paciente,
            p.nombre,
            p.especie,
            cl.nombre,
            cl.apellido,
            cl.telefono
        ORDER BY
            MAX(co.fecha) DESC,
            cl.apellido,
            cl.nombre,
            p.nombre
        LIMIT 10
    """

    with conexion.cursor() as cursor:
        cursor.execute(consulta)
        return cursor.fetchall()

def obtener_detalle_paciente(conexion, id_paciente):
    consulta = """
        SELECT
            cl.nombre,
            cl.apellido,
            cl.telefono,
            cl.domicilio,
            cl.dni,
            p.nombre,
            p.especie,
            p.fecha_nacimiento,
            p.sexo,
            p.castrado,
            p.peso
        FROM paciente AS p
        JOIN cliente AS cl
            ON cl.dni = p.dni
        WHERE p.id_paciente = %s
    """

    with conexion.cursor() as cursor:
        cursor.execute(consulta, (id_paciente,))
        return cursor.fetchone()

def obtener_consultas_paciente(conexion, id_paciente):
    consulta = """
        SELECT
            co.id_consulta,
            co.fecha,
            co.motivo_consulta,
            COALESCE(co.observaciones, ''),
            COALESCE(co.tratamiento, ''),
            v.matricula_veterinario,
            v.nombre || ' ' || v.apellido AS veterinario
        FROM consulta AS co
        JOIN veterinario AS v
            ON v.matricula_veterinario = co.matricula_veterinario
        WHERE co.id_paciente = %s
        ORDER BY co.fecha ASC, co.id_consulta ASC
    """

    with conexion.cursor() as cursor:
        cursor.execute(consulta, (id_paciente,))
        return cursor.fetchall()

def obtener_veterinarios_activos(conexion):
    consulta = """
        SELECT matricula_veterinario, nombre, apellido
        FROM veterinario
        WHERE estado = 'ACTIVO'
        ORDER BY apellido, nombre
    """

    with conexion.cursor() as cursor:
        cursor.execute(consulta)
        return cursor.fetchall()

def registrar_consulta(
    conexion,
    id_paciente,
    matricula_veterinario,
    notas,
    observaciones,
    tratamiento,
):
    consulta = """
        INSERT INTO consulta (
            fecha,
            motivo_consulta,
            observaciones,
            tratamiento,
            id_paciente,
            matricula_veterinario
        )
        VALUES (
            CURRENT_DATE,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id_consulta
    """
    valores = (
        notas,
        observaciones,
        tratamiento,
        id_paciente,
        matricula_veterinario,
    )

    with conexion.cursor() as cursor:
        cursor.execute(consulta, valores)
        return cursor.fetchone()[0]