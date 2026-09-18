# Vet-Logic

Aplicación de gestión veterinaria del equipo ABModel.

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
- Tkinter instalado. En Windows y macOS normalmente viene incluido con Python. Si usás macOS con una instalación que no lo incluye, instalá Python desde [python.org](https://www.python.org/downloads/).

En Fedora:

```bash
sudo dnf install python3-tkinter
```

En Ubuntu o Debian:

```bash
sudo apt install python3-tk
```

## Instalación

1. Crear un entorno virtual:

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows (CMD):

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

macOS y Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
python -m pip install -r requirements.txt
```

## Ejecución

Con el entorno virtual activado, ejecutar:

```bash
python main.py
```

En VS Code, seleccionar el intérprete `.venv/bin/python` mediante `Python: Select Interpreter`.
