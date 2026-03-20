import { DurableObject } from "cloudflare:workers";

/**
 * Horizon Desk — Rate Limiter & Session Gateway
 *
 * Acts as a proxy between the Python CLI (main.py) and the AI worker.
 * Enforces:
 *   - Max 150 requests per minute (globally)
 *   - Max 4096 tokens per request (estimated)
 *   - Tracks live/active users
 */

// ─── Configuration ─────────────────────────────────────────────────────
const MAX_REQUESTS_PER_MINUTE = 150;
const MAX_TOKENS_PER_REQUEST = 4096;
const SESSION_TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes for "active" status
const CLEANUP_INTERVAL_MS = 2 * 60 * 1000; // purge entries older than 2 min

const CORS_HEADERS = {
	'Access-Control-Allow-Origin': '*',
	'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
	'Access-Control-Allow-Headers': 'Content-Type, X-User-Id, Authorization',
};

// ─── Durable Object: Rate Limiter & Session Manager ────────────────────
export class RateLimiterDO extends DurableObject {
	constructor(ctx, env) {
		super(ctx, env);
		this.ctx = ctx;
		this.env = env;
		this._initDb();
	}

	/** Initialize SQLite tables on first use */
	_initDb() {
		const sql = this.ctx.storage.sql;

		sql.exec(`
			CREATE TABLE IF NOT EXISTS requests (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				timestamp INTEGER NOT NULL,
				user_id TEXT DEFAULT 'anonymous'
			)
		`);

		sql.exec(`
			CREATE TABLE IF NOT EXISTS sessions (
				user_id TEXT PRIMARY KEY,
				last_seen INTEGER NOT NULL,
				request_count INTEGER DEFAULT 0
			)
		`);
	}

	/**
	 * Check if a new request is allowed under the rate limit.
	 * @returns {{ allowed: boolean, remaining: number, total: number, reset_at: number }}
	 */
	async checkRateLimit() {
		const now = Date.now();
		const windowStart = now - 60_000; // 1 minute window

		// Count requests in the last 60 seconds
		const result = this.ctx.storage.sql
			.exec("SELECT COUNT(*) as cnt FROM requests WHERE timestamp > ?", windowStart)
			.toArray();

		const count = result[0]?.cnt ?? 0;
		const remaining = Math.max(0, MAX_REQUESTS_PER_MINUTE - count);

		return {
			allowed: count < MAX_REQUESTS_PER_MINUTE,
			remaining,
			total: count,
			max: MAX_REQUESTS_PER_MINUTE,
			reset_at: windowStart + 60_000,
		};
	}

	/**
	 * Record a successful request.
	 * @param {string} userId
	 */
	async recordRequest(userId = 'anonymous') {
		const now = Date.now();

		this.ctx.storage.sql.exec(
			"INSERT INTO requests (timestamp, user_id) VALUES (?, ?)",
			now, userId
		);

		// Update session
		this.ctx.storage.sql.exec(`
			INSERT INTO sessions (user_id, last_seen, request_count)
			VALUES (?, ?, 1)
			ON CONFLICT(user_id) DO UPDATE SET
				last_seen = excluded.last_seen,
				request_count = request_count + 1
		`, userId, now);

		// Periodically cleanup old entries
		await this.cleanupOldEntries();
	}

	/**
	 * Get all users active within the last SESSION_TIMEOUT_MS.
	 * @returns {{ users: Array, count: number }}
	 */
	async getActiveUsers() {
		const cutoff = Date.now() - SESSION_TIMEOUT_MS;

		const rows = this.ctx.storage.sql
			.exec("SELECT user_id, last_seen, request_count FROM sessions WHERE last_seen > ? ORDER BY last_seen DESC", cutoff)
			.toArray();

		return {
			users: rows.map(r => ({
				user_id: r.user_id,
				last_seen: r.last_seen,
				request_count: r.request_count,
			})),
			count: rows.length,
		};
	}

	/**
	 * Purge request entries older than CLEANUP_INTERVAL_MS.
	 */
	async cleanupOldEntries() {
		const cutoff = Date.now() - CLEANUP_INTERVAL_MS;
		this.ctx.storage.sql.exec("DELETE FROM requests WHERE timestamp < ?", cutoff);

		// Also remove stale sessions (inactive > 30 minutes)
		const sessionCutoff = Date.now() - 30 * 60 * 1000;
		this.ctx.storage.sql.exec("DELETE FROM sessions WHERE last_seen < ?", sessionCutoff);
	}
}

