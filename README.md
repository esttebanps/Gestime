# Gestime
## Descripción

Gestime es un sistema de registro y seguimiento del tiempo de juego en una sala de videojuegos. El administrador puede crear cuentas de acceso para los empleados, quienes a su vez pueden registrar el inicio y fin de las sesiones de juego de los clientes. El sistema permite a los empleados visualizar la hora de salida y el costo total de las sesiones de juego de los clientes, así como generar reportes.

## Características

- Autenticación y registro de usuarios
- Registro y seguimiento de sesiones de juego
- Búsqueda por rango de fechas

## Instalación

1. Clonar este repositorio: `git clone https://github.com/tu-usuario/tienda-en-linea.git` (usa tu link)
2. Crear un entorno virtual: `python -m venv nombre-del-entorno`
3. Instalar las dependencias: `pip install -r requirements.txt`
4. Configurar la base de datos en `settings.py`.
5. Ejecutar las migraciones: `python manage.py migrate`
6. Crear un superusuario: `python manage.py createsuperuser`
7. Ejecutar el servidor: `python manage.py runserver`

## Uso

- Acceder a la aplicación en `http://localhost:8000`.
- Acceder al panel de administración en `http://localhost:8000/admin` con las credenciales del superusuario creado previamente.

