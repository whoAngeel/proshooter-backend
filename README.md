

bash
bash

# Proshooter API

API backend para la gestión de prácticas de tiro, clubes, usuarios y estadísticas, desarrollada en Python con FastAPI.

---

## Descripción general

Proshooter es una API RESTful que permite gestionar usuarios, tiradores, clubes, sesiones de práctica, evaluaciones y estadísticas de rendimiento. Está diseñada para ser modular, escalable y fácil de mantener, siguiendo buenas prácticas de arquitectura hexagonal y DDD.

---

## Estructura de directorios

```
src/
├── main.py                # Punto de entrada FastAPI
├── application/           # Lógica de negocio (servicios)
├── domain/                # Entidades, enums y constantes del dominio
├── infraestructure/       # Configuración, modelos ORM, repositorios, auth
├── presentation/          # Esquemas Pydantic y routers/endpoints
└── tests/                 # (Vacío o para tests)
```

### Detalle de carpetas clave

- **application/services/**: Servicios de negocio (ej: shooter_service.py, user_service.py)
- **domain/entities/**: Entidades del dominio (ej: shooter.py, user.py)
- **domain/enums/**: Enumeraciones (roles, niveles, tipos de práctica, etc)
- **infraestructure/database/models/**: Modelos SQLAlchemy (ORM)
- **infraestructure/database/repositories/**: Repositorios para acceso a datos
- **infraestructure/auth/**: Configuración y utilidades de autenticación JWT
- **infraestructure/config/**: Configuración global y settings
- **presentation/api/v1/endpoints/**: Endpoints de la API REST (routers)
- **presentation/schemas/**: Esquemas Pydantic para validación y serialización

---

## Configuración

- Variables de entorno gestionadas en `.env`, `.env.dev`, `.env.prod`
- Configuración centralizada en `src/infraestructure/config/settings.py`
- Ejemplo de variables:
  ```
  PROJECT_NAME=Proshooter API
  VERSION=1.0.0
  HOST=0.0.0.0
  PORT=3000
  DATABASE_URL=postgresql://user:pass@host:port/db
  SECRET_KEY=...
  ```

---

## Endpoints principales

- `/health` — Health check
- `/auth/login` — Login de usuario
- `/users/` — Gestión de usuarios
- `/shooters/` — Gestión de tiradores (listado, detalle, actualización, validación de nickname, ranking, etc)
- `/shooters/validate-nickname` — Validación de nickname único
- `/shooters/{user_id}` — Detalle de tirador
- `/shooters/rankings/top` — Ranking de tiradores
- `/shooters/{user_id}/performance` — Resumen de rendimiento
- `/shooters/{user_id}/classification-history` — Historial de clasificación
- `/shooters/{user_id}/club/{club_id}` — Asignar club
- `/practice-sessions/` — Gestión de sesiones de práctica
- `/practice-evaluations/` — Evaluaciones de práctica
- `/weapons/`, `/targets/`, `/clubs/`, etc.

> Consulta la documentación interactiva en `/docs` (Swagger UI) para ver todos los endpoints y sus detalles.

---

## Dependencias y requisitos

- Python 3.11+
- FastAPI
- SQLAlchemy
- psycopg2-binary
- python-jose
- passlib
- pydantic
- uvicorn
- Otros: ver `requirements.txt`

---

## Instalación y ejecución

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tuusuario/proshooter.git
   cd proshooter
   ```

2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configura las variables de entorno (`.env.dev` para desarrollo).

4. Ejecuta la API:
   ```bash
   uvicorn src.main:app --port 3000 --reload
   ```

5. Accede a la documentación interactiva:
   - [http://localhost:3000/docs](http://localhost:3000/docs)

---

## Ejemplo de uso de endpoint

```bash
# Validar nickname
curl 'http://localhost:3000/shooters/validate-nickname?nickname=juanito'

# Crear tirador (requiere autenticación)
POST /shooters/
{
  "nickname": "juanito",
  "level": "EXPERTO",
  ...
}
```

---

## Arquitectura y flujo

- **FastAPI** como framework principal.
- **Pydantic** para validación de datos.
- **SQLAlchemy** para ORM y acceso a base de datos PostgreSQL.
- **JWT** para autenticación y autorización.
- **Servicios** en `application/` para lógica de negocio desacoplada.
- **Repositorios** en `infraestructure/database/repositories/` para acceso a datos.
- **Esquemas** en `presentation/schemas/` para entrada/salida de datos.
