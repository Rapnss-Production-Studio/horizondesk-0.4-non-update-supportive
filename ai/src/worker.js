/**
 * Horizon Desk — Cloudflare AI Worker
 * Accepts chat completion requests and runs inference via Workers AI.
 */

// CORS headers for cross-origin requests from the Python client
const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-User-Id, Authorization',
};

// Maximum tokens enforced per request
const MAX_OUTPUT_TOKENS = 8000;
const MAX_USER_INPUT_TOKENS = 8000;
const MAX_TOTAL_INPUT_TOKENS = 32768; // System prompt with 100+ tools is very large

// Default model for text inference
const DEFAULT_TEXT_MODEL = '@cf/meta/llama-3.1-8b-instruct';

// Fallback model chain
const MODEL_FALLBACKS = [
  '@cf/meta/llama-3.1-8b-instruct',
  '@cf/meta/llama-3-8b-instruct',
  '@cf/mistral/mistral-7b-instruct-v0.2',
];

// Vision model for image analysis
const VISION_MODEL = '@cf/meta/llama-3.2-11b-vision-instruct';

export default {
  async fetch(request, env) {
    const start = Date.now();
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'POST only' }), { status: 405, headers: CORS_HEADERS });
    }

    try {
      const body = await request.json();
      
      const aiPayload = {
        messages: body.messages,
        max_tokens: body.max_tokens || 2048,
        temperature: body.temperature ?? 0.7,
        top_p: body.top_p ?? 1,
        stop: body.stop
      };

const result = await env.AI.run(body.model || DEFAULT_TEXT_MODEL, aiPayload);
      const end = Date.now();
      
      const responseText = (typeof result === 'string') ? result : (result.response || result.result || JSON.stringify(result));
      
      return new Response(JSON.stringify({
        response: responseText,
        latency: `${end - start}ms`
      }), {
        headers: { 
          'Content-Type': 'application/json', 
          'X-Latency': `${end - start}ms`,
          ...CORS_HEADERS 
        }
      });

    } catch (err) {
      return new Response(JSON.stringify({ error: err.message }), { status: 400, headers: CORS_HEADERS });
    }
  }
};