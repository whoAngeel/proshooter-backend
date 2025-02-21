# Guía de Uso de Alembic para Migraciones de Base de Datos

Alembic es una herramienta de migración de base de datos para SQLAlchemy. Permite realizar cambios en el esquema de la base de datos de manera controlada y reproducible.

## Instalación

Asegúrate de tener Alembic instalado en tu entorno. Si no lo está, puedes instalarlo usando pip:

```bash
pip install alembic
```

## Configuración Inicial

1. Inicializa un directorio de Alembic en tu proyecto:

   ```bash
   alembic init alembic
   ```

   Esto creará un directorio `alembic` con los archivos de configuración necesarios.

2. Configura el archivo `alembic.ini`:

   - Establece la URL de conexión de tu base de datos en `sqlalchemy.url`.

3. Configura el archivo `env.py`:

   - Importa tus modelos y establece `target_metadata` a `Base.metadata`.

   ```python
   from yourapp.models import Base
   target_metadata = Base.metadata
   ```

## Creación de Migraciones

Para crear una nueva migración, usa el comando:

```bash
alembic revision --autogenerate -m "Descripción de la migración"
```

El flag `--autogenerate` permite a Alembic detectar automáticamente los cambios en los modelos y generar el script de migración.

## Aplicación de Migraciones

Para aplicar las migraciones y actualizar la base de datos al estado más reciente, ejecuta:

```bash
alembic upgrade head
```

## Reversión de Migraciones

Si necesitas revertir una migración, puedes hacerlo usando:

```bash
alembic downgrade -1
```

Esto revertirá la última migración aplicada.

## Buenas Prácticas

- Siempre revisa los archivos de migración generados automáticamente para asegurarte de que reflejan correctamente los cambios que deseas aplicar.
- Mantén un control de versiones de tus archivos de migración usando un sistema de control de versiones como Git.
- Asegúrate de que todas las migraciones sean replicables en diferentes entornos (desarrollo, prueba, producción).

Con esta guía, deberías poder gestionar las migraciones de tu base de datos de manera efectiva usando Alembic.
