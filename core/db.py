from configparser import ConfigParser
from pathlib import Path

import psycopg

CONFIG_FILE = Path(__file__).resolve().parents[1] / "database.ini"

def conectar():
    """Conecta con la base de datos configurada localmente."""

    if not CONFIG_FILE.is_file():
        raise FileNotFoundError(
            f"No se encontró el archivo de configuración: {CONFIG_FILE}"
        )

    config = ConfigParser()
    config.read(CONFIG_FILE, encoding="utf-8")

    if "database" not in config:
        raise ValueError(
            f"Falta la sección [database] en {CONFIG_FILE}"
        )

    settings = config["database"]

    return psycopg.connect(
        host=settings["host"],
        port=settings.getint("port"),
        dbname=settings["dbname"],
        user=settings["user"],
        password=settings["password"],
    )
