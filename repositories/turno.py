from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from core.db import conectar

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
    (id_turno, hora, cliente, paciente, especie, motivo, hc, ultimo_turno, estado)
    """
    marcar_turnos_ausentes(conexion)
    
    consulta = """
        SELECT 
            t.id_turno,
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
            ) AS ultimo_turno,
            t.estado
        FROM turno t
        INNER JOIN paciente p ON t.id_paciente = p.id_paciente
        INNER JOIN cliente c ON p.dni = c.dni
        WHERE t.fecha = %s
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

    if estado_normalizado == "AUSENTE":
        return ("Ausente", "🔴")
    
    ahora = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
    hoy = ahora.date()

    if fecha_turno == hoy:
        try:
            hora_turno = datetime.strptime(hora_inicio_str, "%H:%M").time()
            dt_turno = datetime.combine(hoy, hora_turno).replace(tzinfo=ahora.tzinfo)
            diferencia_minutos = (dt_turno - ahora).total_seconds() / 60

            # Lógica de los 40 minutos
            if -40 <= diferencia_minutos <= 40:
                return ("Próximo", "🟡")
        except ValueError:
            pass

    return ("Pendiente", "⚪")

def actualizar_estado_turno(conexion, id_turno: int, nuevo_estado: str):
    """
    Actualiza el estado de un turno en PostgreSQL ('PENDIENTE', 'ATENDIDO', 'CANCELADO', 'AUSENTE').
    """
    estados_validos = ("PENDIENTE", "ATENDIDO", "CANCELADO", "AUSENTE")
    estado_limpio = nuevo_estado.strip().upper()

    if estado_limpio not in estados_validos:
        raise ValueError(
            f"Estado inválido: {nuevo_estado}. Valores permitidos: {estados_validos}"
        )

    consulta = """
        UPDATE turno
        SET estado = %s
        WHERE id_turno = %s;
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (estado_limpio, id_turno))
    conexion.commit()

def registrar_turno_con_paciente_nuevo(conexion, datos: dict) -> dict:
    """
    Registra cliente (si no existe), nuevo paciente (generando automáticamente su HC incremental)
    y el turno correspondiente cumpliendo las restricciones del esquema SQL.
    Retorna los IDs generados: id_paciente (HC) e id_turno.
    """
    dni = datos["dni"].strip()
    nombre_cliente = datos.get("cliente_nombre", "").strip()
    apellido_cliente = datos.get("cliente_apellido", "").strip()
    telefono = datos.get("contacto", "").strip() or "No informado"

    nombre_paciente = datos["paciente"].strip()
    especie = datos.get("especie", "Otro").strip()
    raza = datos.get("raza", "").strip() or None

    fecha = datos["fecha"]
    hora_inicio_str = datos["hora"]
    motivo = datos.get("motivo", "CLINICA").strip().upper()
    if motivo not in ("CLINICA", "VACUNACION", "CIRUGIA", "OTROS"):
        motivo = "CLINICA"

    # Cálculo de hora fin (40 minutos para respetar la restricción ck_turno_duracion)
    hora_dt = datetime.strptime(hora_inicio_str, "%H:%M")
    hora_fin_str = (hora_dt + timedelta(minutes=40)).strftime("%H:%M")

    with conexion.cursor() as cursor:
        # 1. Registrar o actualizar cliente por DNI
        cursor.execute(
            """
            INSERT INTO cliente (dni, nombre, apellido, telefono)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (dni) DO UPDATE
            SET telefono = EXCLUDED.telefono;
            """,
            (dni, nombre_cliente, apellido_cliente, telefono)
        )

        # 2. Registrar el paciente: id_paciente se genera con IDENTITY (incremental único = HC)
        cursor.execute(
            """
            INSERT INTO paciente (nombre, especie, raza, dni)
            VALUES (%s, %s, %s, %s)
            RETURNING id_paciente;
            """,
            (nombre_paciente, especie, raza, dni)
        )
        id_paciente = cursor.fetchone()[0]

        # 3. Registrar el turno vinculado al paciente recién creado
        cursor.execute(
            """
            INSERT INTO turno (fecha, hora_inicio, hora_fin, motivo, estado, id_paciente)
            VALUES (%s, %s, %s, %s, 'PENDIENTE', %s)
            RETURNING id_turno;
            """,
            (fecha, hora_inicio_str, hora_fin_str, motivo, id_paciente)
        )
        id_turno = cursor.fetchone()[0]

    conexion.commit()

    return {
        "id_paciente": id_paciente,  # Este es el número de Historia Clínica (HC)
        "id_turno": id_turno,
    }


def cancelar_turno(conexion, id_turno: int) -> bool:
    """
    Cancela un turno si está en estado 'PENDIENTE' y su horario aún no ha expirado.
    Retorna True si fue cancelado, False si ya no era cancelable.
    """
    ahora = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))

    consulta = """
        UPDATE turno
        SET estado = 'CANCELADO'
        WHERE id_turno = %s
          AND estado = 'PENDIENTE'
          AND (fecha > %s OR (fecha = %s AND hora_inicio > %s))
        RETURNING id_turno;
    """
    with conexion.cursor() as cursor:
        cursor.execute(consulta, (id_turno, ahora.date(), ahora.date(), ahora.time()))
        resultado = cursor.fetchone()

    conexion.commit()
    return resultado is not None

SQL_MARCAR_AUSENTES = """
    UPDATE turno
    SET estado = 'AUSENTE'
    WHERE estado = 'PENDIENTE'
      AND (fecha + hora_inicio + INTERVAL '40 minutes') < (now() AT TIME ZONE %s)
    RETURNING id_turno;
"""

def marcar_turnos_ausentes(conexion, tz_name: str = "America/Argentina/Buenos_Aires") -> int:
    """
    Actualiza a 'AUSENTE' en la base de datos todos los turnos que sigan en 'PENDIENTE'
    y cuyo horario de inicio + 40 minutos ya haya pasado.
    """
    with conexion.cursor() as cursor:
        cursor.execute(SQL_MARCAR_AUSENTES, (tz_name,))
        afectados = cursor.rowcount
    conexion.commit()
    return afectados