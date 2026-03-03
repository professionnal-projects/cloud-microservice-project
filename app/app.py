import os
import platform
import threading
import time
from typing import Any

from flask import Flask, jsonify, render_template_string, request


DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>{{ app_name }} | Dashboard</title>
  <style>
    :root {
      --bg: #0b1220;
      --card: #111a2b;
      --accent: #60a5fa;
      --ok: #22c55e;
      --warn: #f59e0b;
      --text: #e2e8f0;
      --muted: #94a3b8;
      --border: #1f2a44;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
      background: radial-gradient(circle at top, #17233b 0%, var(--bg) 60%);
      color: var(--text);
      min-height: 100vh;
    }
    .container {
      max-width: 1100px;
      margin: 0 auto;
      padding: 24px;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 20px;
    }
    .title {
      margin: 0;
      font-size: 1.8rem;
      letter-spacing: 0.2px;
    }
    .subtitle {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 0.95rem;
    }
    .pill {
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 8px 12px;
      color: var(--muted);
      background: rgba(17, 26, 43, 0.85);
      font-size: 0.9rem;
    }
    .grid {
      display: grid;
      gap: 14px;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      margin-bottom: 14px;
    }
    .card {
      background: rgba(17, 26, 43, 0.92);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px;
      box-shadow: 0 10px 24px rgba(0, 0, 0, 0.25);
    }
    .label {
      color: var(--muted);
      font-size: 0.85rem;
      margin-bottom: 6px;
    }
    .value {
      font-size: 1.4rem;
      font-weight: 600;
      color: var(--accent);
    }
    .section-title {
      margin: 0 0 8px;
      font-size: 1rem;
      font-weight: 600;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
    }
    th, td {
      text-align: left;
      padding: 10px;
      border-bottom: 1px solid var(--border);
    }
    th { color: var(--muted); font-weight: 500; }
    .status {
      padding: 3px 8px;
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: 700;
      display: inline-block;
    }
    .status.up { background: rgba(34, 197, 94, 0.15); color: var(--ok); }
    .status.down { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
    pre {
      margin: 0;
      overflow-x: auto;
      border-radius: 8px;
      padding: 12px;
      border: 1px solid var(--border);
      background: rgba(8, 14, 24, 0.8);
      color: #d1d5db;
      font-size: 0.86rem;
      line-height: 1.35;
    }
    .footer {
      margin-top: 18px;
      color: var(--muted);
      font-size: 0.85rem;
      display: flex;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
    }
    .warn { color: var(--warn); }
  </style>
</head>
<body>
  <div class=\"container\">
    <div class=\"header\">
      <div>
        <h1 class=\"title\">{{ app_name }} Dashboard</h1>
        <p class=\"subtitle\">Flask API • Nginx Reverse Proxy • Docker • CI/CD</p>
      </div>
      <div class=\"pill\">Environment: {{ app_env }}</div>
    </div>

    <div class=\"grid\">
      <div class=\"card\">
        <div class=\"label\">Requests Served</div>
        <div class=\"value\" id=\"requestCount\">0</div>
      </div>
      <div class=\"card\">
        <div class=\"label\">Uptime (s)</div>
        <div class=\"value\" id=\"uptime\">0</div>
      </div>
      <div class=\"card\">
        <div class=\"label\">Echo Requests</div>
        <div class=\"value\" id=\"echoCount\">0</div>
      </div>
      <div class=\"card\">
        <div class=\"label\">Version</div>
        <div class=\"value\" id=\"version\">{{ app_version }}</div>
      </div>
    </div>

    <div class=\"card\" style=\"margin-bottom:14px\">
      <h2 class=\"section-title\">Architecture Diagram</h2>
      <pre>Client Browser / API Consumer
            |
            v
      +-------------+
      |    Nginx    |  :80
      +-------------+
            |
            v
      +-------------+
      | Flask API   |  :5000
      +-------------+
            |
            v
      +-------------+
      |  Metrics &  |
      | Health Data |
      +-------------+</pre>
    </div>

    <div class=\"card\">
      <h2 class=\"section-title\">Route Status</h2>
      <table>
        <thead>
          <tr><th>Route</th><th>Method</th><th>Status</th></tr>
        </thead>
        <tbody>
          <tr><td>/</td><td>GET</td><td><span class=\"status\" id=\"routeRoot\">Checking</span></td></tr>
          <tr><td>/health</td><td>GET</td><td><span class=\"status\" id=\"routeHealth\">Checking</span></td></tr>
          <tr><td>/info</td><td>GET</td><td><span class=\"status\" id=\"routeInfo\">Checking</span></td></tr>
          <tr><td>/metrics</td><td>GET</td><td><span class=\"status\" id=\"routeMetrics\">Checking</span></td></tr>
          <tr><td>/echo</td><td>POST</td><td><span class=\"status\" id=\"routeEcho\">Checking</span></td></tr>
        </tbody>
      </table>
    </div>

    <div class=\"footer\">
      <span>Live data refreshes every 2 seconds.</span>
      <span class=\"warn\">SPOF note: a single host is still a single point of failure.</span>
    </div>
  </div>

  <script>
    function setStatus(elementId, isUp) {
      const el = document.getElementById(elementId);
      el.textContent = isUp ? 'UP' : 'DOWN';
      el.className = 'status ' + (isUp ? 'up' : 'down');
    }

    async function checkRoute(route, method, elementId, body = null) {
      try {
        const options = { method: method, headers: {} };
        if (body) {
          options.headers['Content-Type'] = 'application/json';
          options.body = JSON.stringify(body);
        }
        const response = await fetch(route, options);
        setStatus(elementId, response.ok);
      } catch {
        setStatus(elementId, false);
      }
    }

    async function loadMetrics() {
      try {
        const response = await fetch('/metrics');
        if (!response.ok) {
          return;
        }
        const data = await response.json();
        document.getElementById('requestCount').textContent = data.request_count;
        document.getElementById('uptime').textContent = data.uptime_seconds;
        document.getElementById('echoCount').textContent = data.echo_request_count;
        document.getElementById('version').textContent = data.app_version;
      } catch {
        // Keep previous values on transient errors.
      }
    }

    async function refreshDashboard() {
      await Promise.all([
        checkRoute('/', 'GET', 'routeRoot'),
        checkRoute('/health', 'GET', 'routeHealth'),
        checkRoute('/info', 'GET', 'routeInfo'),
        checkRoute('/metrics', 'GET', 'routeMetrics'),
        checkRoute('/echo', 'POST', 'routeEcho', { ping: 'pong' }),
        loadMetrics()
      ]);
    }

    refreshDashboard();
    setInterval(refreshDashboard, 2000);
  </script>
</body>
</html>
"""


def create_app() -> Flask:
    app = Flask(__name__)

    app_name = os.getenv("APP_NAME", "Cloud Microservice API")
    app_env = os.getenv("APP_ENV", "development")
    app_version = os.getenv("APP_VERSION", "1.0.0")

    state = {
        "start_time": time.time(),
        "request_count": 0,
        "echo_request_count": 0,
    }
    state_lock = threading.Lock()

    @app.before_request
    def count_requests() -> None:
        with state_lock:
            state["request_count"] += 1

    def build_metrics_payload() -> dict[str, Any]:
        with state_lock:
            uptime = round(time.time() - state["start_time"], 2)
            return {
                "app_name": app_name,
                "app_env": app_env,
                "app_version": app_version,
                "uptime_seconds": uptime,
                "request_count": state["request_count"],
                "echo_request_count": state["echo_request_count"],
                "python_version": platform.python_version(),
                "platform": platform.platform(),
            }

    @app.get("/")
    def dashboard() -> str:
        return render_template_string(
            DASHBOARD_TEMPLATE,
            app_name=app_name,
            app_env=app_env,
            app_version=app_version,
        )

    @app.get("/health")
    def health() -> Any:
        payload = {
            "status": "ok",
            "service": app_name,
            "environment": app_env,
            "timestamp": int(time.time()),
        }
        return jsonify(payload), 200

    @app.get("/info")
    def info() -> Any:
        payload = {
            "service": app_name,
            "version": app_version,
            "environment": app_env,
            "runtime": "Flask",
        }
        return jsonify(payload), 200

    @app.get("/metrics")
    def metrics() -> Any:
        return jsonify(build_metrics_payload()), 200

    @app.post("/echo")
    def echo() -> Any:
        body = request.get_json(silent=True)
        if body is None:
            return jsonify({"error": "Request body must be valid JSON"}), 400

        with state_lock:
            state["echo_request_count"] += 1

        payload = {
            "received": body,
            "content_type": request.content_type,
            "message": "Payload echoed successfully",
        }
        return jsonify(payload), 200

    return app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host=host, port=port)
