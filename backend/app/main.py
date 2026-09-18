"""
Punto de entrada del backend.

Fases 1-2: autenticación, usuarios, roles, perfil, contactos, llamadas por
código/enlace y señalización WebRTC. Los routers de reconocimiento de voz,
IA de LSC y avatar se incorporarán en las fases siguientes sin modificar lo
ya implementado.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import admin, auth, calls, contacts, health, lsc_data, lsc_recognition, speech, users
from app.core.config import get_settings
from app.core.storage import STORAGE_ROOT
from app.websocket import signaling

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Backend de la plataforma de videollamadas accesibles con traducción de LSC.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(contacts.router)
app.include_router(calls.router)
app.include_router(speech.router)
app.include_router(lsc_data.router)
app.include_router(lsc_recognition.router)
app.include_router(signaling.router)

STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(STORAGE_ROOT)), name="media")


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": app.version,
        "status": "running",
        "docs": "/docs",
    }
