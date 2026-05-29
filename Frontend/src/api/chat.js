const BASE = import.meta.env.VITE_API_URL || '';

export async function askBackend(question, history = []) {
  const res = await fetch(`${BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history })
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Backend error');
  }
  return res.json();
}

/**
 * Streaming version. Calls onToken(str) for each chunk,
 * then resolves with { agent, sources } when done.
 */
export async function askBackendStream(question, history = [], onToken) {
  const res = await fetch(`${BASE}/ask/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history })
  });

  if (!res.ok) throw new Error(await res.text() || 'Backend error');

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let meta = { agent: null, sources: [] };

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop(); // keep incomplete last line

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      const payload = JSON.parse(line.slice(6));
      if (payload.token !== undefined) {
        onToken(payload.token);
      } else if (payload.done) {
        meta = { agent: payload.agent, sources: payload.sources };
      }
    }
  }
  return meta;
}
