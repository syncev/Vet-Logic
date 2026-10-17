# Vet-Logic

Aplicación de gestión veterinaria del equipo ABModel.

La aplicación utiliza Tkinter, la biblioteca gráfica incluida con Python, y
`screeninfo` para obtener las dimensiones del monitor principal.

## Integrantes

- Santiago Hernandez
- Santiago De Leonardi
- Verónica Cabral
- Belen Vassel
- Ignacio Faerman
- Guevara Aylen

## Requisitos

- Python 3.10 o superior.
- Tkinter instalado.
- Una sesión gráfica activa para abrir la ventana de la aplicación.

### Windows

Descargar Python desde [python.org](https://www.python.org/downloads/windows/).
Durante la instalación, activar **Add Python to PATH**. La distribución oficial
incluye Tkinter.

Comprobar la instalación desde PowerShell:

```powershell
py --version
py -c "import tkinter; print('Tkinter disponible')"
```

### macOS

Descargar Python desde [python.org](https://www.python.org/downloads/macos/).
La distribución oficial incluye Tkinter.

Comprobar la instalación desde Terminal:

```bash
python3 --version
python3 -c "import tkinter; print('Tkinter disponible')"
```

Si `import tkinter` falla, instalar Python desde el sitio oficial de Python o
instalar el paquete de Tk correspondiente a la distribución de Python utilizada.

### Linux

Instalar Python, el módulo para crear entornos virtuales y Tkinter usando el
gestor de paquetes de la distribución.

Ubuntu o Debian:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-tk
```

Fedora:

```bash
sudo dnf install python3 python3-tkinter
```

Arch Linux:

```bash
sudo pacman -S python tk
```

Comprobar la instalación:

```bash
python3 --version
python3 -c "import tkinter; print('Tkinter disponible')"
```

## Instalación

### 1. Obtener el proyecto

Clonar el repositorio o descargarlo y descomprimirlo. Luego abrir una terminal
en la carpeta que contiene `main.py`, `requirements.txt` y `README.md`.

Para un repositorio clonado:

```bash
cd vet-app
```

En Windows también se puede cambiar de carpeta desde PowerShell:

```powershell
cd ruta\a\vet-app
```

### 2. Crear el entorno virtual

Windows (PowerShell):

```powershell
py -m venv .venv
```

macOS y Linux:

```bash
python3 -m venv .venv
```

### 3. Activar el entorno virtual

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Windows (CMD):

```bat
.venv\Scripts\activate.bat
```

macOS y Linux:

```bash
source .venv/bin/activate
```

Cuando la activación sea correcta, el nombre `.venv` aparecerá al comienzo de
la línea de comandos.

### 4. Instalar las dependencias

Con el entorno virtual activado, ejecutar el comando correspondiente:

Windows:

```powershell
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

macOS y Linux:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Las dependencias externas del proyecto son `screeninfo`, `tzdata` y
`psycopg[binary]`; todas están incluidas en `requirements.txt`. Tkinter no se
instala con pip: debe estar disponible en la instalación del sistema de Python.

### 5. Verificar la instalación

Con el entorno virtual todavía activado:

Windows:

```powershell
py -c "import tkinter, screeninfo, psycopg; print('Instalación correcta')"
```

macOS y Linux:

```bash
python -c "import tkinter, screeninfo, psycopg; print('Instalación correcta')"
```

## Configurar PostgreSQL

Vet Logic se conecta a una instancia local de PostgreSQL en la misma computadora
donde se ejecuta la aplicación. PostgreSQL debe estar instalado y su servicio
iniciado. pgAdmin es opcional: el proyecto puede crear la base y cargar los
datos de prueba desde un asistente de terminal.

PostgreSQL es un programa del sistema y no se instala con `requirements.txt`.
Para la primera configuración, use las credenciales del administrador
`postgres` o de otro usuario que tenga permiso `CREATEDB` y pueda conectarse a
la base administrativa `postgres`. El asistente usará esas credenciales para
crear `vetlogic_desarrollo` y las guardará para la conexión de la aplicación.
Las herramientas cliente `psql` y `pg_dump` se necesitan para migraciones y
respaldos; no hace falta abrir pgAdmin.

### Primera configuración

Desde la carpeta del proyecto, ejecutá el asistente:

Windows:

```powershell
py setup_database.py
```

macOS o Linux:

```bash
python3 setup_database.py
```

Ingresá host, puerto, usuario y contraseña de PostgreSQL. El usuario debe poder
conectarse a la base administrativa `postgres` y tener permiso `CREATEDB`.
Para una instalación local, normalmente se usan `localhost` y el puerto `5432`.

El resultado depende del estado de `vetlogic_desarrollo`:

- Si no existe, el asistente la crea, crea las tablas y carga los datos de prueba.
- Si existe pero está vacía, crea las tablas y carga los datos de prueba.
- Si ya tiene el esquema actual, conserva sus datos y no vuelve a cargar el seed.
- Si detecta el esquema legado, no lo modifica; guarda la conexión e indica que requiere migración.
- Si encuentra una estructura desconocida, no la modifica y detiene la configuración para evitar cambios incorrectos.

La conexión se guarda en `database.ini`. Si ese archivo ya existe, el asistente
pregunta antes de reemplazarlo. Conservá el archivo al actualizar el proyecto y
no lo compartas.

### Reemplazar todos los datos locales

Si cambió el archivo `database/vetlogic.sql` y querés que la base local quede
exactamente con su esquema y datos de prueba actuales, ejecutá:

```bash
python3 setup_database.py --replace
```

El asistente crea un respaldo y exige escribir `BORRAR TODO` antes de continuar.
Después recrea las tablas y carga el contenido completo del archivo. Esta
operación elimina todos los datos locales existentes; no la uses para una
actualización que deba conservar información.

### Fusionar el seed sin perder datos locales

Para agregar a una base actual los registros que falten en el archivo
`database/vetlogic.sql`, conservando los datos existentes, ejecutá:

```bash
python3 setup_database.py --merge
```

El asistente crea un respaldo y pide confirmación con `FUSIONAR`. Los clientes
se reconocen por DNI y los veterinarios por matrícula. Los pacientes se
reconocen por DNI del dueño, nombre, especie y fecha de nacimiento coincidente
(no se fusionan automáticamente si falta la fecha). Si un turno del seed ocupa
un horario activo ya usado localmente, se conserva el turno local y se omite el
del seed. Los datos locales coincidentes no se sobrescriben.

### Migrar una base existente

`setup_database.py` no actualiza el esquema de una base que ya contiene tablas.
Si detecta el esquema actual, simplemente conserva los registros y no recarga
los datos de prueba. Para convertir el esquema legado y luego fusionar el seed
sin reemplazar los registros locales, usá el comando siguiente; pgAdmin no es
necesario.

Cerrá la aplicación y ejecutá:

Windows:

```powershell
py migrate_database.py
```

macOS o Linux:

```bash
python3 migrate_database.py
```

El comando comprueba que la base tenga el esquema legado y solicita escribir
`MIGRAR`. Solo después de esa confirmación crea un respaldo en `backups/` y
aplica los cambios dentro de una transacción. Después incorpora los registros
faltantes del seed con las mismas reglas de conservación descritas arriba. Si
la migración encuentra datos que no puede convertir, revierte los cambios y
deja la base legado intacta; el respaldo se conserva. Si termina correctamente,
la base queda en el esquema actual y se puede volver a ejecutar la aplicación.

Si la estructura se detecta como desconocida, el comando de migración se niega a
continuar. No borres ni recrees esa base; primero hay que identificar su origen.

## Ejecución

Con el entorno virtual activado, ejecutar:

Windows:

```powershell
py main.py
```

macOS y Linux:

```bash
python main.py
```

## Ejecutar desde VS Code

1. Abrir la carpeta del proyecto en VS Code.
2. Ejecutar `Python: Select Interpreter` desde la paleta de comandos.
3. Seleccionar `.venv\Scripts\python.exe` en Windows o `.venv/bin/python` en
	macOS y Linux.
4. Abrir `main.py` y ejecutar el archivo.

## Desactivar el entorno virtual

Al terminar, se puede desactivar el entorno virtual con el mismo comando en
cualquier sistema operativo:

```bash
deactivate
```
