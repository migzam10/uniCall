"""
Configuración central de la aplicación.

Todos los valores sensibles (claves, credenciales, URLs de base de datos)
se leen desde variables de entorno / archivo .env. Nunca deben quedar
escritos directamente en el código fuente.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Aplicación
    app_name: str = "LSC Videollamadas Accesibles"
    environment: str = "development"
    debug: bool = True
    # URL pública base del backend, usada para construir URLs de archivos
    # servidos (p. ej. videos de referencia LSC). Ajusta en producción al
    # dominio real (ej. https://api.tudominio.com).
    app_base_url: str = "http://localhost:8000"

    # Base de datos
    database_url: str = "sqlite+aiosqlite:///./dev.db"

    # Seguridad / JWT
    secret_key: str = "CHANGE_ME_GENERATE_A_RANDOM_SECRET"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    # WebRTC (usado en fases posteriores)
    stun_server: str = "stun:stun.l.google.com:19302"
    turn_server: str = ""
    turn_username: str = ""
    turn_password: str = ""

    # IA de voz (Fase 3)
    # "mock": motor determinístico sin dependencias, usado en pruebas y por
    #         defecto en desarrollo si no se ha descargado el modelo.
    # "whisper": motor real (faster-whisper), requiere descargar el modelo
    #            la primera vez que se usa (necesita conexión a internet).
    stt_engine: str = "mock"

    # Reconocimiento de LSC (Fase 5)
    # Distancia DTW máxima para aceptar una coincidencia como válida; por
    # encima de este valor se informa "no reconocido" en vez de arriesgar
    # una respuesta incorrecta (sección 29). Ajustar empíricamente a medida
    # que se acumulen más señas y videos de referencia reales.
    lsc_max_dtw_distance: float = 15.0

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia cacheada de la configuración."""
    return Settings()
