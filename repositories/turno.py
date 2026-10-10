from datetime import date, timedelta


def obtener_horarios_ocupados(conexion, fecha_base: date):
    fecha_final = fecha_base + timedelta(days=2)

    consulta = """
        SELECT fecha, hora_inicio
        FROM turno
        WHERE fecha BETWEEN %s AND %s
          AND estado <> 'CANCELADO'
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (fecha_base, fecha_final))
        filas = cursor.fetchall()

    return {
        (fecha, hora.strftime("%H:%M"))
        for fecha, hora in filas
    }