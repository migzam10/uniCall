import base64

import pytest


async def _register_and_login(client, username: str, email: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": username.title(),
            "username": username,
            "email": email,
            "password": "password123",
            "role": "oyente",
        },
    )
    login = await client.post(
        "/api/v1/auth/login", json={"username_or_email": username, "password": "password123"}
    )
    return login.json()["access_token"]


@pytest.mark.asyncio
async def test_synthesize_generates_valid_wav_audio(client):
    token = await _register_and_login(client, "usera", "a@example.com")
    resp = await client.post(
        "/api/v1/speech/synthesize",
        json={"text": "Hola, buenos días", "voice": "femenina"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["mime_type"] == "audio/wav"

    audio_bytes = base64.b64decode(body["audio_base64"])
    assert len(audio_bytes) > 1000
    assert audio_bytes[:4] == b"RIFF"
    assert audio_bytes[8:12] == b"WAVE"


@pytest.mark.asyncio
async def test_synthesize_masculine_and_feminine_produce_different_audio(client):
    token = await _register_and_login(client, "usera", "a@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    fem_resp = await client.post(
        "/api/v1/speech/synthesize", json={"text": "Hola", "voice": "femenina"}, headers=headers
    )
    masc_resp = await client.post(
        "/api/v1/speech/synthesize", json={"text": "Hola", "voice": "masculina"}, headers=headers
    )

    fem_audio = base64.b64decode(fem_resp.json()["audio_base64"])
    masc_audio = base64.b64decode(masc_resp.json()["audio_base64"])
    assert fem_audio != masc_audio


@pytest.mark.asyncio
async def test_synthesize_empty_text_is_rejected(client):
    token = await _register_and_login(client, "usera", "a@example.com")
    resp = await client.post(
        "/api/v1/speech/synthesize",
        json={"text": "", "voice": "femenina"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_transcribe_with_mock_engine(client):
    token = await _register_and_login(client, "usera", "a@example.com")
    files = {"audio": ("test.wav", b"contenido-de-audio-simulado", "audio/wav")}
    resp = await client.post(
        "/api/v1/speech/transcribe", files=files, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["text"]
    assert resp.json()["language"] == "es"


@pytest.mark.asyncio
async def test_speech_endpoints_require_authentication(client):
    resp = await client.post("/api/v1/speech/synthesize", json={"text": "Hola", "voice": "femenina"})
    assert resp.status_code == 401
