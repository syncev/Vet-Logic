import os
import shutil
import subprocess
from configparser import ConfigParser
from pathlib import Path

import psycopg

from backup_database import archivo_pgpass, crear_respaldo
from setup_database import identificar_esquema

ROOT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = ROOT_DIR / "database.ini"
MIGRATION_FILE = ROOT_DIR / "database" / "migrations" / "001_legacy_to_current.sql"


def leer_configuracion() -> dict[str, str]:
    config = ConfigParser(interpolation=None)
    if not config.read(CONFIG_FILE, encoding="utf-8") or "database" not in config:
        raise FileNotFoundError(
            "No se encontró database.ini. Ejecute setup_database.py primero."
        )
    return dict(config["database"])


def obtener_estado_esquema(configuracion: dict[str, str]) -> str:
    with (
        psycopg.connect(**configuracion) as conexion,
        conexion.cursor() as cursor,
    ):
        return identificar_esquema(cursor)


def ejecutar_migracion(configuracion: dict[str, str], psql: str) -> None:
    entorno = os.environ.copy()
    with archivo_pgpass(
        configuracion["host"],
        configuracion["port"],
        configuracion["dbname"],
        configuracion["user"],
        configuracion["password"],
    ) as passfile:
        entorno["PGPASSFILE"] = str(passfile)
        subprocess.run(
            [
                psql,
                "--no-psqlrc",
                "--set=ON_ERROR_STOP=1",
                "--single-transaction",
                "--host",
                configuracion["host"],
                "--port",
                configuracion["port"],
                "--username",
                configuracion["user"],
                "--dbname",
                configuracion["dbname"],
                "--file",
                str(MIGRATION_FILE),
            ],
            check=True,
            env=entorno,
        )


def main() -> int:
    try:
        configuracion = leer_configuracion()
        psql = shutil.which("psql")
        if psql is None:
            raise FileNotFoundError(
                "No se encontró psql. Instale las herramientas de cliente de PostgreSQL."
            )

        estado = obtener_estado_esquema(configuracion)
        if estado != "legado":
            raise ValueError(
                f"Se esperaba el esquema legado, pero se detectó: {estado}."
            )

        print(
            "La migración actualiza tablas y convierte algunos campos. "
            "Cierre Vet Logic y asegúrese de tener espacio para el respaldo."
        )
        if input("Para continuar, escriba MIGRAR: ").strip() != "MIGRAR":
            print("Migración cancelada; la base no fue modificada.")
            return 0

        # El respaldo se completa antes de empezar la transacción de migración.
        backup_path = crear_respaldo()
        print(f"Respaldo creado: {backup_path.relative_to(ROOT_DIR)}")

        if obtener_estado_esquema(configuracion) != "legado":
            raise ValueError(
                "El esquema cambió después del respaldo. No se ejecutó la migración."
            )

        ejecutar_migracion(configuracion, psql)
        if obtener_estado_esquema(configuracion) != "actual":
            raise RuntimeError(
                "La migración terminó, pero la verificación del esquema no pasó. "
                f"Conserve el respaldo: {backup_path.name}."
            )
    except (
        FileNotFoundError,
        KeyError,
        OSError,
        ValueError,
        psycopg.Error,
        subprocess.CalledProcessError,
        RuntimeError,
    ) as error:
        print(f"No se pudo completar la migración: {error}")
        return 1

    print("Migración completada. Ya puede iniciar la aplicación con: python main.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())