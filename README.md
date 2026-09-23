# Yes or No

Ask [Jev](https://typesafe.ai) (TypeSafe's System-One model) a yes/no question. Jev
doesn't generate text — it returns P(yes) — so the app shows Yes/No and the probability.

Live: https://yesno.jakecuth.com

## Layout

- `index.html` — the whole UI, no build step.
- `functions/ask.js` — Cloudflare Pages Function for `POST /ask`; proxies to
  `POST https://api.typesafe.ai/v1/systemone` so the API key stays server-side.
- `server.py` — same thing for local dev, stdlib only.

## Deploy (Cloudflare Pages)

Connect this repo as a Pages project: no build command, output directory `/`.
Set `TYPESAFE_API_KEY` as a Production (and Preview) environment variable, then add
the custom domain `yesno.jakecuth.com`.

## Local

```bash
export TYPESAFE_API_KEY=...
python server.py        # http://localhost:8765
```
