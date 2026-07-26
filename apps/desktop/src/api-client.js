async function login(apiBase, email, password) {
  const res = await fetch(`${apiBase}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    throw new Error('Login falhou');
  }
  return res.json();
}

async function publishDataset(apiBase, token, payload) {
  const res = await fetch(`${apiBase}/desktop/publish/dataset`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error('Publicação de dataset falhou');
  }
  return res.json();
}

async function publishDashboard(apiBase, token, payload) {
  const res = await fetch(`${apiBase}/desktop/publish/dashboard`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error('Publicação de dashboard falhou');
  }
  return res.json();
}

module.exports = { login, publishDataset, publishDashboard };
