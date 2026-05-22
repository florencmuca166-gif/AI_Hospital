export async function askBackend(question, history = []) {
  const res = await fetch('/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history })
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Backend error');
  }

  return await res.json();
}
