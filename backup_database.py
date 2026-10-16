import os
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from configparser import ConfigParser
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = ROOT_DIR / "database.ini"
BACKUP_DIR = ROOT_DIR / "backups"


def escapar_pgpass(valor: str) -> str:
    if "\n" in valor or "\r" in valor:
        raise ValueError("La configuración contiene un salto de línea inválido.")
    return valor.replace("\\", "\\\\").replace(":", "\\:")


@contextmanager
def archivo_pgpass(
    host: str,
    port: str,
    database: str,
    user: str,
    password: str,
) -> Iterator[Path]:
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        delete=False,
    ) as passfile:
        passfile.write(
            ":".join(
                escapar_pgpass(valor)
                for valor in (host, port, database, user, password)
            )
            + "\n"
        )
        passfile_path = Path(passfile.name)

    try:
        if os.name == "posix":
            passfile_path.chmod(0o600)
        yield passfile_path
    finally:
        passfile_path.unlink(missing_ok=True)


def crear_respaldo() -> Path:
    ejecutable = shutil.which("pg_dump")
    if ejecutable is None:
        raise FileNotFoundError(
            "No se encontró pg_dump. Instale las herramientas de cliente de PostgreSQL."
        )

    config = ConfigParser(interpolation=None)
    if not config.read(CONFIG_FILE, encoding="utf-8") or "database" not in config:
        raise FileNotFoundError(
            "No se encontró una configuración válida. Ejecute setup_database.py primero."
        )

    settings = config["database"]
    host = settings["host"]
    port = settings["port"]
    database = settings["dbname"]
    user = settings["user"]
    password = settings["password"]

    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    backup_path = BACKUP_DIR / f"vetlogic_{timestamp}.dump"

    # pg_dump lee las credenciales desde un archivo temporal protegido, no desde argumentos.
    with archivo_pgpass(host, port, database, user, password) as passfile_path:
        environment = os.environ.copy()
        environment["PGPASSFILE"] = str(passfile_path)
        try:
            subprocess.run(
                [
                    ejecutable,
                    "--format=custom",
                    "--no-password",
                    "--host",
                    host,
                    "--port",
                    port,
                    "--username",
                    user,
                    "--dbname",
                    database,
                    "--file",
                    str(backup_path),
                ],
                check=True,
                env=environment,
            )
        except Exception:
            backup_path.unlink(missing_ok=True)
            raise

    return backup_path


def main() -> int:
    try:
        backup_path = crear_respaldo()
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"No se pudo crear el respaldo: {error}")
        return 1

    print(f"Respaldo creado: {backup_path.relative_to(ROOT_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())