#!/usr/bin/env node
/** One-time read-only Search Console OAuth helper. Do not run until requested. */
import fs from "fs";
import http from "http";
import path from "path";
import { spawn } from "child_process";

const envFile = path.join(process.cwd(), ".env.local");
if (fs.existsSync(envFile)) {
  for (const line of fs.readFileSync(envFile, "utf8").split(/\r?\n/)) {
    const match = line.match(/^([A-Z0-9_]+)=(.*)$/);
    if (!match || process.env[match[1]] !== undefined) continue;
    process.env[match[1]] = match[2].trim().replace(/^(["'])(.*)\1$/, "$2");
  }
}

const clientId = process.env.GSC_CLIENT_ID;
const clientSecret = process.env.GSC_CLIENT_SECRET;
const redirect = "http://localhost:5312";
const scope = "https://www.googleapis.com/auth/webmasters.readonly";

if (!clientId || !clientSecret) {
  console.error("Set GSC_CLIENT_ID and GSC_CLIENT_SECRET in .env.local first.");
  process.exit(1);
}

const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?${new URLSearchParams({
  client_id: clientId,
  redirect_uri: redirect,
  response_type: "code",
  scope,
  access_type: "offline",
  prompt: "consent",
})}`;

const server = http.createServer(async (request, response) => {
  const code = new URL(request.url, redirect).searchParams.get("code");
  if (!code) {
    response.writeHead(400).end("No OAuth code in callback.");
    return;
  }

  const tokenResponse = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      code,
      client_id: clientId,
      client_secret: clientSecret,
      redirect_uri: redirect,
      grant_type: "authorization_code",
    }),
  });
  const payload = await tokenResponse.json();
  if (!tokenResponse.ok || !payload.refresh_token) {
    response.writeHead(500).end("Token exchange failed. Check the terminal.");
    console.error(JSON.stringify(payload, null, 2));
    server.close();
    return;
  }

  response.writeHead(200, { "Content-Type": "text/plain" }).end("Done. Close this tab and return to the terminal.");
  console.log("\nAdd this value to .env.local as GSC_REFRESH_TOKEN:\n");
  console.log(payload.refresh_token);
  server.close();
});

server.listen(5312, () => {
  console.log("Opening Google consent for the read-only Search Console scope.");
  console.log(`If the browser does not open, paste this URL:\n${authUrl}\n`);
  spawn("open", [authUrl], { stdio: "ignore", detached: true }).unref();
});
