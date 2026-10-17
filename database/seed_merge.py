from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg import sql

ROOT_DIR = Path(__file__).resolve().parents[1]
SEED_FILE = ROOT_DIR / "database" / "vetlogic.sql"


def fusionar_seed(cursor: psycopg.Cursor) -> dict[str, int]:
    """Importa el seed sin reemplazar registros locales coincidentes."""
    schema_seed = f"vetlogic_seed_{uuid4().hex}"
    counts: dict[str, int] = {}
    cursor.execute(
        sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema_seed))
    )
    cursor.execute(
        sql.SQL("SET LOCAL search_path TO {}").format(
            sql.Identifier(schema_seed)
        )
    )
    cursor.execute(SEED_FILE.read_text(encoding="utf-8"))
    cursor.execute("SET LOCAL search_path TO public, pg_catalog")

    seed = lambda table: sql.Identifier(schema_seed, table)
    public = lambda table: sql.Identifier("public", table)

    cursor.execute(
        sql.SQL(
            """
            INSERT INTO {} (dni, nombre, apellido, telefono, mail, domicilio, estado)
            SELECT dni, nombre, apellido, telefono, mail, domicilio, estado
            FROM {}
            ON CONFLICT (dni) DO NOTHING
            """
        ).format(public("cliente"), seed("cliente"))
    )
    counts["cliente"] = cursor.rowcount
    cursor.execute(
        sql.SQL(
            """
            INSERT INTO {} (
                matricula_veterinario, nombre, apellido, contacto, estado,
                especialidad, domicilio, correo, contacto_emergencia
            )
            SELECT matricula_veterinario, nombre, apellido, contacto, estado,
                   especialidad, domicilio, correo, contacto_emergencia
            FROM {}
            ON CONFLICT (matricula_veterinario) DO NOTHING
            """
        ).format(public("veterinario"), seed("veterinario"))
    )
    counts["veterinario"] = cursor.rowcount

    patient_matches = sql.SQL(
        """
        SELECT DISTINCT ON (source.id_paciente)
               source.id_paciente AS seed_id, local.id_paciente AS local_id
        FROM {} AS source
        JOIN {} AS local
          ON local.dni = source.dni
         AND lower(btrim(local.nombre)) = lower(btrim(source.nombre))
         AND lower(btrim(local.especie)) = lower(btrim(source.especie))
         AND local.fecha_nacimiento = source.fecha_nacimiento
        WHERE source.fecha_nacimiento IS NOT NULL
        ORDER BY source.id_paciente, local.id_paciente
        """
    ).format(seed("paciente"), public("paciente"))

    cursor.execute(
        sql.SQL(
            """
            INSERT INTO {} (
                nombre, especie, raza, sexo, fecha_nacimiento, peso, castrado,
                dni, estado
            )
            SELECT source.nombre, source.especie, source.raza, source.sexo,
                   source.fecha_nacimiento, source.peso, source.castrado,
                   source.dni, source.estado
            FROM {} AS source
            JOIN {} AS owner ON owner.dni = source.dni
                        WHERE source.fecha_nacimiento IS NOT NULL
                            AND NOT EXISTS (
                  SELECT 1
                  FROM {} AS local
                  WHERE local.dni = source.dni
                    AND lower(btrim(local.nombre)) = lower(btrim(source.nombre))
                    AND lower(btrim(local.especie)) = lower(btrim(source.especie))
                    AND local.fecha_nacimiento = source.fecha_nacimiento
              )
            """
        ).format(
            public("paciente"),
            seed("paciente"),
            public("cliente"),
            public("paciente"),
        )
    )
    counts["paciente"] = cursor.rowcount

    cursor.execute(
        sql.SQL(
            """
            INSERT INTO {} (fecha, hora_inicio, hora_fin, motivo, estado, id_paciente)
            SELECT source.fecha, source.hora_inicio, source.hora_fin,
                   source.motivo, source.estado, patient_map.local_id
            FROM {} AS source
            JOIN ({}) AS patient_map ON patient_map.seed_id = source.id_paciente
            WHERE (
                   source.estado = 'CANCELADO'
                   AND NOT EXISTS (
                       SELECT 1 FROM {} AS cancelled
                       WHERE cancelled.fecha = source.fecha
                         AND cancelled.hora_inicio = source.hora_inicio
                         AND cancelled.id_paciente = patient_map.local_id
                         AND cancelled.estado = 'CANCELADO'
                   )
               ) OR (
                   source.estado <> 'CANCELADO'
                   AND NOT EXISTS (
                   SELECT 1 FROM {} AS local
                   WHERE local.fecha = source.fecha
                     AND local.hora_inicio = source.hora_inicio
                     AND local.estado <> 'CANCELADO'
                   )
               )
            ON CONFLICT (fecha, hora_inicio) WHERE estado <> 'CANCELADO'
            DO NOTHING
            """
        ).format(
            public("turno"),
            seed("turno"),
            patient_matches,
            public("turno"),
            public("turno"),
        )
    )
    counts["turno"] = cursor.rowcount

    cursor.execute(
        sql.SQL(
            """
            INSERT INTO {} (
                fecha, motivo_consulta, observaciones, tratamiento,
                id_paciente, matricula_veterinario, id_turno
            )
            SELECT source.fecha, source.motivo_consulta, source.observaciones,
                   source.tratamiento, patient_map.local_id,
                   source.matricula_veterinario, local_turn.id_turno
            FROM {} AS source
            JOIN {} AS seed_turn ON seed_turn.id_turno = source.id_turno
            JOIN ({}) AS patient_map
              ON patient_map.seed_id = seed_turn.id_paciente
                        JOIN {} AS local_turn
              ON local_turn.fecha = seed_turn.fecha
             AND local_turn.hora_inicio = seed_turn.hora_inicio
             AND local_turn.estado <> 'CANCELADO'
             AND local_turn.id_paciente = patient_map.local_id
                         AND local_turn.hora_fin = seed_turn.hora_fin
                         AND local_turn.motivo = seed_turn.motivo
                         AND local_turn.estado = seed_turn.estado
            ON CONFLICT (id_turno) DO NOTHING
            """
        ).format(
            public("consulta"),
            seed("consulta"),
            seed("turno"),
            patient_matches,
            public("turno"),
        )
    )
    counts["consulta"] = cursor.rowcount

    cursor.execute(
        sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema_seed))
    )
    return counts