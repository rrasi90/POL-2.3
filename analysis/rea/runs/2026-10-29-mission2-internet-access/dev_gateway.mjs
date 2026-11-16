// Single-origin local gateway for Cloudflare Quick Tunnel (Mission 2).
// Routes /api/*, /healthz, /readyz, /docs, /redoc, /openapi.json -> FastAPI (8001)
// everything else (incl. Next HMR websocket upgrades) -> Next.js (3000).
// Lives in the dated run directory; never committed.
import http from "node:http";
import net from "node:net";

const API = { host: "127.0.0.1", port: 8001 };
const WEB = { host: "127.0.0.1", port: 3000 };
const PORT = Number(process.env.POL_GATEWAY_PORT || 8080);

const API_EXACT = new Set(["/healthz", "/readyz", "/docs", "/redoc", "/openapi.json"]);
const API_PREFIX = "/api/";

function targetFor(url) {
  const path = (url || "/").split("?")[0];
  if (API_EXACT.has(path) || path.startsWith(API_PREFIX)) return API;
  return WEB;
}

function rawRequest(req) {
  const lines = [`${req.method} ${req.url} HTTP/1.1`];
  for (const [k, v] of Object.entries(req.headers)) {
    if (v === undefined) continue;
    lines.push(`${k}: ${Array.isArray(v) ? v.join(", ") : v}`);
  }
  return lines.join("\r\n") + "\r\n\r\n";
}

const server = http.createServer((req, res) => {
  const t = targetFor(req.url);
  const upstream = http.request(
    { host: t.host, port: t.port, path: req.url, method: req.method, headers: req.headers },
    (u) => {
      res.writeHead(u.statusCode || 502, u.headers);
      u.pipe(res);
    },
  );
  upstream.on("error", (e) => {
    if (!res.headersSent) res.writeHead(502, { "content-type": "text/plain" });
    res.end(`gateway error: ${e.message}`);
  });
  req.pipe(upstream);
});

server.on("upgrade", (req, clientSocket, head) => {
  const t = targetFor(req.url);
  const upstream = net.connect(t.port, t.host, () => {
    upstream.write(rawRequest(req));
    if (head.length) upstream.write(head);
    upstream.pipe(clientSocket);
    clientSocket.pipe(upstream);
  });
  upstream.on("error", () => clientSocket.destroy());
  clientSocket.on("error", () => upstream.destroy());
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`[gateway] 127.0.0.1:${PORT}  /api/*,healthz -> ${API.host}:${API.port}  rest -> ${WEB.host}:${WEB.port}`);
});
