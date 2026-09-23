# Yes or No

Ask [Jev](https://typesafe.ai) (TypeSafe's System-One model) a yes/no question. Jev
doesn't generate text — it returns P(yes) — so the app shows YES/NO, the probability,
and a confidence meter. That's it.

```bash
export TYPESAFE_API_KEY=...
python server.py        # http://localhost:8765
```

Stdlib only (Python 3.9+). `server.py` serves `index.html` and proxies `POST /ask`
to `POST https://api.typesafe.ai/v1/systemone` with a single `noul` question, so the
API key stays server-side.
