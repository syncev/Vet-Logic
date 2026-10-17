import argparse
import os
import subprocess
from configparser import ConfigParser
from getpass import getpass
from pathlib import Path

import psycopg
from psycopg import sql

from backup_database import crear_respaldo
from database.seed_merge import fusionar_seed

ROOT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = ROOT_DIR / "database.ini"
SCHEMA_FILE = ROOT_DIR / "database" / "vetlogic.sql"
DATABASE_NAME = "vetlogic_desarrollo"
CURRENT_SCHEMA = {
    "cliente": {"dni", "nombre", "apellido", "telefono"},
    "veterinario": {"matricula_veterinario", "nombre", "apellido", "contacto"},
    "paciente": {"id_paciente", "nombre", "especie", "castrado", "dni"},
    "turno": {"id_turno", "fecha", "hora_inicio", "hora_fin", "id_paciente"},
    "consulta": {
        "id_consulta",
        "observaciones",
        "tratamiento",
        "matricula_veterinario",
        "id_turno",
    },
}


def identificar_esquema(cursor) -> str:
    cursor.execute(
        """
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
        """
    )
    columnas: dict[str, set[str]] = {}
    for tabla, columna in cursor.fetchall():
        columnas.setdefault(tabla, set()).add(columna)

    if not columnas:
        return "vacio"

    # Estas columnas identifican el esquema anterior guardado en el historial.
    if (
        "nombre_y_apellido" in columnas.get("cliente", set())
        or "estado_reproductivo" in columnas.get("paciente", set())
        or "matricula_veterinario" in columnas.get("turno", set())
    ):
        return "legado"

    if all(
        requeridas.issubset(columnas.get(tabla, set()))
        for tabla, requeridas in CURRENT_SCHEMA.items()
    ):
        return "actual"

    return "desconocido"


def solicitar_configuracion() -> dict[str, str | int]:
    host = input("Servidor PostgreSQL [localhost]: ").strip() or "localhost"
    port_text = input("Puerto PostgreSQL [5432]: ").strip() or "5432"
    user = input("Usuario PostgreSQL [postgres]: ").strip() or "postgres"
    password = getpass("Contraseña PostgreSQL: ")

    try:
        port = int(port_text)
    except ValueError as error:
        raise ValueError("El puerto debe ser un número.") from error

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
    }


def confirmar_reemplazo_configuracion() -> bool:
    if not CONFIG_FILE.exists():
        return True

    respuesta = input(
        f"Ya existe {CONFIG_FILE.name}. ¿Reemplazar su configuración? [s/N]: "
    )
    return respuesta.strip().lower() in ("s", "si", "sí")


def crear_base_si_no_existe(configuracion: dict[str, str | int]) -> str:
    parametros = {**configuracion, "connect_timeout": 5}

    # La conexión administrativa permite crear la base sin depender de pgAdmin.
    with (
        psycopg.connect(
            **parametros,
            dbname="postgres",
            autocommit=True,
        ) as conexion,
        conexion.cursor() as cursor,
    ):
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DATABASE_NAME,),
        )
        base_existe = cursor.fetchone() is not None

        if not base_existe:
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(DATABASE_NAME)
                )
            )

    parametros_base = {**parametros, "dbname": DATABASE_NAME}
    with (
        psycopg.connect(**parametros_base) as conexion,
        conexion.cursor() as cursor,
    ):
        estado_esquema = identificar_esquema(cursor)

        if estado_esquema == "vacio":
            script = SCHEMA_FILE.read_text(encoding="utf-8")
            cursor.execute(script)

    return estado_esquema


def reemplazar_datos(configuracion: dict[str, str | int]) -> None:
    parametros = {**configuracion, "dbname": DATABASE_NAME}
    with (
        psycopg.connect(**parametros) as conexion,
        conexion.cursor() as cursor,
    ):
        cursor.execute(SCHEMA_FILE.read_text(encoding="utf-8"))


