// POST /ask — proxies one noul question to Jev.
// Never emits 5xx (Cloudflare replaces those with its own HTML page):
// runtime errors return 200 { error }.

const TYPESAFE_URL = 'https://api.typesafe.ai/v1/systemone';
const INSTRUCTIONS =
  '`question` is a yes/no question. Answer it truthfully to the best of your ' +
  'knowledge. True means the honest answer is YES; false means the honest answer is NO.';

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });

export async function ask(request, env) {
  let question = '';
  try {
    question = String((await request.json()).question || '').trim();
  } catch {
    return json({ error: 'invalid JSON' }, 400);
  }
  if (!question) return json({ error: 'question is required' }, 400);
  if (question.length > 500) return json({ error: 'question too long' }, 400);

  const apiKey = env.TYPESAFE_API_KEY;
  if (!apiKey) return json({ error: 'TYPESAFE_API_KEY is not configured' });

  const model = env.JEV_MODEL || 'jev-latest';
  try {
    const r = await fetch(TYPESAFE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
        'User-Agent': 'yes-or-no/0.1',
      },
      body: JSON.stringify({
        model,
        state: { question },
        questions: { answer: { type: 'noul', instructions: INSTRUCTIONS } },
      }),
    });
    if (!r.ok) return json({ error: `Jev HTTP ${r.status}: ${await r.text()}` });
    const data = await r.json();
    const p_yes = Number(data.answers.answer.noul);
    return json({
      question,
      p_yes,
      answer: p_yes >= 0.5 ? 'yes' : 'no',
      model: data.model || model,
      usage: data.usage || {},
    });
  } catch (e) {
    return json({ error: String(e && e.message ? e.message : e) });
  }
}
