from core.db import conectar


def eliminar_historia_clinica(numero_hc: int) -> None:
    if numero_hc <= 0:
        raise ValueError("El número de HC debe ser un entero positivo.")

    with conectar() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "DELETE FROM consulta WHERE id_consulta = %s",
                (numero_hc,),
            )
            if cursor.rowcount != 1:
                raise ValueError(
                    f"No existe una historia clínica con número {numero_hc}."
                )
