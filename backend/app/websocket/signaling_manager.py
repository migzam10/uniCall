"""
Gestor de conexiones WebSocket para la señalización WebRTC.

Cada llamada es una "sala": los mensajes que un participante envía
(offer/answer/ICE candidates y control básico) se retransmiten a los demás
participantes de la misma sala. El audio/video real viaja directo entre
los usuarios por WebRTC; el servidor solo coordina la señalización
(sección 2 de la especificación: "no convertir al servidor en un
intermediario innecesario de todo el tráfico audiovisual").

Implementación en memoria, adecuada para un único proceso/servidor. En la
sección 26 (escalabilidad) se contempla separar esto en un "Signaling
Server" independiente cuando el proyecto lo requiera; en ese momento este
gestor se reemplazaría por uno respaldado en un pub/sub (p. ej. Redis).
"""
import uuid
from dataclasses import dataclass, field

from fastapi import WebSocket


@dataclass
class CallRoom:
    call_id: uuid.UUID
    connections: dict[uuid.UUID, WebSocket] = field(default_factory=dict)

    async def broadcast(self, sender_id: uuid.UUID, message: dict) -> None:
        for user_id, ws in list(self.connections.items()):
            if user_id == sender_id:
                continue
            try:
                await ws.send_json(message)
            except Exception:
                # Conexión rota; se limpiará en el próximo disconnect.
                continue


class SignalingManager:
    def __init__(self) -> None:
        self._rooms: dict[uuid.UUID, CallRoom] = {}

    def _get_or_create_room(self, call_id: uuid.UUID) -> CallRoom:
        if call_id not in self._rooms:
            self._rooms[call_id] = CallRoom(call_id=call_id)
        return self._rooms[call_id]

    async def connect(self, call_id: uuid.UUID, user_id: uuid.UUID, websocket: WebSocket) -> CallRoom:
        room = self._get_or_create_room(call_id)
        room.connections[user_id] = websocket
        return room

    def disconnect(self, call_id: uuid.UUID, user_id: uuid.UUID) -> None:
        room = self._rooms.get(call_id)
        if room is None:
            return
        room.connections.pop(user_id, None)
        if not room.connections:
            self._rooms.pop(call_id, None)

    def participant_count(self, call_id: uuid.UUID) -> int:
        room = self._rooms.get(call_id)
        return len(room.connections) if room else 0


# Instancia única compartida por la aplicación.
signaling_manager = SignalingManager()
