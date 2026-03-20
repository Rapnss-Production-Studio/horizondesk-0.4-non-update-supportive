import { DurableObject } from "cloudflare:workers";

/**
 * Horizon Online - Multi-Agent Team Collaboration
 * 
 * Enables multiple OmniAgent instances to form teams,
 * distribute tasks, and sync results in real-time.
 */

// TeamRoom Durable Object - Manages a single team's state
export class TeamRoom extends DurableObject {
	constructor(ctx, env) {
		super(ctx, env);
		this.sessions = new Map(); // WebSocket sessions
	}

	// Initialize team with leader info
	async initTeam(leaderRole) {
		await this.ctx.storage.put("leader", {
			role: leaderRole,
			joinedAt: Date.now()
		});
		await this.ctx.storage.put("members", []);
		await this.ctx.storage.put("tasks", []);
		await this.ctx.storage.put("results", []);
		return { success: true };
	}

	// Add a member to the team
	async joinTeam(memberRole) {
		const members = await this.ctx.storage.get("members") || [];
		const memberId = `member_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;

		members.push({
			id: memberId,
			role: memberRole,
			joinedAt: Date.now(),
			status: "ready"
		});

		await this.ctx.storage.put("members", members);
		this.broadcast({ type: "member_joined", role: memberRole, id: memberId });

		return { success: true, memberId, members };
	}

	// Get team status
	async getStatus() {
		const leader = await this.ctx.storage.get("leader");
		const members = await this.ctx.storage.get("members") || [];
		const tasks = await this.ctx.storage.get("tasks") || [];
		const results = await this.ctx.storage.get("results") || [];

		return { leader, members, tasks, results };
	}

	// Leader assigns a task to a member
	async assignTask(memberId, taskDescription, taskType) {
		const tasks = await this.ctx.storage.get("tasks") || [];
		const taskId = `task_${Date.now()}`;

		const task = {
			id: taskId,
			assignedTo: memberId,
			description: taskDescription,
			type: taskType,
			status: "pending",
			createdAt: Date.now()
		};

		tasks.push(task);
		await this.ctx.storage.put("tasks", tasks);
		this.broadcast({ type: "task_assigned", task });

		return { success: true, taskId, task };
	}

	// Member submits task result
	async submitResult(memberId, taskId, resultData) {
		const tasks = await this.ctx.storage.get("tasks") || [];
		const results = await this.ctx.storage.get("results") || [];

		// Update task status
		const taskIndex = tasks.findIndex(t => t.id === taskId);
		if (taskIndex >= 0) {
			tasks[taskIndex].status = "completed";
			await this.ctx.storage.put("tasks", tasks);
		}

		// Store result
		const result = {
			taskId,
			memberId,
			data: resultData,
			submittedAt: Date.now()
		};
		results.push(result);
		await this.ctx.storage.put("results", results);

		this.broadcast({ type: "result_submitted", taskId, memberId });

		return { success: true, result };
	}

	// Get pending tasks for a member
	async getMyTasks(memberId) {
		const tasks = await this.ctx.storage.get("tasks") || [];
		return tasks.filter(t => t.assignedTo === memberId && t.status === "pending");
	}

	// Get all results (for leader to sync)
	async getAllResults() {
		return await this.ctx.storage.get("results") || [];
	}

	// ─── TEAM CHAT ───────────────────────────────────────────────
	async sendChatMessage(sender, role, text, attachmentUrl = null) {
		const messages = await this.ctx.storage.get("messages") || [];
		const msg = {
			id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
			sender,
			role,
			text,
			attachmentUrl,
			timestamp: Date.now()
		};
		messages.push(msg);
		// Keep only last 500 messages
		if (messages.length > 500) messages.splice(0, messages.length - 500);
		await this.ctx.storage.put("messages", messages);
		// Broadcast to all clients connected via WebSocket
		this.broadcast({ type: "new_message", message: msg });
		return { success: true, message: msg };
	}

	async getChatMessages(limit = 50) {
		const messages = await this.ctx.storage.get("messages") || [];
		return messages.slice(-limit);
	}

	// WebSocket handling for real-time updates
	async fetch(request) {
		if (request.headers.get("Upgrade") === "websocket") {
			const pair = new WebSocketPair();
			const [client, server] = Object.values(pair);

			this.ctx.acceptWebSocket(server);
			this.sessions.set(server, { connectedAt: Date.now() });

			return new Response(null, { status: 101, webSocket: client });
		}

		return new Response("Expected WebSocket", { status: 400 });
	}

	webSocketMessage(ws, message) {
		// Handle incoming WebSocket messages
		try {
			const data = JSON.parse(message);
			// Echo or process
			ws.send(JSON.stringify({ type: "ack", data }));
		} catch (e) {
			ws.send(JSON.stringify({ type: "error", message: e.message }));
		}
	}

	webSocketClose(ws) {
		this.sessions.delete(ws);
	}

	// Broadcast message to all connected clients
	broadcast(message) {
		const msg = JSON.stringify(message);
		for (const [ws] of this.sessions) {
			try {
				ws.send(msg);
			} catch (e) {
				this.sessions.delete(ws);
			}
		}
	}
}

// Generate 6-digit team code
function generateTeamCode() {
	return Math.floor(100000 + Math.random() * 900000).toString();
}

// Main Worker - REST API
export default {
	async fetch(request, env, ctx) {
		const url = new URL(request.url);
		const path = url.pathname;

		// CORS headers for local testing
		const corsHeaders = {
			"Access-Control-Allow-Origin": "*",
			"Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
			"Access-Control-Allow-Headers": "Content-Type",
			"Content-Type": "application/json"
		};

		if (request.method === "OPTIONS") {
			return new Response(null, { headers: corsHeaders });
		}

		try {
			// POST /api/team/create - Create a new team
			if (path === "/api/team/create" && request.method === "POST") {
				const { role } = await request.json();
				const teamCode = generateTeamCode();
				const roomId = `team_${teamCode}`;

				// Get or create the Durable Object for this team
				const stub = env.TEAM_ROOM.get(env.TEAM_ROOM.idFromName(roomId));
				await stub.initTeam(role);

				// Store team code mapping (in-memory for local dev)
				// In production, you'd use KV: await env.TEAM_CODES.put(teamCode, roomId);

				return new Response(JSON.stringify({
					success: true,
					teamCode,
					message: `Team created! Share this code: ${teamCode}`
				}), { headers: corsHeaders });
			}

			// POST /api/team/join - Join a team with code
			if (path === "/api/team/join" && request.method === "POST") {
				const { code, role } = await request.json();
				const roomId = `team_${code}`;

				const stub = env.TEAM_ROOM.get(env.TEAM_ROOM.idFromName(roomId));
				const result = await stub.joinTeam(role);

				return new Response(JSON.stringify({
					success: true,
					memberId: result.memberId,
					teamCode: code,
					message: `Joined team ${code} as ${role}`
				}), { headers: corsHeaders });
			}

			// GET /api/team/:code/status - Get team status
			if (path.startsWith("/api/team/") && path.endsWith("/status")) {
				const code = path.split("/")[3];
				const roomId = `team_${code}`;

				const stub = env.TEAM_ROOM.get(env.TEAM_ROOM.idFromName(roomId));
				const status = await stub.getStatus();

				return new Response(JSON.stringify(status), { headers: corsHeaders });
			}

			// GET /api/team/:code/messages - Get team chat messages
			if (path.match(/^\/api\/team\/\d+\/messages$/) && request.method === "GET") {
				const code = path.split("/")[3];
				const limit = parseInt(url.searchParams.get("limit") || "50");
				const stub = env.TEAM_ROOM.get(env.TEAM_ROOM.idFromName(`team_${code}`));
				const messages = await stub.getChatMessages(limit);
				return new Response(JSON.stringify({ messages }), { headers: corsHeaders });
			}

			// POST /api/team/:code/messages - Send a team chat message
			if (path.match(/^\/api\/team\/\d+\/messages$/) && request.method === "POST") {
				const code = path.split("/")[3];
				const { sender, role, text, attachmentUrl } = await request.json();
				if (!sender || !text) {
					return new Response(JSON.stringify({ error: "sender and text are required" }), { status: 400, headers: corsHeaders });
				}
				const stub = env.TEAM_ROOM.get(env.TEAM_ROOM.idFromName(`team_${code}`));
				const result = await stub.sendChatMessage(sender, role || "Member", text, attachmentUrl || null);
				return new Response(JSON.stringify(result), { headers: corsHeaders });
			}

			// GET /api/team/:code/members - Get team members
			if (path.startsWith("/api/team/") && path.endsWith("/members")) {
				const code = path.split("/")[3];
				const roomId = `team_${code}`;

				const stub = env.TEAM_ROOM.get(env.TEAM_ROOM.idFromName(roomId));
				const status = await stub.getStatus();
				const members = status.members || [];

				return new Response(JSON.stringify({ members }), { headers: corsHeaders });
			}

			// GET /api/team/:code/tasks/:memberId - Get tasks for specific member
			if (path.match(/^\/api\/team\/\d+\/tasks\/[^\/]+$/)) {
				const parts = path.split("/");
				const code = parts[3];
				const memberId = parts[5];
				const roomId = `team_${code}`;

				const stub = env.TEAM_ROOM.get(env.TEAM_ROOM.idFromName(roomId));
				const tasks = await stub.getMyTasks(memberId);

				return new Response(JSON.stringify({ tasks }), { headers: corsHeaders });
			}

			// POST /api/team/:code/tasks - Leader assigns a task (called by Teams.jsx)
			if (path.match(/^\/api\/team\/\w+\/tasks$/) && request.method === "POST") {
				const code = path.split("/")[3];
				const { memberId, description, type } = await request.json();
				if (!memberId || !description) {
					return new Response(JSON.stringify({ error: "memberId and description are required" }), { status: 400, headers: corsHeaders });
				}
				const stub = env.TEAM_ROOM.get(env.TEAM_ROOM.idFromName(`team_${code}`));
				const result = await stub.assignTask(memberId, description, type || "general");
				return new Response(JSON.stringify(result), { headers: corsHeaders });
			}

			// GET /api/team/:code/results - Leader syncs all submitted results
			if (path.match(/^\/api\/team\/\w+\/results$/) && request.method === "GET") {
				const code = path.split("/")[3];
				const stub = env.TEAM_ROOM.get(env.TEAM_ROOM.idFromName(`team_${code}`));
				const results = await stub.getAllResults();
				return new Response(JSON.stringify({ results }), { headers: corsHeaders });
			}

			// POST /api/team/:code/results - Member submits work result (called by Teams.jsx)
			if (path.match(/^\/api\/team\/\w+\/results$/) && request.method === "POST") {
				const code = path.split("/")[3];
				const { taskId, memberId, filename, content } = await request.json();
				if (!taskId || !memberId) {
					return new Response(JSON.stringify({ error: "taskId and memberId are required" }), { status: 400, headers: corsHeaders });
				}
				const stub = env.TEAM_ROOM.get(env.TEAM_ROOM.idFromName(`team_${code}`));
				const result = await stub.submitResult(memberId, taskId, { filename: filename || `output_${taskId}.txt`, content });
				return new Response(JSON.stringify({ success: true, result }), { headers: corsHeaders });
			}

			// POST /api/task/assign - Leader assigns task (legacy route kept for CLI compat)
			if (path === "/api/task/assign" && request.method === "POST") {
				const { teamCode, memberId, description, type } = await request.json();
				const roomId = `team_${teamCode}`;

				const stub = env.TEAM_ROOM.get(env.TEAM_ROOM.idFromName(roomId));
				const result = await stub.assignTask(memberId, description, type);

				return new Response(JSON.stringify(result), { headers: corsHeaders });
			}

			// POST /api/task/complete - Member submits result
			if (path === "/api/task/complete" && request.method === "POST") {
				const { teamCode, memberId, taskId, resultData } = await request.json();
				const roomId = `team_${teamCode}`;

				const stub = env.TEAM_ROOM.get(env.TEAM_ROOM.idFromName(roomId));
				const result = await stub.submitResult(memberId, taskId, resultData);

				return new Response(JSON.stringify(result), { headers: corsHeaders });
			}

			// GET /api/task/:code/:memberId - Get tasks for member
			if (path.startsWith("/api/task/") && path.split("/").length === 5) {
				const parts = path.split("/");
				const code = parts[3];
				const memberId = parts[4];
				const roomId = `team_${code}`;

				const stub = env.TEAM_ROOM.get(env.TEAM_ROOM.idFromName(roomId));
				const tasks = await stub.getMyTasks(memberId);

				return new Response(JSON.stringify({ tasks }), { headers: corsHeaders });
			}

			// GET /api/results/:code - Get all results (for sync)
			if (path.startsWith("/api/results/")) {
				const code = path.split("/")[3];
				const roomId = `team_${code}`;

				const stub = env.TEAM_ROOM.get(env.TEAM_ROOM.idFromName(roomId));
				const results = await stub.getAllResults();

				return new Response(JSON.stringify({ results }), { headers: corsHeaders });
			}

			// WebSocket upgrade for real-time
			if (path.startsWith("/ws/")) {
				const code = path.split("/")[2];
				const roomId = `team_${code}`;

				const stub = env.TEAM_ROOM.get(env.TEAM_ROOM.idFromName(roomId));
				return stub.fetch(request);
			}

			// Health check
			if (path === "/api/health") {
				return new Response(JSON.stringify({
					status: "ok",
					service: "Horizon Online",
					version: "1.0.0"
				}), { headers: corsHeaders });
			}

			// POST /api/auth/signup - Create new user
			if (path === "/api/auth/signup" && request.method === "POST") {
				const { email, password, username } = await request.json();

				// Check if user exists
				const existing = await env.DB.prepare("SELECT * FROM users WHERE email = ?").bind(email).first();
				if (existing) {
					return new Response(JSON.stringify({ error: "User already exists" }), { status: 400, headers: corsHeaders });
				}

				// Generate verification code
				const code = Math.floor(100000 + Math.random() * 900000).toString();

				// Create user (unverified)
				// In real app, hash password!
				const userId = crypto.randomUUID();
				await env.DB.prepare("INSERT INTO users (id, email, password, username, verify_code, verified) VALUES (?, ?, ?, ?, ?, 0)")
					.bind(userId, email, password, username, code)
					.run();

				// Send email
				await sendEmail(email, "Verify your Horizon Desk account", `Your code is: ${code}`, env);

				return new Response(JSON.stringify({ success: true, message: "Verification code sent" }), { headers: corsHeaders });
			}

			// POST /api/auth/verify - Verify email
			if (path === "/api/auth/verify" && request.method === "POST") {
				const { email, code } = await request.json();

				const user = await env.DB.prepare("SELECT * FROM users WHERE email = ?").bind(email).first();
				if (!user) return new Response(JSON.stringify({ error: "User not found" }), { status: 404, headers: corsHeaders });

				if (user.verify_code !== code) {
					return new Response(JSON.stringify({ error: "Invalid code" }), { status: 400, headers: corsHeaders });
				}

				await env.DB.prepare("UPDATE users SET verified = 1, verify_code = NULL WHERE email = ?").bind(email).run();
				return new Response(JSON.stringify({ success: true, message: "Account verified" }), { headers: corsHeaders });
			}

			// POST /api/auth/login
			if (path === "/api/auth/login" && request.method === "POST") {
				const { email, password } = await request.json();

				const user = await env.DB.prepare("SELECT * FROM users WHERE email = ?").bind(email).first();
				if (!user || user.password !== password) {
					return new Response(JSON.stringify({ error: "Invalid credentials" }), { status: 401, headers: corsHeaders });
				}

				if (!user.verified) {
					return new Response(JSON.stringify({ error: "Email not verified" }), { status: 403, headers: corsHeaders });
				}

				return new Response(JSON.stringify({
					success: true,
					user: { id: user.id, email: user.email, username: user.username }
				}), { headers: corsHeaders });
			}

			// POST /api/auth/forgot-password
			if (path === "/api/auth/forgot-password" && request.method === "POST") {
				const { email } = await request.json();

				const user = await env.DB.prepare("SELECT * FROM users WHERE email = ?").bind(email).first();
				if (!user) {
					// We return success even if user doesn't exist to prevent email enumeration,
					// but for this MVP, returning an error is fine to help the user debug.
					return new Response(JSON.stringify({ error: "User not found" }), { status: 404, headers: corsHeaders });
				}

				// Generate reset code
				const code = Math.floor(100000 + Math.random() * 900000).toString();

				// Save code to DB
				await env.DB.prepare("UPDATE users SET verify_code = ? WHERE email = ?").bind(code, email).run();

				// Send email
				await sendEmail(email, "Horizon Desk Password Reset", `Your password reset code is: ${code}`, env);

				return new Response(JSON.stringify({ success: true, message: "Reset code sent to email" }), { headers: corsHeaders });
			}

			// POST /api/auth/reset-password
			if (path === "/api/auth/reset-password" && request.method === "POST") {
				const { email, code, newPassword } = await request.json();

				const user = await env.DB.prepare("SELECT * FROM users WHERE email = ?").bind(email).first();
				if (!user) return new Response(JSON.stringify({ error: "User not found" }), { status: 404, headers: corsHeaders });

				if (user.verify_code !== code) {
					return new Response(JSON.stringify({ error: "Invalid reset code" }), { status: 400, headers: corsHeaders });
				}

				// Update password and clear code
				await env.DB.prepare("UPDATE users SET password = ?, verify_code = NULL WHERE email = ?").bind(newPassword, email).run();

				return new Response(JSON.stringify({ success: true, message: "Password updated successfully" }), { headers: corsHeaders });
			}

			// Temporary Debug Route for Schema
			if (path === "/api/debug/schema" && request.method === "GET") {
				const info = await env.DB.prepare("PRAGMA table_info(users)").all();
				return new Response(JSON.stringify(info), { headers: corsHeaders });
			}

			// POST /api/auth/oauth-sync (Used by Desktop App to upsert a Rapnss OAuth profile into D1)
			if (path === "/api/auth/oauth-sync" && request.method === "POST") {
				const userData = await request.json();
				// Derive safe values from what Rapnss actually returns:
				// { id, handle, name, email }
				const rapnssId = String(userData.id || userData.rapnssId || '');
				const email = userData.email || `${rapnssId}@rapnss.oauth`;
				const username = userData.name || userData.handle || email.split('@')[0];
				const fullName = userData.name || username;
				const handle = userData.handle || username;
				
				// Look up by rapnss_id first (most reliable)
				let user = rapnssId ? await env.DB.prepare("SELECT * FROM users WHERE rapnss_id = ?").bind(rapnssId).first() : null;
				
				// Fall back to email if rapnss_id not found (links existing old accounts to Rapnss)
				if (!user && email) {
					user = await env.DB.prepare("SELECT * FROM users WHERE email = ?").bind(email).first();
				}

				if (!user) {
					const userId = crypto.randomUUID();
					await env.DB.prepare(
						"INSERT INTO users (id, rapnss_id, email, username, handle, full_name, provider, verified) VALUES (?, ?, ?, ?, ?, ?, 'rapnss', 1)"
					).bind(userId, rapnssId || null, email, username, handle, fullName).run();
					user = { id: userId, rapnss_id: rapnssId, email, username };
				} else {
					// Update profile info on every login
					await env.DB.prepare(
						"UPDATE users SET username = ?, handle = ?, full_name = ?, rapnss_id = ? WHERE id = ?"
					).bind(username, handle, fullName, rapnssId || user.rapnss_id, user.id).run();
					user = { ...user, username };
				}

				return new Response(JSON.stringify({
					success: true,
					user: { id: user.id, rapnss_id: user.rapnss_id, email: user.email, username: user.username }
				}), { headers: corsHeaders });
			}

			// POST /api/auth/oauth-exchange
			if (path === "/api/auth/oauth-exchange" && request.method === "POST") {
				const { code, redirectUri } = await request.json();

				// 1. Exchange code for token
				const tokenResponse = await fetch("https://rapnss.in/api/oauth/token", {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({
						grant_type: "authorization_code",
						client_id: env.RAPNSS_CLIENT_ID,
						client_secret: env.RAPNSS_CLIENT_SECRET,
						code: code,
						redirect_uri: redirectUri
					})
				});

				const tokenData = await tokenResponse.json();
				if (!tokenResponse.ok) {
					return new Response(JSON.stringify({ error: "Failed token exchange", details: tokenData }), { status: 400, headers: corsHeaders });
				}

				// 2. Fetch User Info from Rapnss
				const userResponse = await fetch("https://rapnss.in/api/oauth/userinfo", {
					headers: { "Authorization": `Bearer ${tokenData.access_token}` }
				});
				const userData = await userResponse.json();
				if (!userResponse.ok) {
					return new Response(JSON.stringify({ error: "Failed getting user profile", details: userData }), { status: 400, headers: corsHeaders });
				}

				// 3. Map Rapnss fields: { id, handle, name, email }
				const rapnssId = String(userData.id || '');
				const email = userData.email || `${rapnssId}@rapnss.oauth`;
				const username = userData.name || userData.handle || email.split('@')[0];
				const fullName = userData.name || username;
				const handle = userData.handle || username;

				// Look up by rapnss_id first (most reliable)
				let user = rapnssId ? await env.DB.prepare("SELECT * FROM users WHERE rapnss_id = ?").bind(rapnssId).first() : null;

				// Fall back to email to link existing accounts
				if (!user && email) {
					user = await env.DB.prepare("SELECT * FROM users WHERE email = ?").bind(email).first();
				}

				if (!user) {
					const userId = crypto.randomUUID();
					await env.DB.prepare(
						"INSERT INTO users (id, rapnss_id, email, username, handle, full_name, provider, verified) VALUES (?, ?, ?, ?, ?, ?, 'rapnss', 1)"
					).bind(userId, rapnssId || null, email, username, handle, fullName).run();
					user = { id: userId, rapnss_id: rapnssId, email, username };
				} else {
					// Refresh profile on every login
					await env.DB.prepare(
						"UPDATE users SET username = ?, handle = ?, full_name = ?, rapnss_id = ? WHERE id = ?"
					).bind(username, handle, fullName, rapnssId || user.rapnss_id, user.id).run();
					user = { ...user, username };
				}

				return new Response(JSON.stringify({
					success: true,
					user: { id: user.id, rapnss_id: user.rapnss_id, email: user.email, username: user.username },
					rapnssToken: tokenData.access_token
				}), { headers: corsHeaders });
			}

			// POST /api/classify - ResNet-50 Image Classification
			if (path === "/api/classify" && request.method === "POST") {
				try {
					const { image } = await request.json(); // Expecting array of integers (e.g. from generic-form-data or similar) or base64?
					// Workers AI expects input depends on model. For resnet-50 it usually takes { image: number[] } or similar.
					// Actually, @cf/microsoft/resnet-50 takes { image: number[] } (pixel values) or input directly.
					// Let's assume the client sends the raw bytes as an array.

					const response = await env.AI.run('@cf/microsoft/resnet-50', {
						image: image
					});

					return new Response(JSON.stringify(response), { headers: corsHeaders });
				} catch (e) {
					return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: corsHeaders });
				}
			}

			// POST /api/dev/register - Register a user as a developer
			if (path === "/api/dev/register" && request.method === "POST") {
				const { userId } = await request.json();

				const existing = await env.DB.prepare("SELECT * FROM developers WHERE user_id = ?").bind(userId).first();
				if (existing) {
					return new Response(JSON.stringify({ success: true, developer: existing }), { headers: corsHeaders });
				}

				const devId = crypto.randomUUID();
				await env.DB.prepare(
					"INSERT INTO developers (id, user_id, agreed_to_terms, free_releases_left, ad_balance) VALUES (?, ?, 1, 1, 10.00)"
				).bind(devId, userId).run();

				const newDev = await env.DB.prepare("SELECT * FROM developers WHERE id = ?").bind(devId).first();
				return new Response(JSON.stringify({ success: true, developer: newDev, message: "Welcome to the Developer Program! You received 1 free release and $10 in Ad Credits." }), { headers: corsHeaders });
			}

			// GET /api/dev/dashboard - Get developer details and their plugins
			if (path === "/api/dev/dashboard" && request.method === "GET") {
				const userId = url.searchParams.get("userId");
				if (!userId) return new Response(JSON.stringify({ error: "Missing userId" }), { status: 400, headers: corsHeaders });

				const dev = await env.DB.prepare("SELECT * FROM developers WHERE user_id = ?").bind(userId).first();
				if (!dev) return new Response(JSON.stringify({ error: "Developer not found" }), { status: 404, headers: corsHeaders });

				const { results: plugins } = await env.DB.prepare("SELECT * FROM plugins WHERE developer_id = ? ORDER BY created_at DESC").bind(dev.id).all();

				return new Response(JSON.stringify({ success: true, developer: dev, plugins }), { headers: corsHeaders });
			}

			// POST /api/dev/plugins - Upload/Publish a new plugin
			if (path === "/api/dev/plugins" && request.method === "POST") {
				const { developerId, name, description, version, tigrisUrl, iconUrl, category } = await request.json();

				const dev = await env.DB.prepare("SELECT * FROM developers WHERE id = ?").bind(developerId).first();
				if (!dev) return new Response(JSON.stringify({ error: "Developer not found" }), { status: 404, headers: corsHeaders });

				// Check if they have free releases or balance
				if (dev.free_releases_left <= 0 && dev.ad_balance < 2.00) {
					return new Response(JSON.stringify({ error: "Insufficient balance to publish. Costs $2.00." }), { status: 402, headers: corsHeaders });
				}

				// Deduct balance or free release
				if (dev.free_releases_left > 0) {
					await env.DB.prepare("UPDATE developers SET free_releases_left = free_releases_left - 1 WHERE id = ?").bind(developerId).run();
				} else {
					await env.DB.prepare("UPDATE developers SET ad_balance = ad_balance - 2.00 WHERE id = ?").bind(developerId).run();
				}

				const pluginId = `p_${Date.now()}_${crypto.randomUUID().substr(0, 4)}`;
				await env.DB.prepare(
					"INSERT INTO plugins (id, developer_id, name, description, version, tigris_url, icon_url, category, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'published')"
				).bind(pluginId, developerId, name, description, version, tigrisUrl, iconUrl || null, category || 'general').run();

				return new Response(JSON.stringify({ success: true, message: "Plugin published successfully!", pluginId }), { headers: corsHeaders });
			}

			// GET /api/dev/plugins/:id - Get single plugin details
			if (path.match(/^\/api\/dev\/plugins\/[^\/]+$/) && request.method === "GET") {
				const pluginId = path.split("/").pop();
				const plugin = await env.DB.prepare("SELECT * FROM plugins WHERE id = ?").bind(pluginId).first();
				if (!plugin) return new Response(JSON.stringify({ error: "Plugin not found" }), { status: 404, headers: corsHeaders });
				return new Response(JSON.stringify({ success: true, plugin }), { headers: corsHeaders });
			}

			// PUT /api/dev/plugins/:id - Update a plugin
			if (path.match(/^\/api\/dev\/plugins\/[^\/]+$/) && request.method === "PUT") {
				const pluginId = path.split("/").pop();
				const { name, description, version, iconUrl, category } = await request.json();

				const plugin = await env.DB.prepare("SELECT * FROM plugins WHERE id = ?").bind(pluginId).first();
				if (!plugin) return new Response(JSON.stringify({ error: "Plugin not found" }), { status: 404, headers: corsHeaders });

				await env.DB.prepare(
					"UPDATE plugins SET name = ?, description = ?, version = ?, icon_url = ?, category = ? WHERE id = ?"
				).bind(
					name || plugin.name,
					description || plugin.description,
					version || plugin.version,
					iconUrl !== undefined ? iconUrl : plugin.icon_url,
					category || plugin.category,
					pluginId
				).run();

				const updated = await env.DB.prepare("SELECT * FROM plugins WHERE id = ?").bind(pluginId).first();
				return new Response(JSON.stringify({ success: true, plugin: updated }), { headers: corsHeaders });
			}

			// DELETE /api/dev/plugins/:id - Delete a plugin
			if (path.match(/^\/api\/dev\/plugins\/[^\/]+$/) && request.method === "DELETE") {
				const pluginId = path.split("/").pop();
				const plugin = await env.DB.prepare("SELECT * FROM plugins WHERE id = ?").bind(pluginId).first();
				if (!plugin) return new Response(JSON.stringify({ error: "Plugin not found" }), { status: 404, headers: corsHeaders });

				await env.DB.prepare("DELETE FROM plugins WHERE id = ?").bind(pluginId).run();
				return new Response(JSON.stringify({ success: true, message: "Plugin deleted" }), { headers: corsHeaders });
			}

			// POST /api/dev/auth/token - CLI auth: exchange OAuth code for developer token
			if (path === "/api/dev/auth/token" && request.method === "POST") {
				const { code, redirectUri } = await request.json();

				// 1. Exchange code for Rapnss token
				const tokenResponse = await fetch("https://rapnss.in/api/oauth/token", {
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({
						grant_type: "authorization_code",
						client_id: "client_19149213c616458a813269c2b232bd7e",
						client_secret: "sec_7bd0f2dd5ac0450696871740bafcd91f",
						code,
						redirect_uri: redirectUri
					})
				});

				const tokenData = await tokenResponse.json();
				if (!tokenResponse.ok) {
					return new Response(JSON.stringify({ error: "Token exchange failed", details: tokenData }), { status: 400, headers: corsHeaders });
				}

				// 2. Get user info
				const userResponse = await fetch("https://rapnss.in/api/oauth/userinfo", {
					headers: { "Authorization": `Bearer ${tokenData.access_token}` }
				});
				const userData = await userResponse.json();
				if (!userResponse.ok) {
					return new Response(JSON.stringify({ error: "Failed getting user profile", details: userData }), { status: 400, headers: corsHeaders });
				}

				// 3. Upsert user
				const rapnssId = String(userData.id || '');
				const email = userData.email || `${rapnssId}@rapnss.oauth`;
				const username = userData.name || userData.handle || email.split('@')[0];
				const fullName = userData.name || username;
				const handle = userData.handle || username;

				let user = rapnssId ? await env.DB.prepare("SELECT * FROM users WHERE rapnss_id = ?").bind(rapnssId).first() : null;
				if (!user && email) {
					user = await env.DB.prepare("SELECT * FROM users WHERE email = ?").bind(email).first();
				}

				if (!user) {
					const userId = crypto.randomUUID();
					await env.DB.prepare(
						"INSERT INTO users (id, rapnss_id, email, username, handle, full_name, provider, verified) VALUES (?, ?, ?, ?, ?, ?, 'rapnss', 1)"
					).bind(userId, rapnssId || null, email, username, handle, fullName).run();
					user = { id: userId, rapnss_id: rapnssId, email, username };
				}

				// 4. Get or create developer account
				let dev = await env.DB.prepare("SELECT * FROM developers WHERE user_id = ?").bind(user.id).first();
				if (!dev) {
					const devId = crypto.randomUUID();
					await env.DB.prepare(
						"INSERT INTO developers (id, user_id, agreed_to_terms, free_releases_left, ad_balance) VALUES (?, ?, 1, 1, 10.00)"
					).bind(devId, user.id).run();
					dev = await env.DB.prepare("SELECT * FROM developers WHERE id = ?").bind(devId).first();
				}

				return new Response(JSON.stringify({
					success: true,
					user: { id: user.id, email: user.email, username: user.username },
					developer: { id: dev.id, free_releases_left: dev.free_releases_left, ad_balance: dev.ad_balance },
					token: tokenData.access_token
				}), { headers: corsHeaders });
			}

			// GET /api/plugins - Plugin Store Catalog
			if (path === "/api/plugins" && request.method === "GET") {
				const query = `
					SELECT p.id, p.name, p.description, p.version, p.status, p.tigris_url, p.icon_url, p.category, u.username as author 
					FROM plugins p 
					JOIN developers d ON p.developer_id = d.id 
					JOIN users u ON d.user_id = u.id 
					WHERE p.status = 'published'
					ORDER BY p.created_at DESC
				`;
				const { results: dbPlugins } = await env.DB.prepare(query).all();

				let finalPlugins = dbPlugins;
				if (dbPlugins.length === 0) {
					finalPlugins = [
						{ id: "p_1", name: "Spotify Controller", description: "Allows the agent to control your Spotify desktop app (Play, Pause, Skip).", author: "Rapnss Production Studio", version: "1.0", status: "installed", category: "media", icon_url: null, tigris_url: null },
						{ id: "p_built_in_2", name: "GitHub Manager", description: "Create repos, commit, and push code directly from the chat.", author: "Rapnss Production Studio", version: "1.1", status: "available", category: "developer", icon_url: null, tigris_url: null }
					];
				}

				return new Response(JSON.stringify({ plugins: finalPlugins }, null, 2), {
					status: 200,
					headers: { ...corsHeaders, "Content-Type": "application/json" }
				});
			}

			// Serve static files (index.html)
			return new Response("Horizon Online API - Use /api/* endpoints", {
				status: 200,
				headers: corsHeaders
			});

		} catch (error) {
			console.error("API Error:", error);
			console.error("Stack:", error.stack);
			return new Response(JSON.stringify({
				error: error.message
			}), {
				status: 500,
				headers: corsHeaders
			});
		}
	}
};

// --- Auth Helper Functions ---
import nodemailer from 'nodemailer';

async function sendEmail(email, subject, body, env) {
	console.log(`[EMAIL] Preparing to send to ${email}`);
	try {
		const transporter = nodemailer.createTransport({
			host: "smtp.zoho.in",
			port: 465,
			secure: true, // true for 465, false for other ports
			auth: {
				user: "admin@rapnss.in",
				pass: "Rapnss@147258369"
			}
		});

		const info = await transporter.sendMail({
			from: '"Horizon Desk" <admin@rapnss.in>',
			to: email,
			subject: subject,
			text: body,
			html: body.replace(/\n/g, "<br>")
		});

		console.log(`[EMAIL] Sent: ${info.messageId}`);
		return true;
	} catch (error) {
		console.error(`[EMAIL ERROR] Failed to send email: ${error.message}`);
		// Fallback or rethrow? For now, we log but don't crash the signup flow if email fails (or we should?)
		// Let's rethrow to alert the user in the UI
		throw error;
	}
}

// --- Auth Endpoints (To be merged into fetch handler above) ---
// I need to inject these into the `fetch` function logic. 
// Instead of replacing the whole file which is risky with "replace_file_content" on a large file, 
// I will insert them before the "return new Response" at the end of the try block.

