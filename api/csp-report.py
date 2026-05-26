"""
/api/csp-report — CSP violation collector (Report-Only, observability only)

Purpose:
    Receives Content-Security-Policy violation reports sent by browsers via
    the `report-uri /api/csp-report` directive in the CSP Report-Only header.

Privacy constraints (enforced in code):
    - Reads at most 4 KB of the request body regardless of Content-Length.
    - Does NOT log the full payload.
    - Does NOT log IP addresses, cookies, Authorization headers, or User-Agent.
    - Logs only: timestamp (UTC), blocked-uri, violated-directive,
      and a truncated document-uri (max 200 chars each).
    - Always responds 204 No Content — never exposes internal state.

This collector is TEMPORARY and is used solely to observe CSP violations
during the Report-Only phase before any enforcement decision is made.
It does not write to any database or external service.
Logs are visible in Vercel Functions → Logs (retention per plan).

See SECURITY-HARDENING.md § CSP Report-Only collector for full context.
"""

import datetime
import json
from http.server import BaseHTTPRequestHandler

MAX_BODY      = 4096   # maximum bytes read from request body
MAX_URI_CHARS = 200    # maximum characters logged from any URI field
MAX_DIR_CHARS = 120    # maximum characters logged from violated-directive


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        """Accept a CSP report, log minimal safe fields, always return 204."""
        # ── Read body, capped at MAX_BODY regardless of Content-Length ───
        try:
            declared = int(self.headers.get("Content-Length", 0))
        except (ValueError, TypeError):
            declared = 0
        body = self.rfile.read(min(declared, MAX_BODY))

        # ── Parse and log — never raise ──────────────────────────────────
        try:
            payload = json.loads(body)
            if not isinstance(payload, dict):
                raise ValueError("unexpected payload type")

            # Browsers send {"csp-report": {...}}; some send flat objects.
            report = payload.get("csp-report", payload)
            if not isinstance(report, dict):
                report = {}

            blocked   = str(report.get("blocked-uri",        ""))[:MAX_URI_CHARS]
            directive = str(report.get("violated-directive", ""))[:MAX_DIR_CHARS]
            doc_uri   = str(report.get("document-uri",       ""))[:MAX_URI_CHARS]
            ts        = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

            # Single-line log — no PII, no full payload
            print(
                f"[CSP] ts={ts}"
                f" blocked={blocked!r}"
                f" directive={directive!r}"
                f" doc={doc_uri!r}"
            )
        except Exception:
            # Silently discard malformed, empty, or unexpected payloads.
            pass

        self._no_content()

    def do_OPTIONS(self):
        """Respond to preflight requests with 204."""
        self._no_content()

    def _no_content(self):
        self.send_response(204)
        self.end_headers()

    def log_message(self, *args):
        """Silence default BaseHTTPRequestHandler access logs."""
        pass
