import getpass
import psycopg


def conectar():
    """Conecta con la base de datos de desarrollo de VetLogic."""

    password = getpass.getpass("Contraseña de PostgreSQL: ")

    conexion = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="vetlogic_desarrollo",
        user="postgres",
        password=password,
    )

    return conexion
