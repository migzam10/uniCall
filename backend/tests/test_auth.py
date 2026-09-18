import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Maria Perez",
            "username": "mariap",
            "email": "maria@example.com",
            "password": "password123",
            "role": "oyente",
        },
    )
    assert register_resp.status_code == 201
    assert register_resp.json()["role"] == "oyente"

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "mariap", "password": "password123"},
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()


@pytest.mark.asyncio
async def test_register_duplicate_username_fails(client):
    payload = {
        "full_name": "Maria Perez",
        "username": "mariap",
        "email": "maria@example.com",
        "password": "password123",
        "role": "oyente",
    }
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_login_with_wrong_password_fails(client):
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Maria Perez",
            "username": "mariap",
            "email": "maria@example.com",
            "password": "password123",
            "role": "oyente",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "mariap", "password": "wrong-password"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_requires_authentication(client):
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_profile_and_preferences_update(client):
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Juan Gomez",
            "username": "juang",
            "email": "juan@example.com",
            "password": "password123",
            "role": "sordo",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "juang", "password": "password123"},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_resp = await client.get("/api/v1/users/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["user"]["role"] == "sordo"

    profile_resp = await client.put(
        "/api/v1/users/me/profile",
        headers=headers,
        json={"bio": "Amo la accesibilidad", "location": "Bogota"},
    )
    assert profile_resp.status_code == 200
    assert profile_resp.json()["bio"] == "Amo la accesibilidad"

    prefs_resp = await client.put(
        "/api/v1/users/me/preferences",
        headers=headers,
        json={"voice_preference": "masculina", "show_avatar": False},
    )
    assert prefs_resp.status_code == 200
    assert prefs_resp.json()["voice_preference"] == "masculina"
    assert prefs_resp.json()["show_avatar"] is False


@pytest.mark.asyncio
async def test_admin_endpoints_are_restricted_by_role(client):
    # Usuario no-admin
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Maria Perez",
            "username": "mariap",
            "email": "maria@example.com",
            "password": "password123",
            "role": "oyente",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "mariap", "password": "password123"},
    )
    token = login_resp.json()["access_token"]

    forbidden_resp = await client.get(
        "/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert forbidden_resp.status_code == 403

    # Usuario admin
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Admin Root",
            "username": "adminroot",
            "email": "admin@example.com",
            "password": "password123",
            "role": "administrador",
        },
    )
    admin_login = await client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "adminroot", "password": "password123"},
    )
    admin_token = admin_login.json()["access_token"]

    allowed_resp = await client.get(
        "/api/v1/admin/users", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert allowed_resp.status_code == 200
    assert len(allowed_resp.json()) == 2
