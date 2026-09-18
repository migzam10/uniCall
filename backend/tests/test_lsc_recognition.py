import io

import pytest

from app.ai.lsc.dtw import dtw_distance
from app.ai.lsc.landmark_extractor import FRAME_VECTOR_SIZE, VideoLandmarkExtractor


async def _register_and_login(client, username: str, email: str, role: str = "administrador") -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": username.title(),
            "username": username,
            "email": email,
            "password": "password123",
            "role": role,
        },
    )
    login = await client.post(
        "/api/v1/auth/login", json={"username_or_email": username, "password": "password123"}
    )
    return login.json()["access_token"]


def _make_synthetic_mp4_bytes() -> bytes:
    """Genera un archivo mp4 sintético válido (sin personas reales)."""
    import tempfile
    from pathlib import Path

    import cv2
    import numpy as np

    tmp_path = Path(tempfile.mktemp(suffix=".mp4"))
    writer = cv2.VideoWriter(str(tmp_path), cv2.VideoWriter_fourcc(*"mp4v"), 10, (320, 240))
    for i in range(15):
        frame = np.full((240, 320, 3), (i * 15) % 255, dtype=np.uint8)
        writer.write(frame)
    writer.release()
    content = tmp_path.read_bytes()
    tmp_path.unlink()
    return content


# --- Unidad: DTW ---

def test_dtw_distance_identical_sequences_is_zero():
    seq = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]
    assert dtw_distance(seq, seq) == 0.0


def test_dtw_distance_different_sequences_is_positive():
    seq_a = [[1.0, 2.0], [3.0, 4.0]]
    seq_b = [[10.0, 20.0], [30.0, 40.0]]
    assert dtw_distance(seq_a, seq_b) > 0


def test_dtw_distance_empty_sequence_is_infinite():
    assert dtw_distance([], [[1.0, 2.0]]) == float("inf")


# --- Unidad: extracción de landmarks (con video sintético real) ---

def test_landmark_extraction_on_synthetic_video_produces_correct_shape():
    video_bytes = _make_synthetic_mp4_bytes()
    import tempfile
    from pathlib import Path

    tmp_path = Path(tempfile.mktemp(suffix=".mp4"))
    tmp_path.write_bytes(video_bytes)

    extractor = VideoLandmarkExtractor(target_fps=5, max_frames=10)
    sequence, hand_frames = extractor.extract_from_file(str(tmp_path))
    tmp_path.unlink()

    assert len(sequence) > 0
    assert len(sequence[0]) == FRAME_VECTOR_SIZE
    # El video sintético no contiene una persona real, por lo que no se
    # detectan manos (limitación esperada y validada explícitamente aquí).
    assert hand_frames == 0


# --- Integración: endpoints, con la extracción real (video sin manos) ---

