# Instrucciones para correr el proyecto en Windows

Sigue estos pasos para evitar errores al ejecutar este proyecto:

---

## 1. Clona o copia el proyecto

Asegúrate de copiar todos los archivos del proyecto, incluyendo:

- requirements.txt
- app.py (o el archivo principal)
- La carpeta "src" y otras necesarias para el código

---

## 2. Crea y activa el entorno virtual

Abre PowerShell o CMD dentro de la carpeta del proyecto y escribe:

    python -m venv venv
    venv\Scripts\activate

Verás algo como esto al activarse:

    (venv) PS C:\...>

---

## 3. Instala las dependencias

Con el entorno activado, ejecuta:

    pip install -r requirements.txt

Esto instalará automáticamente todas las librerías necesarias.

---



## 4. Ejecuta el proyecto

Dentro del entorno activado, ejecuta el archivo principal:

    python app.py

---

## Problemas comunes

- Si ves errores de módulos faltantes: verifica que el entorno virtual esté **activado** y que hayas corrido `pip install -r requirements.txt`.

- Si usas una versión de Python muy nueva (como 3.12+), puede que algunas librerías aún no sean totalmente compatibles. Se recomienda usar Python 3.10 o 3.11.

Si al ejecutar el proyecto ves un error como:  
`ModuleNotFoundError: No module named 'sympy'`

Significa que necesitas instalar los paquetes del proyecto con:

    pip install -r requirements.txt

---



