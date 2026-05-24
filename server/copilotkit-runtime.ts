import http from "node:http";
import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNodeHttpEndpoint,
} from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";

const AGENT_URL = process.env.AGENT_URL || "http://localhost:8001";
const PORT = parseInt(process.env.RUNTIME_PORT || "4001", 10);

const agent = new HttpAgent({ url: `${AGENT_URL}/api/agent` });

const runtime = new CopilotRuntime({
  agents: {
    rashid_orchestrator: agent,
  },
});

const handler = copilotRuntimeNodeHttpEndpoint({
  endpoint: "/api/copilotkit",
  serviceAdapter: new ExperimentalEmptyAdapter(),
  runtime,
});

const server = http.createServer((req, res) => {
  if (req.url?.startsWith("/api/copilotkit")) {
    // Handle threads GET request (Intelligence mode not configured — return empty)
    if (req.method === "GET" && req.url.includes("/threads")) {
      res.writeHead(200, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
      res.end(JSON.stringify({ threads: [] }));
      return;
    }
    // Handle CORS preflight
    if (req.method === "OPTIONS") {
      res.writeHead(204, {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-Session-Id, Authorization",
      });
      res.end();
      return;
    }
    return handler(req, res);
  }
  res.writeHead(404);
  res.end("Not Found");
});

server.listen(PORT, () => {
  console.log(`CopilotKit runtime bridge on http://localhost:${PORT}`);
  console.log(`Proxying AG-UI to ${AGENT_URL}/api/agent`);
});
