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