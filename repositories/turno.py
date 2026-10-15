from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


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
            t.id_turno
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
          # aca chicos saque CANCELADO porque postgresql ocultaba y descartaba raiz cualquier turno que estuviera CANCELADO, y no nos sirve para el turnero.
        ORDER BY t.hora_inicio ASC;
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (fecha_consulta,))
        return cursor.fetchall()

def resolver_estado_visual(fecha_turno: date, hora_inicio_str: str, estado_bd: str) -> tuple[str, str]:
   
    estado_normalizado = (estado_bd or "PENDIENTE").upper()

    if estado_normalizado in ("ATENDIDO", "COMPLETADO"):
        return ("Completado", "🟢")
    
    if estado_normalizado == "CANCELADO":
        return ("Cancelado", "🔴")

    ahora = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
    hoy = ahora.date()

    if fecha_turno == hoy:
        try:
            hora_turno = datetime.strptime(hora_inicio_str, "%H:%M").time()
            dt_turno = datetime.combine(hoy, hora_turno).replace(tzinfo=ahora.tzinfo)
            diferencia_minutos = (dt_turno - ahora).total_seconds() / 60

            # Esto chicos es la logica de los 40 minutos que pactamos   
            if -40 <= diferencia_minutos <= 40:
                return ("Próximo", "🟡")
        except ValueError:
            pass

    return ("Pendiente", "⚪")