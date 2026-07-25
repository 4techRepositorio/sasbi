const form = document.getElementById('login');
const statusEl = document.getElementById('status');

form.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const data = new FormData(form);
  statusEl.textContent = 'A autenticar…';
  try {
    await window.fourproDesktop.login(data.get('email'), data.get('password'));
    statusEl.textContent = 'Sessão iniciada. Pode publicar via API do Desktop.';
    await window.fourproDesktop.publishDataset({
      title: 'Desktop demo',
      rows: [{ metric: 1 }],
      layer: 'gold',
    });
    statusEl.textContent = 'Dataset de demonstração publicado no catálogo do tenant.';
  } catch (err) {
    statusEl.textContent = err?.message || 'Falha na operação.';
  }
});