@pytest.mark.asyncio
async def test_process_video_rejects_clip_without_hands(client):
    token = await _register_and_login(client, "admin1", "admin1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    category = (await client.post("/api/v1/admin/lsc/categories", json={"name": "Saludos"}, headers=headers)).json()
    sign = (
        await client.post(
            "/api/v1/admin/lsc/signs",
            json={"category_id": category["id"], "word": "hola", "meaning": "Saludo"},
            headers=headers,
        )
    ).json()

    files = {"video": ("hola.mp4", io.BytesIO(_make_synthetic_mp4_bytes()), "video/mp4")}
    upload = (await client.post(f"/api/v1/admin/lsc/signs/{sign['id']}/videos", files=files, headers=headers)).json()

    resp = await client.post(f"/api/v1/admin/lsc/videos/{upload['id']}/process", headers=headers)
    assert resp.status_code == 422
    assert "manos" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_process_video_requires_existing_video(client):
    token = await _register_and_login(client, "admin1", "admin1@example.com")
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = await client.post(
        f"/api/v1/admin/lsc/videos/{fake_id}/process", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_recognize_rejects_clip_without_hands(client, monkeypatch):
    import app.services.lsc_recognition_service as recognition_module

    # Se necesita al menos una plantilla publicada para que el servicio
    # llegue a evaluar la detección de manos del clip de consulta (si no
    # hay plantillas, responde antes con un mensaje distinto, también
    # correcto, cubierto en la prueba siguiente).
    admin_token = await _register_and_login(client, "admin1", "admin1@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    category = (
        await client.post("/api/v1/admin/lsc/categories", json={"name": "Saludos"}, headers=admin_headers)
    ).json()
    sign = (
        await client.post(
            "/api/v1/admin/lsc/signs",
            json={"category_id": category["id"], "word": "hola", "meaning": "Saludo"},
            headers=admin_headers,
        )
    ).json()
    await client.patch(f"/api/v1/admin/lsc/signs/{sign['id']}", json={"status": "published"}, headers=admin_headers)
    files = {"video": ("hola.mp4", io.BytesIO(_make_synthetic_mp4_bytes()), "video/mp4")}
    video = (
        await client.post(f"/api/v1/admin/lsc/signs/{sign['id']}/videos", files=files, headers=admin_headers)
    ).json()
    monkeypatch.setattr(
        recognition_module.VideoLandmarkExtractor, "extract_from_file", lambda self, path: (SEQ_HOLA, 3)
    )
    await client.post(f"/api/v1/admin/lsc/videos/{video['id']}/process", headers=admin_headers)
    monkeypatch.undo()  # se restaura el extractor real de MediaPipe

    # Ahora sí: un clip real (sintético, sin manos detectables) debe
    # rechazarse explícitamente por falta de detección de manos.
    token = await _register_and_login(client, "usera", "a@example.com", role="sordo")
    files2 = {"video": ("clip.mp4", io.BytesIO(_make_synthetic_mp4_bytes()), "video/mp4")}
    resp = await client.post(
        "/api/v1/lsc/recognize", files=files2, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["matched"] is False
    assert "manos" in body["message"].lower()


@pytest.mark.asyncio
async def test_recognize_with_no_published_templates_returns_helpful_message(client):
    token = await _register_and_login(client, "usera", "a@example.com", role="sordo")
    files = {"video": ("clip.mp4", io.BytesIO(_make_synthetic_mp4_bytes()), "video/mp4")}
    resp = await client.post(
        "/api/v1/lsc/recognize", files=files, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["matched"] is False


# --- Integración: flujo completo con extractor controlado ---
#
# MediaPipe no detecta manos en video sintético (no hay una persona real
# filmada), por lo que para probar el flujo de EMPARENAMIENTO end-to-end se
# sustituye el extractor real por uno determinístico. Esto prueba
# honestamente la lógica de comparación DTW + umbral de confianza, no la
# precisión del modelo de visión (que requiere video real de LSC, fuera del
# alcance de este entorno de pruebas).

SEQ_HOLA = [[0.1, 0.2, 0.3], [0.15, 0.25, 0.35], [0.2, 0.3, 0.4]]
SEQ_GRACIAS = [[100.0, 120.0, 140.0], [110.0, 130.0, 150.0], [120.0, 140.0, 160.0]]


class _FakeExtractor:
    """Devuelve secuencias fijas según el orden de llamada, simulando
    landmarks ya conocidos en vez de correr MediaPipe de verdad."""

    def __init__(self, sequences_with_hands: list[tuple[list[list[float]], int]]):
        self._calls = iter(sequences_with_hands)

    def extract_from_file(self, path: str):
        return next(self._calls)


@pytest.mark.asyncio
async def test_full_recognition_flow_with_controlled_extractor(client, monkeypatch):
    import app.services.lsc_recognition_service as recognition_module

    token = await _register_and_login(client, "admin1", "admin1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    category = (await client.post("/api/v1/admin/lsc/categories", json={"name": "Saludos"}, headers=headers)).json()
    sign_hola = (
        await client.post(
            "/api/v1/admin/lsc/signs",
            json={"category_id": category["id"], "word": "hola", "meaning": "Saludo informal"},
            headers=headers,
        )
    ).json()
    await client.patch(f"/api/v1/admin/lsc/signs/{sign_hola['id']}", json={"status": "published"}, headers=headers)

    files = {"video": ("hola.mp4", io.BytesIO(_make_synthetic_mp4_bytes()), "video/mp4")}
    video = (
        await client.post(f"/api/v1/admin/lsc/signs/{sign_hola['id']}/videos", files=files, headers=headers)
    ).json()

    # 1) Procesar el video de referencia: el extractor "ve" SEQ_HOLA con manos detectadas.
    monkeypatch.setattr(
        recognition_module.VideoLandmarkExtractor,
        "extract_from_file",
        lambda self, path: (SEQ_HOLA, 3),
    )
    process_resp = await client.post(f"/api/v1/admin/lsc/videos/{video['id']}/process", headers=headers)
    assert process_resp.status_code == 201
    assert process_resp.json()["frame_count"] == len(SEQ_HOLA)

    # 2) Reconocer un clip que produce EXACTAMENTE la misma secuencia -> debe
    #    emparejar con alta confianza.
    monkeypatch.setattr(
        recognition_module.VideoLandmarkExtractor,
        "extract_from_file",
        lambda self, path: (SEQ_HOLA, 3),
    )
    sordo_token = await _register_and_login(client, "userb", "b@example.com", role="sordo")
    match_files = {"video": ("clip.mp4", io.BytesIO(_make_synthetic_mp4_bytes()), "video/mp4")}
    match_resp = await client.post(
        "/api/v1/lsc/recognize", files=match_files, headers={"Authorization": f"Bearer {sordo_token}"}
    )
    assert match_resp.status_code == 200
    match_body = match_resp.json()
    assert match_body["matched"] is True
    assert match_body["word"] == "hola"
    assert match_body["confidence"] > 0.9

    # 3) Reconocer un clip MUY distinto -> no debe emparejar (evita
    #    "inventar" una seña con baja confianza, sección 29).
    monkeypatch.setattr(
        recognition_module.VideoLandmarkExtractor,
        "extract_from_file",
        lambda self, path: (SEQ_GRACIAS, 3),
    )
    mismatch_files = {"video": ("clip2.mp4", io.BytesIO(_make_synthetic_mp4_bytes()), "video/mp4")}
    mismatch_resp = await client.post(
        "/api/v1/lsc/recognize", files=mismatch_files, headers={"Authorization": f"Bearer {sordo_token}"}
    )
    assert mismatch_resp.status_code == 200
    mismatch_body = mismatch_resp.json()
    assert mismatch_body["matched"] is False
    assert mismatch_body["closest_word"] == "hola"


@pytest.mark.asyncio
async def test_cannot_process_same_video_twice(client, monkeypatch):
    import app.services.lsc_recognition_service as recognition_module

    token = await _register_and_login(client, "admin1", "admin1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    category = (await client.post("/api/v1/admin/lsc/categories", json={"name": "Saludos"}, headers=headers)).json()
    sign = (
        await client.post(
            "/api/v1/admin/lsc/signs",
            json={"category_id": category["id"], "word": "hola", "meaning": "Saludo"},
            headers=headers,
        )
    ).json()
    files = {"video": ("hola.mp4", io.BytesIO(_make_synthetic_mp4_bytes()), "video/mp4")}
    video = (await client.post(f"/api/v1/admin/lsc/signs/{sign['id']}/videos", files=files, headers=headers)).json()

    monkeypatch.setattr(
        recognition_module.VideoLandmarkExtractor, "extract_from_file", lambda self, path: (SEQ_HOLA, 3)
    )
    first = await client.post(f"/api/v1/admin/lsc/videos/{video['id']}/process", headers=headers)
    assert first.status_code == 201

    second = await client.post(f"/api/v1/admin/lsc/videos/{video['id']}/process", headers=headers)
    assert second.status_code == 409
