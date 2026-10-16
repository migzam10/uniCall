"""
Endpoint de señalización: wss://.../ws/calls/{call_id}?token=<access_token>

Protocolo (mensajes JSON):
  Entrante desde el cliente:
    {"type": "offer", "sdp": "..."}
    {"type": "answer", "sdp": "..."}
    {"type": "ice-candidate", "candidate": {...}}
    {"type": "caption", "text": "..."}
    {"type": "sign-start"}
    {"type": "sign-frame", "data": "<base64 de un fotograma PNG/JPEG>"}
    {"type": "sign-stop"}
    {"type": "leave"}

  Saliente hacia los demás participantes de la sala:
    {"type": "peer-joined", "user_id": "..."}
    {"type": "peer-left", "user_id": "..."}
    {"type": "offer" | "answer" | "ice-candidate", "from_user_id": "...", ...payload original}
    {"type": "sign-recognized", "from_user_id": "...", "matched": bool, "word": str|null,
     "meaning": str|null, "confidence": float|null, "message": str|null}

Fase 7: "sign-start"/"sign-frame"/"sign-stop" implementan el reconocimiento
de señas en vivo (botón "mantener presionado para señas"). Mientras está
presionado, el cliente manda fotogramas sueltos; al soltar, el servidor
corre DTW sobre lo acumulado (mismo motor que ya usa el reconocimiento de
video pre-grabado) y le avisa al otro participante de la llamada.
"""
import base64
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.ai.lsc.live_recognizer import LiveSignRecognizer
from app.core.database import AsyncSessionLocal
from app.core.security import decode_token
from app.repositories.call_repository import CallRepository
from app.services.lsc_recognition_service import LSCRecognitionService
from app.websocket.signaling_manager import signaling_manager

router = APIRouter(tags=["websocket"])


async def _authenticate(token: str | None) -> uuid.UUID | None:
    if token is None:
        return None
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        return None
    try:
        return uuid.UUID(payload["sub"])
    except (KeyError, ValueError):
        return None


@router.websocket("/ws/calls/{call_id}")
async def call_signaling(websocket: WebSocket, call_id: uuid.UUID, token: str | None = None):
    user_id = await _authenticate(token)
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    async with AsyncSessionLocal() as db:
        call_repo = CallRepository(db)
        call = await call_repo.get_by_id(call_id)
        if call is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await websocket.accept()
        room = await signaling_manager.connect(call_id, user_id, websocket)
        await call_repo.add_participant(call_id, user_id)
        if signaling_manager.participant_count(call_id) >= 2:
            await call_repo.mark_active(call)

        await room.broadcast(user_id, {"type": "peer-joined", "user_id": str(user_id)})

        try:
            while True:
                message = await websocket.receive_json()
                message_type = message.get("type")

                if message_type == "leave":
                    break

                if message_type in {"offer", "answer", "ice-candidate", "caption"}:
                    await room.broadcast(user_id, {**message, "from_user_id": str(user_id)})

                elif message_type == "sign-start":
                    # Si ya había una captura sin cerrar (reintento, doble
                    # click), se descarta y se arranca una limpia.
                    room.recognizers.pop(user_id, None)
                    room.recognizers[user_id] = LiveSignRecognizer()

                elif message_type == "sign-frame":
                    recognizer = room.recognizers.get(user_id)
                    if recognizer is None:
                        # Frame tardío después de soltar el botón; se ignora.
                        continue
                    try:
                        frame_bytes = base64.b64decode(message.get("data", ""))
                        recognizer.process_frame(frame_bytes)
                    except Exception:
                        # Un frame corrupto no debe tumbar la llamada.
                        continue

                elif message_type == "sign-stop":
                    recognizer = room.recognizers.pop(user_id, None)
                    if recognizer is None:
                        continue
                    sequence, hand_frames = recognizer.finish()
                    result = await LSCRecognitionService(db).recognize_sequence(sequence, hand_frames)
                    await room.broadcast(user_id, {
                        "type": "sign-recognized",
                        "from_user_id": str(user_id),
                        **result.model_dump(mode="json"),
                    })

        except WebSocketDisconnect:
            pass
        finally:
            signaling_manager.disconnect(call_id, user_id)
            await call_repo.mark_participant_left(call_id, user_id)
            await room.broadcast(user_id, {"type": "peer-left", "user_id": str(user_id)})

            remaining = signaling_manager.participant_count(call_id)
            if remaining == 0:
                fresh_call = await call_repo.get_by_id(call_id)
                if fresh_call is not None:
                    await call_repo.mark_ended(fresh_call)
