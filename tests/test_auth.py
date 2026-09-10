from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.models import User


class TestAuthSignup:
    def test_signup_success(self, client: TestClient):
        """Deve cadastrar um novo usuario com sucesso."""
        response = client.post(
            "/api/auth/signup",
            json={"email": "teste@example.com", "password": "123456"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "teste@example.com"
        assert data["user"]["is_active"] is True
        assert "id" in data["user"]

    def test_signup_duplicate_email(self, client: TestClient):
        """Deve rejeitar cadastro com email duplicado."""
        client.post(
            "/api/auth/signup",
            json={"email": "dup@example.com", "password": "123456"},
        )
        response = client.post(
            "/api/auth/signup",
            json={"email": "dup@example.com", "password": "654321"},
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    def test_signup_invalid_email(self, client: TestClient):
        """Deve rejeitar email sem formato valido."""
        response = client.post(
            "/api/auth/signup",
            json={"email": "invalido", "password": "123456"},
        )
        assert response.status_code == 422

    def test_signup_short_password(self, client: TestClient):
        """Deve rejeitar senha com menos de 6 caracteres."""
        response = client.post(
            "/api/auth/signup",
            json={"email": "valido@example.com", "password": "123"},
        )
        assert response.status_code == 422


class TestAuthLogin:
    def test_login_success(self, client: TestClient):
        """Deve logar com credenciais validas."""
        client.post(
            "/api/auth/signup",
            json={"email": "login@example.com", "password": "123456"},
        )
        response = client.post(
            "/api/auth/login",
            json={"email": "login@example.com", "password": "123456"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "login@example.com"

    def test_login_wrong_password(self, client: TestClient):
        """Deve rejeitar login com senha incorreta."""
        client.post(
            "/api/auth/signup",
            json={"email": "wrongpw@example.com", "password": "123456"},
        )
        response = client.post(
            "/api/auth/login",
            json={"email": "wrongpw@example.com", "password": "wrong"},
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client: TestClient):
        """Deve rejeitar login de usuario inexistente."""
        response = client.post(
            "/api/auth/login",
            json={"email": "noone@example.com", "password": "123456"},
        )
        assert response.status_code == 401


class TestAuthLogout:
    def test_logout_returns_message(self, client: TestClient):
        """Logout deve retornar mensagem de sucesso."""
        response = client.post("/api/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"


class TestAuthMe:
    def test_me_with_valid_token(self, client: TestClient):
        """Deve retornar dados do usuario com token valido."""
        signup_resp = client.post(
            "/api/auth/signup",
            json={"email": "me@example.com", "password": "123456"},
        )
        token = signup_resp.json()["access_token"]

        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["email"] == "me@example.com"

    def test_me_without_token(self, client: TestClient):
        """Deve retornar 401 sem token."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_me_with_invalid_token(self, client: TestClient):
        """Deve retornar 401 com token invalido."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalidtoken123"},
        )
        assert response.status_code == 401