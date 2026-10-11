from core.db import conectar


def eliminar_cliente(dni: str) -> None:
    dni = dni.strip()
    if not dni:
        raise ValueError("El DNI del cliente es obligatorio.")

    with conectar() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT 1 FROM cliente WHERE dni = %s", (dni,))
            if cursor.fetchone() is None:
                raise ValueError(f"No existe un cliente con DNI {dni}.")

            cursor.execute(
                """
                DELETE FROM consulta
                USING paciente
                WHERE consulta.id_paciente = paciente.id_paciente
                  AND paciente.dni = %s
                """,
                (dni,),
            )
            cursor.execute(
                """
                DELETE FROM turno
                USING paciente
                WHERE turno.id_paciente = paciente.id_paciente
                  AND paciente.dni = %s
                """,
                (dni,),
            )
            cursor.execute("DELETE FROM paciente WHERE dni = %s", (dni,))
            cursor.execute("DELETE FROM cliente WHERE dni = %s", (dni,))

            if cursor.rowcount != 1:
                raise ValueError(f"No existe un cliente con DNI {dni}.")
