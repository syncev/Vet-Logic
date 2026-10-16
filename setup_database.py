from configparser import ConfigParser
from getpass import getpass
import os
from pathlib import Path

import psycopg
from psycopg import sql


ROOT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = ROOT_DIR / "database.ini"
SCHEMA_FILE = ROOT_DIR / "database" / "vetlogic.sql"
DATABASE_NAME = "vetlogic_desarrollo"


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


def crear_base_si_no_existe(configuracion: dict[str, str | int]) -> None:
    parametros = {**configuracion, "connect_timeout": 5}

    # La conexión administrativa permite crear la base sin depender de pgAdmin.
    with psycopg.connect(
        **parametros,
        dbname="postgres",
        autocommit=True,
    ) as conexion:
        with conexion.cursor() as cursor:
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
    with psycopg.connect(**parametros_base) as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                LIMIT 1
                """
            )
            tiene_tablas = cursor.fetchone() is not None

            if not tiene_tablas:
                script = SCHEMA_FILE.read_text(encoding="utf-8")
                cursor.execute(script)

    if base_existe and tiene_tablas:
        print(
            "La base ya contiene tablas. No se ejecutó vetlogic.sql para "
            "proteger sus datos."
        )
    else:
        print("Base creada y datos iniciales cargados desde vetlogic.sql.")


def guardar_configuracion(configuracion: dict[str, str | int]) -> None:
    config = ConfigParser()
    config["database"] = {
        **{key: str(value) for key, value in configuracion.items()},
        "dbname": DATABASE_NAME,
    }

    with CONFIG_FILE.open("w", encoding="utf-8") as archivo:
        config.write(archivo)

    if os.name == "posix":
        CONFIG_FILE.chmod(0o600)


def main() -> int:
    if not confirmar_reemplazo_configuracion():
        print("No se modificó la configuración existente.")
        return 0

    try:
        configuracion = solicitar_configuracion()
        crear_base_si_no_existe(configuracion)
        guardar_configuracion(configuracion)
    except (OSError, ValueError, psycopg.Error) as error:
        print(f"No se pudo configurar Vet Logic: {error}")
        return 1

    print(f"Configuración guardada en {CONFIG_FILE.name}.")
    print("Ya puede iniciar la aplicación con: python main.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())