def obtener_historias(conexion, texto="", filtro="Todos"):
    condiciones = {
        "Cliente": "cl.nombre || ' ' || cl.apellido ILIKE %s",
        "Paciente": "p.nombre ILIKE %s",
        "Especie": "p.especie ILIKE %s",
        "HC": "p.id_paciente::text ILIKE %s",
        "Telefono": "cl.telefono ILIKE %s",
        "Motivo": """
            EXISTS (
                SELECT 1
                FROM consulta AS filtro_consulta
                WHERE filtro_consulta.id_paciente = p.id_paciente
                  AND filtro_consulta.motivo_consulta ILIKE %s
            )
        """,
    }

    parametros = []
    where = ""
    if texto:
        patron = f"%{texto}%"
        if filtro == "Todos":
            where = """
                WHERE (
                    cl.nombre || ' ' || cl.apellido ILIKE %s
                    OR p.nombre ILIKE %s
                    OR p.especie ILIKE %s
                    OR p.id_paciente::text ILIKE %s
                    OR cl.telefono ILIKE %s
                    OR EXISTS (
                        SELECT 1
                        FROM consulta AS filtro_consulta
                        WHERE filtro_consulta.id_paciente = p.id_paciente
                          AND filtro_consulta.motivo_consulta ILIKE %s
                    )
                )
            """
            parametros.extend([patron] * 6)
        else:
            condicion = condiciones.get(filtro)
            if condicion is None:
                raise ValueError(f"Filtro de historias desconocido: {filtro}")
            where = f"WHERE {condicion}"
            parametros.append(patron)

    consulta = f"""
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
        LEFT JOIN consulta AS co
            ON co.id_paciente = p.id_paciente
        {where}
        GROUP BY
            p.id_paciente,
            p.nombre,
            p.especie,
            cl.nombre,
            cl.apellido,
            cl.telefono
        ORDER BY
            MAX(co.fecha) DESC NULLS LAST,
            cl.apellido,
            cl.nombre,
            p.nombre
    """

    with conexion.cursor() as cursor:
        cursor.execute(consulta, parametros)
        return cursor.fetchall()


def registrar_cliente_y_paciente(
    conexion,
    dni,
    nombre_cliente,
    apellido_cliente,
    telefono,
    mail,
    domicilio,
    nombre_paciente,
    especie,
    raza,
    sexo,
):
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO cliente (dni, nombre, apellido, telefono, mail, domicilio)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (dni) DO NOTHING
            """,
            (
                dni,
                nombre_cliente,
                apellido_cliente,
                telefono,
                mail or None,
                domicilio or None,
            ),
        )
        cliente_creado = cursor.rowcount == 1
        cursor.execute(
            """
            INSERT INTO paciente (nombre, especie, raza, sexo, dni)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_paciente
            """,
            (
                nombre_paciente,
                especie,
                raza or None,
                sexo or None,
                dni,
            ),
        )
        return cursor.fetchone()[0], cliente_creado


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
    id_turno=None,
):
    with conexion.cursor() as cursor:
        if id_turno is not None:
            cursor.execute(
                """
                UPDATE turno
                SET estado = 'ATENDIDO'
                WHERE id_turno = %s
                    AND id_paciente = %s
                    AND fecha = CURRENT_DATE
                    AND estado = 'PENDIENTE'
                RETURNING id_turno
                """,
                (id_turno, id_paciente),
            )
            if cursor.fetchone() is None:
                raise ValueError(
                    "El turno ya no está pendiente o no corresponde a este paciente."
                )

        cursor.execute(
            """
            INSERT INTO consulta (
                fecha,
                motivo_consulta,
                observaciones,
                tratamiento,
                id_paciente,
                matricula_veterinario,
                id_turno
            )
            VALUES (
                CURRENT_DATE,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id_consulta
            """,
            (
                notas,
                observaciones,
                tratamiento,
                id_paciente,
                matricula_veterinario,
                id_turno,
            ),
        )
        return cursor.fetchone()[0]


def eliminar_paciente(conexion, id_paciente):
    with conexion.cursor() as cursor:
        cursor.execute(
            "DELETE FROM consulta WHERE id_paciente = %s",
            (id_paciente,),
        )
        cursor.execute(
            "DELETE FROM turno WHERE id_paciente = %s",
            (id_paciente,),
        )
        cursor.execute(
            """
            DELETE FROM paciente
            WHERE id_paciente = %s
            RETURNING id_paciente
            """,
            (id_paciente,),
        )
        return cursor.fetchone() is not None


def eliminar_cliente_de_paciente(conexion, id_paciente):
    with conexion.cursor() as cursor:
        cursor.execute(
            """
            SELECT cl.dni
            FROM cliente AS cl
            JOIN paciente AS p
                ON p.dni = cl.dni
            WHERE p.id_paciente = %s
            FOR UPDATE OF cl
            """,
            (id_paciente,),
        )
        fila = cursor.fetchone()
        if fila is None:
            return False

        dni = fila[0]
        cursor.execute(
            """
            DELETE FROM consulta
            WHERE id_paciente IN (
                SELECT id_paciente
                FROM paciente
                WHERE dni = %s
            )
            """,
            (dni,),
        )
        cursor.execute(
            "DELETE FROM turno WHERE id_paciente IN "
            "(SELECT id_paciente FROM paciente WHERE dni = %s)",
            (dni,),
        )
        cursor.execute(
            "DELETE FROM paciente WHERE dni = %s",
            (dni,),
        )
        cursor.execute(
            """
            DELETE FROM cliente
            WHERE dni = %s
            RETURNING dni
            """,
            (dni,),
        )
        return cursor.fetchone() is not None