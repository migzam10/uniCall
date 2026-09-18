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
async def test_create_and_join_call_by_code(client):
    token_a = await _register_and_login(client, "usera", "a@example.com")
    token_b = await _register_and_login(client, "userb", "b@example.com")

    create_resp = await client.post("/api/v1/calls", headers={"Authorization": f"Bearer {token_a}"})
    assert create_resp.status_code == 201
    call = create_resp.json()
    assert len(call["code"]) == 8
    assert call["status"] == "waiting"

    join_resp = await client.post(
        "/api/v1/calls/join",
        json={"code": call["code"]},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert join_resp.status_code == 200
    assert join_resp.json()["id"] == call["id"]


@pytest.mark.asyncio
async def test_join_invalid_code_returns_404(client):
    token = await _register_and_login(client, "usera", "a@example.com")
    resp = await client.post(
        "/api/v1/calls/join", json={"code": "NOEXISTE"}, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_direct_call_requires_contact(client):
    token_a = await _register_and_login(client, "usera", "a@example.com")
    token_b = await _register_and_login(client, "userb", "b@example.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    me_b = await client.get("/api/v1/users/me", headers=headers_b)
    user_b_id = me_b.json()["user"]["id"]

    # Sin ser contactos -> 403
    forbidden_resp = await client.post(
        "/api/v1/calls/direct", json={"contact_user_id": user_b_id}, headers=headers_a
    )
    assert forbidden_resp.status_code == 403

    # Se hacen contactos
    send_resp = await client.post("/api/v1/contacts/requests", json={"to_username": "userb"}, headers=headers_a)
    request_id = send_resp.json()["id"]
    await client.post(f"/api/v1/contacts/requests/{request_id}/accept", headers=headers_b)

    # Ahora sí puede llamar directamente
    direct_resp = await client.post(
        "/api/v1/calls/direct", json={"contact_user_id": user_b_id}, headers=headers_a
    )
    assert direct_resp.status_code == 201

    # B ve la invitación pendiente
    invitations_resp = await client.get("/api/v1/calls/invitations", headers=headers_b)
    assert invitations_resp.status_code == 200
    assert len(invitations_resp.json()) == 1
    assert invitations_resp.json()[0]["from_username"] == "usera"


@pytest.mark.asyncio
async def test_ice_servers_endpoint(client):
    token = await _register_and_login(client, "usera", "a@example.com")
    resp = await client.get("/api/v1/calls/ice-servers", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    servers = resp.json()["ice_servers"]
    assert len(servers) >= 1
    assert servers[0]["urls"].startswith("stun:")


@pytest.mark.asyncio
async def test_calls_require_authentication(client):
    resp = await client.post("/api/v1/calls")
    assert resp.status_code == 401
