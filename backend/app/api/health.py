import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Request

logger = logging.getLogger("uvicorn.info")

router = APIRouter(tags=["health"])


@router.get("/health")
@router.get("/api/v1/health")
@router.get("/api/v1/ping")
async def health_check(request: Request):
    """
    Endpoint para comprobar la conectividad del frontend con el backend.
    Soporta /health, /api/v1/health y /api/v1/ping.
    Registra la IP y cabeceras de origen en los logs del servidor.
    """
    client_ip = request.client.host if request.client else "desconocido"
    user_agent = request.headers.get("user-agent", "desconocido")
    logger.info(f"==> [FRONTEND PING] Conexión recibida exitosamente desde IP: {client_ip} | User-Agent: {user_agent}")

    return {
        "status": "ok",
        "frontend_connected": True,
        "message": "Backend conectado exitosamente con el frontend",
        "server_time": datetime.now(timezone.utc).isoformat(),
        "client_ip": client_ip,
    }
