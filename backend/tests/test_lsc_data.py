import io

import pytest


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


@pytest.mark.asyncio
async def test_category_crud_flow(client):
    admin_token = await _register_and_login(client, "admin1", "admin1@example.com")
    headers = {"Authorization": f"Bearer {admin_token}"}

    create_resp = await client.post(
        "/api/v1/admin/lsc/categories",
        json={"name": "Saludos", "description": "Expresiones de saludo"},
        headers=headers,
    )
    assert create_resp.status_code == 201
    category = create_resp.json()
    assert category["slug"] == "saludos"
    assert category["is_active"] is True

    # Duplicada -> 409
    dup_resp = await client.post(
        "/api/v1/admin/lsc/categories", json={"name": "Saludos"}, headers=headers
    )
    assert dup_resp.status_code == 409

    list_resp = await client.get("/api/v1/admin/lsc/categories", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    update_resp = await client.patch(
        f"/api/v1/admin/lsc/categories/{category['id']}",
        json={"is_active": False},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_only_admin_can_manage_categories(client):
    oyente_token = await _register_and_login(client, "usera", "a@example.com", role="oyente")
    resp = await client.post(
        "/api/v1/admin/lsc/categories",
        json={"name": "Saludos"},
        headers={"Authorization": f"Bearer {oyente_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_sign_crud_and_versioning(client):
    admin_token = await _register_and_login(client, "admin1", "admin1@example.com")
    headers = {"Authorization": f"Bearer {admin_token}"}

    category = (
        await client.post("/api/v1/admin/lsc/categories", json={"name": "Saludos"}, headers=headers)
    ).json()

    sign_resp = await client.post(
        "/api/v1/admin/lsc/signs",
        json={
            "category_id": category["id"],
            "word": "hola",
            "meaning": "Saludo informal",
            "tags": "saludo,informal",
        },
        headers=headers,
    )
    assert sign_resp.status_code == 201
    sign = sign_resp.json()
    assert sign["status"] == "draft"
    assert sign["version"] == 1

    # Publicar y versionar
    update_resp = await client.patch(
        f"/api/v1/admin/lsc/signs/{sign['id']}",
        json={"status": "published", "bump_version": True},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "published"
    assert update_resp.json()["version"] == 2

    list_resp = await client.get(
        "/api/v1/admin/lsc/signs", params={"category_id": category["id"]}, headers=headers
    )
    assert len(list_resp.json()) == 1


@pytest.mark.asyncio
async def test_sign_requires_existing_category(client):
    admin_token = await _register_and_login(client, "admin1", "admin1@example.com")
    headers = {"Authorization": f"Bearer {admin_token}"}
    fake_category_id = "00000000-0000-0000-0000-000000000000"

    resp = await client.post(
        "/api/v1/admin/lsc/signs",
        json={"category_id": fake_category_id, "word": "hola", "meaning": "Saludo"},
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_upload_video_for_sign(client):
    admin_token = await _register_and_login(client, "admin1", "admin1@example.com")
    headers = {"Authorization": f"Bearer {admin_token}"}

    category = (
        await client.post("/api/v1/admin/lsc/categories", json={"name": "Saludos"}, headers=headers)
    ).json()
    sign = (
        await client.post(
            "/api/v1/admin/lsc/signs",
            json={"category_id": category["id"], "word": "hola", "meaning": "Saludo"},
            headers=headers,
        )
    ).json()

    fake_video_bytes = b"\x00\x00\x00\x18ftypmp42" + b"0" * 500  # cabecera MP4 simulada
    files = {"video": ("hola.mp4", io.BytesIO(fake_video_bytes), "video/mp4")}
    upload_resp = await client.post(
        f"/api/v1/admin/lsc/signs/{sign['id']}/videos", files=files, headers=headers
    )
    assert upload_resp.status_code == 201
    video = upload_resp.json()
    assert video["sign_id"] == sign["id"]
    assert video["size_bytes"] == len(fake_video_bytes)
    assert video["url"].startswith("http")

    # Aparece al consultar la seña con sus videos
    sign_detail = await client.get(f"/api/v1/admin/lsc/signs/{sign['id']}", headers=headers)
    assert len(sign_detail.json()["videos"]) == 1

    # Tipo de archivo no soportado -> 400
    bad_files = {"video": ("hola.txt", io.BytesIO(b"no es un video"), "text/plain")}
    bad_resp = await client.post(
        f"/api/v1/admin/lsc/signs/{sign['id']}/videos", files=bad_files, headers=headers
    )
    assert bad_resp.status_code == 400

    # Eliminar el video
    delete_resp = await client.delete(f"/api/v1/admin/lsc/videos/{video['id']}", headers=headers)
    assert delete_resp.status_code == 204


@pytest.mark.asyncio
async def test_phrase_with_sign_sequence(client):
    admin_token = await _register_and_login(client, "admin1", "admin1@example.com")
    headers = {"Authorization": f"Bearer {admin_token}"}

    category = (
        await client.post("/api/v1/admin/lsc/categories", json={"name": "Saludos"}, headers=headers)
    ).json()

    sign_hola = (
        await client.post(
            "/api/v1/admin/lsc/signs",
            json={"category_id": category["id"], "word": "hola", "meaning": "Saludo"},
            headers=headers,
        )
    ).json()
    sign_como = (
        await client.post(
            "/api/v1/admin/lsc/signs",
            json={"category_id": category["id"], "word": "como", "meaning": "Cómo"},
            headers=headers,
        )
    ).json()
    sign_estas = (
        await client.post(
            "/api/v1/admin/lsc/signs",
            json={"category_id": category["id"], "word": "estas", "meaning": "Estás"},
            headers=headers,
        )
    ).json()

    phrase_resp = await client.post(
        "/api/v1/admin/lsc/phrases",
        json={
            "text": "Hola, ¿cómo estás?",
            "signs": [
                {"sign_id": sign_hola["id"], "position": 0},
                {"sign_id": sign_como["id"], "position": 1},
                {"sign_id": sign_estas["id"], "position": 2},
            ],
        },
        headers=headers,
    )
    assert phrase_resp.status_code == 201
    phrase = phrase_resp.json()
    assert [s["word"] for s in phrase["signs"]] == ["hola", "como", "estas"]

    # Posiciones duplicadas -> 400
    bad_resp = await client.post(
        "/api/v1/admin/lsc/phrases",
        json={
            "text": "Frase inválida",
            "signs": [
                {"sign_id": sign_hola["id"], "position": 0},
                {"sign_id": sign_como["id"], "position": 0},
            ],
        },
        headers=headers,
    )
    assert bad_resp.status_code == 400

    # Actualizar la secuencia
    update_resp = await client.patch(
        f"/api/v1/admin/lsc/phrases/{phrase['id']}",
        json={"signs": [{"sign_id": sign_estas["id"], "position": 0}]},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert [s["word"] for s in update_resp.json()["signs"]] == ["estas"]

    list_resp = await client.get("/api/v1/admin/lsc/phrases", headers=headers)
    assert len(list_resp.json()) == 1
