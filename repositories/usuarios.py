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
