# Yes or No

Ask [Jev](https://typesafe.ai) (TypeSafe's System-One model) a yes/no question. Jev
doesn't generate text — it returns P(yes) — so the app shows Yes/No and the probability.

Live: https://yesno.jakecuth.com

## Layout

- `public/index.html` — the whole UI, no build step.
- `worker.js` + `ask.js` — Cloudflare Worker: `POST /ask` proxies to
  `POST https://api.typesafe.ai/v1/systemone` (key stays server-side); everything
  else is served from `public/` as static assets (`wrangler.jsonc`).
- `server.py` — same thing for local dev, stdlib only.

## Deploy (Cloudflare Workers)

Workers & Pages → Create → connect this repo. No build command; deploy command
`npx wrangler deploy`. Add `TYPESAFE_API_KEY` as a secret in the Worker's settings.
`wrangler.jsonc` binds the custom domain `yesno.jakecuth.com`.

## Local

```bash
export TYPESAFE_API_KEY=...
python server.py        # http://localhost:8765
```
