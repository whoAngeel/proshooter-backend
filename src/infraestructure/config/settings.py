import os
from enum import Enum
from pathlib import Path
from typing import List, Optional
from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
# Esto debe hacerse antes de definir la clase Settings
load_dotenv()


class Environment(str, Enum):
    """
    Enum para definir los entornos válidos de la aplicación.
    Esto nos ayuda a prevenir errores de tipeo y hace el código más mantenible.
    """

    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"
    TESTING = "test"


class LogLevel(str, Enum):
    """
    Enum para definir los niveles de logging válidos.
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """
    Configuración principal de la aplicación.

    Esta clase maneja todas las variables de configuración usando pydantic-settings,
    lo que proporciona validación automática, conversión de tipos, y valores por defecto.
    """

    # =====================================
    # Configuración del entorno
    # =====================================
    ENV: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Entorno de ejecución de la aplicación",
    )

    DEBUG: bool = Field(
        default=True, description="Activar modo debug (solo para desarrollo)"
    )

    LOG_LEVEL: LogLevel = Field(
        default=LogLevel.INFO, description="Nivel de logging de la aplicación"
    )

    # =====================================
    # Configuración de la aplicación
    # =====================================
    PROJECT_NAME: str = Field(
        default="ProShooter API", description="Nombre del proyecto"
    )

    VERSION: str = Field(default="1.0.0", description="Versión de la aplicación")

    DESCRIPTION: str = Field(
        default="Sistema de seguimiento para tiradores deportivos y profesionales",
        description="Descripción de la aplicación",
    )

    # =====================================
    # Configuración del servidor
    # =====================================
    HOST: str = Field(
        default="0.0.0.0", description="Host donde se ejecutará el servidor"
    )

    API_PORT: int = Field(default=8000, description="Puerto donde se ejecutará la API")

    # Para compatibilidad con código legacy que usa PORT
    @property
    def PORT(self) -> int:
        """Alias para API_PORT para mantener compatibilidad."""
        return self.API_PORT

    # =====================================
    # Configuración de seguridad
    # =====================================
    SECRET_KEY: str = Field(
        ...,  # Campo requerido
        min_length=32,
        description="Clave secreta para JWT y encriptación",
    )

    ALGORITHM: str = Field(
        default="HS256", description="Algoritmo para firmar tokens JWT"
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=12 * 60,  # 12 horas en minutos
        description="Tiempo de expiración de tokens JWT en minutos",
    )

    # =====================================
    # Configuración de base de datos
    # =====================================
    DATABASE_URL: Optional[str] = Field(
        default=None, description="URL completa de conexión a la base de datos"
    )

    # Componentes individuales de la DB para mayor flexibilidad
    POSTGRES_USER: str = Field(default="angel", description="Usuario de PostgreSQL")

    POSTGRES_PASSWORD: str = Field(
        default="angel", description="Contraseña de PostgreSQL"
    )

    POSTGRES_DB: str = Field(
        default="proshooter_db", description="Nombre de la base de datos"
    )

    POSTGRES_HOST: str = Field(
        default="postgres",
        description="Host de la base de datos (nombre del servicio en Docker)",
    )

    DB_PORT: int = Field(default=5432, description="Puerto de la base de datos")

    # =====================================
    # Configuración de CORS
    # =====================================
    CORS_ORIGINS: List[str] = Field(
        default=["*"], description="Orígenes permitidos para CORS"
    )

    CORS_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Métodos HTTP permitidos para CORS",
    )

    CORS_HEADERS: List[str] = Field(
        default=["*"], description="Headers permitidos para CORS"
    )

    # =====================================
    # Configuración específica para CI/CD
    # =====================================
    API_IMAGE: str = Field(
        default="subkey/proshooter-api:latest", description="Imagen Docker de la API"
    )

    BUILD_TARGET: str = Field(
        default="development", description="Target del Dockerfile multistage"
    )

    # =====================================
    # Validadores personalizados
    # =====================================

    @field_validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        """
        Validar que la clave secreta tenga la longitud mínima requerida
        y no sea una clave de desarrollo conocida.
        """
        if len(v) < 32:
            raise ValueError("SECRET_KEY debe tener al menos 32 caracteres")

        # Lista de claves de desarrollo conocidas que no deben usarse en producción
        dangerous_keys = [
            "fasdfjasfsdfkasjdfoiadbasdbasd",
            "your-secret-key-here",
            "change-me",
            "dev-secret-key",
        ]

        if v in dangerous_keys:
            raise ValueError("No uses claves de desarrollo conocidas en producción")

        return v

    @field_validator("ENV")
    def validate_environment_specific_settings(cls, v, values):
        """
        Validar configuraciones específicas según el entorno.
        """
        # En producción, DEBUG debe ser False
        if v == Environment.PRODUCTION and values.get("DEBUG", False):
            raise ValueError("DEBUG debe ser False en producción")

        return v

    @field_validator("CORS_ORIGINS")
    def validate_cors_origins(cls, v, values):
        """
        Validar configuración de CORS según el entorno.
        """
        env = values.get("ENV", Environment.DEVELOPMENT)

        # En producción, no permitir CORS desde cualquier origen
        if env == Environment.PRODUCTION and "*" in v:
            raise ValueError('CORS_ORIGINS no debe incluir "*" en producción')

        return v

    # =====================================
    # Propiedades computadas
    # =====================================

    @property
    def database_url(self) -> str:
        """
        Construir la URL de la base de datos automáticamente si no se proporciona.

        Esto es útil porque permite definir la URL completa O los componentes individuales,
        dando flexibilidad según el método de deployment.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL

        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def is_development(self) -> bool:
        """Verificar si estamos en entorno de desarrollo."""
        return self.ENV == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Verificar si estamos en entorno de producción."""
        return self.ENV == Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        """Verificar si estamos en entorno de testing."""
        return self.ENV == Environment.TESTING

    # =====================================
    # Configuración de pydantic-settings
    # =====================================

    class Config:
        """
        Configuración de pydantic-settings.
        """

        # Archivo de variables de entorno a leer
        env_file = ".env"

        # Permitir múltiples archivos .env (útil para override)
        env_file_encoding = "utf-8"

        # Ser sensible a mayúsculas/minúsculas
        case_sensitive = True

        # Validar asignaciones (útil para detectar errores)
        validate_assignment = True

        # Permitir campos extra (útil para futuras expansiones)
        extra = "allow"


class DevelopmentSettings(Settings):
    """
    Configuración específica para desarrollo.
    Hereda de Settings y sobrescribe valores por defecto para desarrollo.
    """

    ENV: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    LOG_LEVEL: LogLevel = LogLevel.DEBUG
    CORS_ORIGINS: List[str] = ["*"]  # Permitir todos los orígenes en desarrollo


class ProductionSettings(Settings):
    """
    Configuración específica para producción.
    Hereda de Settings y sobrescribe valores por defecto para producción.
    """

    ENV: Environment = Environment.PRODUCTION
    DEBUG: bool = False
    LOG_LEVEL: LogLevel = LogLevel.WARNING

    # En producción, requerir configuración explícita de CORS
    CORS_ORIGINS: List[str] = Field(
        default_factory=list,
        description="Debe configurarse explícitamente en producción",
    )


class TestingSettings(Settings):
    """
    Configuración específica para testing.
    Usa base de datos en memoria y configuraciones optimizadas para pruebas.
    """

    ENV: Environment = Environment.TESTING
    DEBUG: bool = True
    LOG_LEVEL: LogLevel = LogLevel.DEBUG

    # Usar base de datos SQLite en memoria para tests
    DATABASE_URL: str = "sqlite:///:memory:"


# =====================================
# Factory function para crear settings
# =====================================


def get_settings() -> Settings:
    """
    Factory function para obtener la configuración apropiada según el entorno.

    Esta función lee la variable ENV y retorna la clase de configuración apropiada.
    Es el punto de entrada principal para obtener configuración en la aplicación.
    """
    env = os.getenv("ENV", "dev").lower()

    if env == "prod" or env == "production":
        return ProductionSettings()
    elif env == "test" or env == "testing":
        return TestingSettings()
    else:
        # Por defecto, usar configuración de desarrollo
        return DevelopmentSettings()


# =====================================
# Instancia global de settings
# =====================================

# Crear la instancia global de configuración
settings = get_settings()

# Validar configuración al importar el módulo
if __name__ == "__main__":
    # Esto es útil para debuggear la configuración
    print("Configuración cargada:")
    print(f"Entorno: {settings.ENV}")
    print(f"Debug: {settings.DEBUG}")
    print(f"Database URL: {settings.database_url}")
    print(f"API Port: {settings.API_PORT}")
    print(f"Log Level: {settings.LOG_LEVEL}")
