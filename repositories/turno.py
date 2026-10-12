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

def obtener_turnos_por_fecha(conexion, fecha_consulta: date) -> list[tuple]:
    """
    Recupera los turnos de una fecha para poblar la tabla del turnero.
    Retorna tuplas con el formato:
    (hora, cliente, paciente, especie, motivo, hc, ultimo_turno)
    """
    consulta = """
        SELECT 
            TO_CHAR(t.hora_inicio, 'HH24:MI') AS hora,
            CONCAT(c.nombre, ' ', c.apellido) AS cliente,
            p.nombre AS paciente,
            p.especie,
            t.motivo,
            p.id_paciente::TEXT AS hc,
            COALESCE(
                (
                    SELECT TO_CHAR(t_ant.fecha, 'DD/MM/YYYY')
                    FROM turno t_ant
                    WHERE t_ant.id_paciente = t.id_paciente
                      AND t_ant.fecha < t.fecha
                    ORDER BY t_ant.fecha DESC
                    LIMIT 1
                ),
                '-'
            ) AS ultimo_turno
        FROM turno t
        INNER JOIN paciente p ON t.id_paciente = p.id_paciente
        INNER JOIN cliente c ON p.dni = c.dni
        WHERE t.fecha = %s
          AND t.estado <> 'CANCELADO'
        ORDER BY t.hora_inicio ASC;
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (fecha_consulta,))
        return cursor.fetchall()