import { ask } from './ask.js';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/ask') {
      if (request.method !== 'POST') {
        return new Response(JSON.stringify({ error: 'method not allowed' }), {
          status: 405,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return ask(request, env);
    }
    return env.ASSETS.fetch(request);
  },
};
