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
async def test_search_users_excludes_self(client):
    token_a = await _register_and_login(client, "usera", "a@example.com")
    await _register_and_login(client, "userb", "b@example.com")

    resp = await client.get(
        "/api/v1/contacts/search", params={"q": "user"}, headers={"Authorization": f"Bearer {token_a}"}
    )
    assert resp.status_code == 200
    usernames = [u["username"] for u in resp.json()]
    assert "userb" in usernames
    assert "usera" not in usernames


@pytest.mark.asyncio
async def test_contact_request_full_flow(client):
    token_a = await _register_and_login(client, "usera", "a@example.com")
    token_b = await _register_and_login(client, "userb", "b@example.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # A envía solicitud a B
    send_resp = await client.post(
        "/api/v1/contacts/requests", json={"to_username": "userb"}, headers=headers_a
    )
    assert send_resp.status_code == 201
    request_id = send_resp.json()["id"]

    # Duplicada -> 409
    dup_resp = await client.post(
        "/api/v1/contacts/requests", json={"to_username": "userb"}, headers=headers_a
    )
    assert dup_resp.status_code == 409

    # B ve la solicitud entrante
    incoming_resp = await client.get("/api/v1/contacts/requests/incoming", headers=headers_b)
    assert incoming_resp.status_code == 200
    assert len(incoming_resp.json()) == 1

    # B acepta
    accept_resp = await client.post(f"/api/v1/contacts/requests/{request_id}/accept", headers=headers_b)
    assert accept_resp.status_code == 204

    # Ambos se ven como contactos
    contacts_a = await client.get("/api/v1/contacts", headers=headers_a)
    contacts_b = await client.get("/api/v1/contacts", headers=headers_b)
    assert any(c["username"] == "userb" for c in contacts_a.json())
    assert any(c["username"] == "usera" for c in contacts_b.json())


@pytest.mark.asyncio
async def test_reject_contact_request(client):
    token_a = await _register_and_login(client, "usera", "a@example.com")
    token_b = await _register_and_login(client, "userb", "b@example.com")

    send_resp = await client.post(
        "/api/v1/contacts/requests",
        json={"to_username": "userb"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    request_id = send_resp.json()["id"]

    reject_resp = await client.post(
        f"/api/v1/contacts/requests/{request_id}/reject",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert reject_resp.status_code == 204

    contacts_a = await client.get(
        "/api/v1/contacts", headers={"Authorization": f"Bearer {token_a}"}
    )
    assert contacts_a.json() == []


@pytest.mark.asyncio
async def test_remove_contact(client):
    token_a = await _register_and_login(client, "usera", "a@example.com")
    token_b = await _register_and_login(client, "userb", "b@example.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    send_resp = await client.post("/api/v1/contacts/requests", json={"to_username": "userb"}, headers=headers_a)
    request_id = send_resp.json()["id"]
    await client.post(f"/api/v1/contacts/requests/{request_id}/accept", headers=headers_b)

    user_b_resp = await client.get("/api/v1/contacts", headers=headers_a)
    user_b_id = user_b_resp.json()[0]["id"]

    remove_resp = await client.delete(f"/api/v1/contacts/{user_b_id}", headers=headers_a)
    assert remove_resp.status_code == 204

    contacts_a_after = await client.get("/api/v1/contacts", headers=headers_a)
    contacts_b_after = await client.get("/api/v1/contacts", headers=headers_b)
    assert contacts_a_after.json() == []
    assert contacts_b_after.json() == []