// ─── Main Worker Fetch Handler ─────────────────────────────────────────
export default {
	async fetch(request, env, ctx) {
		// CORS preflight
		if (request.method === 'OPTIONS') {
			return new Response(null, { status: 204, headers: CORS_HEADERS });
		}

		const url = new URL(request.url);

		// ── Route: GET /api/status ──────────────────────────────────────
		if (url.pathname === '/api/status' && request.method === 'GET') {
			const stub = getRateLimiterStub(env);
			const [rateInfo, activeUsers] = await Promise.all([
				stub.checkRateLimit(),
				stub.getActiveUsers(),
			]);

			return jsonResponse({
				status: 'ok',
				rate_limit: rateInfo,
				active_users: activeUsers,
				config: {
					max_requests_per_minute: MAX_REQUESTS_PER_MINUTE,
					max_tokens_per_request: MAX_TOKENS_PER_REQUEST,
				}
			});
		}

		// ── Route: POST /api/chat ───────────────────────────────────────
		if (url.pathname === '/api/chat' && request.method === 'POST') {
			return handleChatRequest(request, env);
		}

		// ── Route: GET /health ──────────────────────────────────────────
		if (url.pathname === '/health') {
			return jsonResponse({ status: 'ok', worker: 'horizon-updater-gateway' });
		}

		// ── Fallback: Serve static assets or 404 ───────────────────────
		return jsonResponse({ error: 'Not found. Use POST /api/chat or GET /api/status' }, 404);
	}
};

// ─── Chat Request Handler ──────────────────────────────────────────────
async function handleChatRequest(request, env) {
	let body;
	try {
		body = await request.json();
	} catch {
		return jsonResponse({ error: 'Invalid JSON body.' }, 400);
	}

	// Validate messages
	if (!body.messages || !Array.isArray(body.messages) || body.messages.length === 0) {
		return jsonResponse({ error: 'Missing or invalid "messages" array.' }, 400);
	}

	// Extract user ID from header or body
	const userId = request.headers.get('X-User-Id') || body.user_id || 'anonymous';

	// ── Step 1: Check Rate Limit ────────────────────────────────────
	const stub = getRateLimiterStub(env);
	const rateInfo = await stub.checkRateLimit();

	if (!rateInfo.allowed) {
		return jsonResponse({
			error: 'Rate limit exceeded. Maximum 150 requests per minute.',
			rate_limit: rateInfo,
			retry_after_seconds: Math.ceil((rateInfo.reset_at - Date.now()) / 1000),
		}, 429);
	}

	// ── Step 2: Check Token Limit (user content only, not system prompt) ──
	const userMessages = body.messages.filter(m => m.role !== 'system');
	const userText = userMessages.map(m => typeof m.content === 'string' ? m.content : JSON.stringify(m.content)).join(' ');
	const estimatedUserTokens = Math.ceil(userText.length / 4);

	if (estimatedUserTokens > MAX_TOKENS_PER_REQUEST) {
		return jsonResponse({
			error: `User input too long. Estimated ${estimatedUserTokens} tokens exceeds ${MAX_TOKENS_PER_REQUEST} limit.`,
			estimated_tokens: estimatedUserTokens,
			max_tokens: MAX_TOKENS_PER_REQUEST,
		}, 413);
	}

	// ── Step 3: Proxy to AI Worker ──────────────────────────────────
	try {
		// Use service binding if available, otherwise use URL
		let aiResponse;

		if (env.AI_WORKER) {
			// Service binding (preferred — no network hop)
			aiResponse = await env.AI_WORKER.fetch(new Request('https://ai-worker/chat', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					messages: body.messages,
					model: body.model,
					max_tokens: body.max_tokens,
					temperature: body.temperature,
					top_p: body.top_p,
					stop: body.stop,
				}),
			}));
		} else if (env.AI_WORKER_URL) {
			// URL-based fallback
			aiResponse = await fetch(env.AI_WORKER_URL, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					messages: body.messages,
					model: body.model,
					max_tokens: body.max_tokens,
					temperature: body.temperature,
					top_p: body.top_p,
					stop: body.stop,
				}),
			});
		} else {
			return jsonResponse({
				error: 'AI worker not configured. Set AI_WORKER service binding or AI_WORKER_URL env var.',
			}, 503);
		}

		// ── Step 4: Record the request ──────────────────────────────
		await stub.recordRequest(userId);

		// ── Step 5: Return the AI response ──────────────────────────
		const aiData = await aiResponse.json();

		if (!aiResponse.ok) {
			return jsonResponse({
				error: 'AI worker returned an error.',
				details: aiData,
				rate_limit: { remaining: rateInfo.remaining - 1 },
			}, aiResponse.status);
		}

		return jsonResponse({
			...aiData,
			rate_limit: { remaining: rateInfo.remaining - 1, max: MAX_REQUESTS_PER_MINUTE },
			user_id: userId,
		});

	} catch (err) {
		return jsonResponse({
			error: 'Failed to reach AI worker.',
			details: err.message,
		}, 502);
	}
}

// ─── Helpers ───────────────────────────────────────────────────────────

/**
 * Get the singleton RateLimiterDO stub (one DO instance for all rate limiting).
 */
function getRateLimiterStub(env) {
	return env.RATE_LIMITER.getByName("global-rate-limiter");
}

/**
 * Returns a JSON response with CORS headers.
 */
function jsonResponse(data, status = 200) {
	return new Response(JSON.stringify(data), {
		status,
		headers: {
			'Content-Type': 'application/json',
			...CORS_HEADERS,
		},
	});
}