def fusionar_datos(configuracion: dict[str, str | int]) -> dict[str, int]:
    parametros = {**configuracion, "dbname": DATABASE_NAME}
    with (
        psycopg.connect(**parametros) as conexion,
        conexion.cursor() as cursor,
    ):
        return fusionar_seed(cursor)


def guardar_configuracion(configuracion: dict[str, str | int]) -> None:
    config = ConfigParser(interpolation=None)
    config["database"] = {
        **{key: str(value) for key, value in configuracion.items()},
        "dbname": DATABASE_NAME,
    }

    with CONFIG_FILE.open("w", encoding="utf-8") as archivo:
        config.write(archivo)

    if os.name == "posix":
        CONFIG_FILE.chmod(0o600)


def main() -> int:
    parser = argparse.ArgumentParser(description="Configura la base de Vet Logic.")
    modos = parser.add_mutually_exclusive_group()
    modos.add_argument(
        "--replace",
        action="store_true",
        help="reemplaza los datos locales por el seed actual después de respaldarlos",
    )
    modos.add_argument(
        "--merge",
        action="store_true",
        help="fusiona los datos del seed sin sobrescribir los registros locales",
    )
    argumentos = parser.parse_args()

    if not confirmar_reemplazo_configuracion():
        print("No se modificó la configuración existente.")
        return 0

    try:
        configuracion = solicitar_configuracion()
        estado_esquema = crear_base_si_no_existe(configuracion)
        guardar_configuracion(configuracion)
        if argumentos.replace and estado_esquema != "vacio":
            if estado_esquema not in ("actual", "legado"):
                raise ValueError(
                    "No se reemplaza una estructura desconocida. Revise su origen."
                )
            print(
                "Esta operación borrará todos los datos de "
                f"{DATABASE_NAME} y cargará el seed actual."
            )
            if input("Para continuar, escriba BORRAR TODO: ").strip() != "BORRAR TODO":
                print("Reemplazo cancelado; la base no fue modificada.")
                return 0
            backup_path = crear_respaldo()
            print(f"Respaldo creado: {backup_path.relative_to(ROOT_DIR)}")
            reemplazar_datos(configuracion)
            estado_esquema = "actual"
        elif argumentos.merge and estado_esquema == "actual":
            print(
                "Se agregarán registros del seed cuando no coincidan con los "
                "locales. Los conflictos de turnos se resuelven conservando el local."
            )
            if input("Para continuar, escriba FUSIONAR: ").strip() != "FUSIONAR":
                print("Fusión cancelada; la base no fue modificada.")
                return 0
            backup_path = crear_respaldo()
            print(f"Respaldo creado: {backup_path.relative_to(ROOT_DIR)}")
            fusion_counts = fusionar_datos(configuracion)
            print("Registros agregados: " + ", ".join(
                f"{tabla}={cantidad}"
                for tabla, cantidad in fusion_counts.items()
            ))
    except (
        KeyError,
        OSError,
        ValueError,
        psycopg.Error,
        subprocess.CalledProcessError,
    ) as error:
        print(f"No se pudo configurar Vet Logic: {error}")
        return 1

    print(f"Configuración guardada en {CONFIG_FILE.name}.")
    if estado_esquema == "legado":
        print(
            "La base usa el esquema anterior. No se modificó; cree un "
            "respaldo y ejecute migrate_database.py para actualizarla."
        )
        return 2
    if estado_esquema == "desconocido":
        print(
            "La estructura no coincide con un esquema conocido. No se "
            "modificó la base; revise su origen antes de continuar."
        )
        return 2
    if estado_esquema == "vacio":
        print("Base creada y datos iniciales cargados desde vetlogic.sql.")
    elif not argumentos.replace and not argumentos.merge:
        print("Se encontró una base con el esquema actual; no se recargó el seed.")
    elif argumentos.merge and estado_esquema != "actual":
        print(
            "La fusión requiere el esquema actual. Para una base legada, "
            "ejecute migrate_database.py."
        )
        return 2
    print("Ya puede iniciar la aplicación con: python main.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())