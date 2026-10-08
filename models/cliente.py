class Cliente:
    def __init__(self, dni, nombre_y_apellido, telefono, mail, domicilio):
        self.__dni = dni
        self.__nombre_y_apellido = nombre_y_apellido
        self.__telefono = telefono
        self.__mail = mail
        self.__domicilio = domicilio

# Leer el dato privado para mostrarlo
@property
def telefono(self):
    return self.__telefono

@telefono.setter
def telefono(self, valor):
    if (len(valor)) < 8:
        raise ValueError("El teléfono debe tener 8 dígitos.")

    else:
        self.__telefono = valor 




