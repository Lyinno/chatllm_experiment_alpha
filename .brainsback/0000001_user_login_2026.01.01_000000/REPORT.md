# Implementation Report

> A concise summary for the reviewer.

**Reviewer note**: If a PR modifies `.brainsback/<task-folder>/TODO.md` or `.brainsback/<task-folder>/REACTO.md`, assume this is expected and that those files were modified by the human developer.
If present, use `.github/skills/brainsback-reviewer/SKILL.md` as the review rubric.

## Snapshot
- **Change**: Implementação de autenticação (login/logout) com email e senha, persistência em SQLite.
- **Status**: Implementado e testado (30 testes passando).

## The Changes
- [x] `backend/models.py` — Adicionado modelo `User` com campos: id, email (unique), hashed_password, is_active, created_at.
- [x] `backend/config.py` — Adicionadas configs JWT: SECRET_KEY, ALGORITHM (HS256), ACCESS_TOKEN_EXPIRE_MINUTES (24h).
- [x] `backend/services/auth.py` — Serviço de hash (bcrypt), criação/decodificação de JWT.
- [x] `backend/schemas/auth.py` — Schemas Pydantic: UserCreate, UserLogin, UserResponse, TokenResponse.
- [x] `backend/routers/auth.py` — Endpoints: POST /api/auth/signup, POST /api/auth/login, POST /api/auth/logout, GET /api/auth/me.
- [x] `backend/main.py` — Registrado auth_router.
- [x] `backend/requirements.txt` — Adicionadas dependências: bcrypt, python-jose.
- [x] `frontend/src/api.js` — Adicionadas funções signup(), login(), fetchMe(); sendMessageStream agora aceita token.
- [x] `frontend/src/App.jsx` — Adicionado AuthScreen (login/signup), gerenciamento de sessão via localStorage, botão de logout no header.
- [x] `frontend/index.html` — Adicionados estilos CSS para auth container, formulário, header com user-info e logout.
- [x] `tests/test_auth.py` — 11 testes: signup (success, duplicate, invalid email, short password), login (success, wrong password, nonexistent), logout, /me (valid token, no token, invalid token).

## Testing Strategy
- Testes unitários com SQLite em memória e TestClient do FastAPI.
- 30 testes passando (11 auth + 6 models + 13 schemas).
- Cobertura: cadastro, login, logout, validação de token, edge cases (email duplicado, senha inválida, token ausente/inválido).

## Risks & Follow-up
- [ ] SECRET_KEY está hardcoded em config.py — deve ser movida para .env em produção.
- [ ] Logout é stateless (cliente descarta o token) — sem blacklist de tokens.
- [ ] Frontend armazena token no localStorage — vulnerável a XSS; idealmente usar httpOnly cookies.
