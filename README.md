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
- Paola Argento

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

La única dependencia externa del proyecto es `screeninfo`. Tkinter no se
instala con `pip`: debe estar disponible en la instalación del sistema de
Python.

### 5. Verificar la instalación

Con el entorno virtual todavía activado:

Windows:

```powershell
py -c "import tkinter, screeninfo; print('Instalación correcta')"
```

macOS y Linux:

```bash
python -c "import tkinter, screeninfo; print('Instalación correcta')"
```

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
