def obtener_profesionales_activos(conexion):
    consulta = """
        SELECT matricula_veterinario, nombre, apellido, estado, contacto,
            especialidad, domicilio, correo, contacto_emergencia
        FROM veterinario
        WHERE estado = 'ACTIVO'
        ORDER BY apellido, nombre, matricula_veterinario
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta)
        return cursor.fetchall()


def crear_profesional(
    conexion,
    matricula,
    nombre,
    apellido,
    contacto,
    especialidad,
    domicilio,
    correo,
    contacto_emergencia,
):
    consulta = """
        INSERT INTO veterinario
        (matricula_veterinario, nombre, apellido, contacto, estado,
         especialidad, domicilio, correo, contacto_emergencia)
        VALUES (%s, %s, %s, %s, 'ACTIVO', %s, %s, %s, %s)
    """
    valores = (
        matricula,
        nombre,
        apellido,
        contacto,
        especialidad,
        domicilio,
        correo,
        contacto_emergencia,
    )

    with conexion.cursor() as cursor:
        cursor.execute(consulta, valores)


def inhabilitar_profesional(conexion, matricula):
    consulta = """
        UPDATE veterinario
        SET estado = 'INACTIVO'
        WHERE matricula_veterinario = %s
          AND estado = 'ACTIVO'
    """

    with conexion.cursor() as cursor:
        cursor.execute(consulta, (matricula,))
        return cursor.rowcount


def actualizar_profesional(
    conexion,
    matricula,
    nombre,
    domicilio,
    contacto,
    correo,
    contacto_emergencia,
):
    consulta = """
        UPDATE veterinario
        SET nombre = %s,
            domicilio = %s,
            contacto = %s,
            correo = %s,
            contacto_emergencia = %s
        WHERE matricula_veterinario = %s
    """
    valores = (
        nombre,
        domicilio,
        contacto,
        correo,
        contacto_emergencia,
        matricula,
    )

    with conexion.cursor() as cursor:
        cursor.execute(consulta, valores)
        return cursor.rowcount
