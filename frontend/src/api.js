const API_BASE = window.location.origin;

// ─── Auth ────────────────────────────────────────────────────────────────

async function signup(email, password) {
  const response = await fetch(`${API_BASE}/api/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.detail || "Erro ao cadastrar.");
  return body;
}

async function login(email, password) {
  const response = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.detail || "Erro ao logar.");
  return body;
}

async function fetchMe(token) {
  const response = await fetch(`${API_BASE}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.detail || "Erro ao obter usuario.");
  return body;
}

// ─── Sessions ────────────────────────────────────────────────────────────

async function listSessions(token) {
  const response = await fetch(`${API_BASE}/api/sessions/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.detail || "Erro ao listar sessoes.");
  return body.sessions;
}

async function createSession(token) {
  const response = await fetch(`${API_BASE}/api/sessions/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: "{}",
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.detail || "Erro ao criar sessao.");
  return body;
}

async function deleteSession(token, sessionId) {
  const response = await fetch(`${API_BASE}/api/sessions/${sessionId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "Erro ao deletar sessao.");
  }
}

async function getSessionMessages(token, sessionId) {
  const response = await fetch(`${API_BASE}/api/sessions/${sessionId}/messages`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.detail || "Erro ao carregar mensagens.");
  return body;
}

// ─── Chat ────────────────────────────────────────────────────────────────

async function sendMessageStream({ message, history, sessionId, token, onDelta, signal }) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}/api/chat/stream`, {
    method: "POST",
    headers,
    body: JSON.stringify({ message, history, session_id: sessionId }),
    signal,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = body?.detail || "Erro ao enviar mensagem para o servidor.";
    throw new Error(detail);
  }

  if (!response.body) {
    throw new Error("Streaming nao suportado no ambiente atual.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";
  let lastSessionId = sessionId;

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() || "";

    for (const rawEvent of events) {
      const line = rawEvent
        .split("\n")
        .find((part) => part.startsWith("data:"));
      if (!line) continue;

      const payloadText = line.slice(5).trim();
      if (!payloadText) continue;

      let payload;
      try {
        payload = JSON.parse(payloadText);
      } catch {
        continue;
      }

      if (payload.error) {
        // Don't throw — just capture session_id if present and continue
        if (payload.session_id) lastSessionId = payload.session_id;
        continue;
      }

      if (payload.delta) {
        onDelta(payload.delta);
      }

      if (payload.session_id) {
        lastSessionId = payload.session_id;
      }
    }
  }

  return lastSessionId;
}
