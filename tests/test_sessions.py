from __future__ import annotations

from fastapi.testclient import TestClient


class TestSessionsAPI:
    def _auth_header(self, client: TestClient) -> dict:
        client.post(
            "/api/auth/signup",
            json={"email": "sess-test@example.com", "password": "123456"},
        )
        resp = client.post(
            "/api/auth/login",
            json={"email": "sess-test@example.com", "password": "123456"},
        )
        token = resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_list_sessions_empty(self, client: TestClient):
        """Deve retornar lista vazia para usuario sem sessoes."""
        headers = self._auth_header(client)
        response = client.get("/api/sessions/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["sessions"] == []

    def test_create_session(self, client: TestClient):
        """Deve criar uma nova sessao."""
        headers = self._auth_header(client)
        response = client.post("/api/sessions/", headers=headers, json={})
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Nova conversa"
        assert "id" in data

    def test_create_and_list_sessions(self, client: TestClient):
        """Deve listar sessoes apos criar."""
        headers = self._auth_header(client)
        client.post("/api/sessions/", headers=headers, json={})
        client.post("/api/sessions/", headers=headers, json={})
        response = client.get("/api/sessions/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) == 2

    def test_get_session_by_id(self, client: TestClient):
        """Deve retornar uma sessao especifica."""
        headers = self._auth_header(client)
        create_resp = client.post("/api/sessions/", headers=headers, json={})
        session_id = create_resp.json()["id"]
        response = client.get(f"/api/sessions/{session_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == session_id

    def test_get_session_not_found(self, client: TestClient):
        """Deve retornar 404 para sessao inexistente."""
        headers = self._auth_header(client)
        response = client.get("/api/sessions/99999", headers=headers)
        assert response.status_code == 404

    def test_update_title(self, client: TestClient):
        """Deve atualizar o titulo de uma sessao."""
        headers = self._auth_header(client)
        create_resp = client.post("/api/sessions/", headers=headers, json={})
        session_id = create_resp.json()["id"]
        response = client.patch(
            f"/api/sessions/{session_id}/title",
            headers=headers,
            json={"title": "Minha conversa"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Minha conversa"

    def test_delete_session(self, client: TestClient):
        """Deve deletar uma sessao."""
        headers = self._auth_header(client)
        create_resp = client.post("/api/sessions/", headers=headers, json={})
        session_id = create_resp.json()["id"]
        response = client.delete(f"/api/sessions/{session_id}", headers=headers)
        assert response.status_code == 204
        # Verify it's gone
        get_resp = client.get(f"/api/sessions/{session_id}", headers=headers)
        assert get_resp.status_code == 404

    def test_sessions_require_auth(self, client: TestClient):
        """Sessoes endpoints devem exigir autenticacao."""
        response = client.get("/api/sessions/")
        assert response.status_code == 401
        response = client.post("/api/sessions/", json={})
        assert response.status_code == 401

    def test_session_messages(self, client: TestClient):
        """Deve retornar mensagens de uma sessao."""
        headers = self._auth_header(client)
        create_resp = client.post("/api/sessions/", headers=headers, json={})
        session_id = create_resp.json()["id"]
        response = client.get(f"/api/sessions/{session_id}/messages", headers=headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_other_user_cannot_access_session(self, client: TestClient):
        """Usuario B nao deve acessar sessoes do usuario A."""
        # User A creates session
        client.post(
            "/api/auth/signup",
            json={"email": "user-a@test.com", "password": "123456"},
        )
        resp_a = client.post(
            "/api/auth/login",
            json={"email": "user-a@test.com", "password": "123456"},
        )
        token_a = resp_a.json()["access_token"]
        create_resp = client.post("/api/sessions/", headers={"Authorization": f"Bearer {token_a}"}, json={})
        session_id = create_resp.json()["id"]

        # User B tries to access
        client.post(
            "/api/auth/signup",
            json={"email": "user-b@test.com", "password": "123456"},
        )
        resp_b = client.post(
            "/api/auth/login",
            json={"email": "user-b@test.com", "password": "123456"},
        )
        token_b = resp_b.json()["access_token"]
        response = client.get(f"/api/sessions/{session_id}", headers={"Authorization": f"Bearer {token_b}"})
        assert response.status_code == 404