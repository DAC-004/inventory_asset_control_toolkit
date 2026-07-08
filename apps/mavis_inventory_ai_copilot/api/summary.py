"""Vercel serverless proxy for OpenAI management summaries."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler

SYSTEM_PROMPT = """You are an inventory optimization analyst writing an executive management summary.

Rules:
- Use ONLY the structured metrics provided in the user message. Do not invent SKUs, locations, dollar values, or counts.
- State clearly that recommendations are based on the current sample data loaded in the toolkit.
- Avoid claiming certainty beyond the supplied data.
- Recommend human review before executing transfers, markdowns, or replenishment actions.
- Write in clear executive-ready markdown with sections: Executive Overview, Priority Risks, Recommended Actions (Transfers, Markdown & Exit, Replenishment), Financial Impact Summary (markdown table), and Next Steps.
- Keep the tone professional and concise."""


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:
        _json_response(self, 204, {})

    def do_POST(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            _json_response(
                self,
                500,
                {"error": "OPENAI_API_KEY is not configured in Vercel project settings."},
            )
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw) if raw else {}
            model = payload.get("model") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            context = payload.get("context", {})
        except (ValueError, json.JSONDecodeError) as exc:
            _json_response(self, 400, {"error": f"Invalid request body: {exc}"})
            return

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            "Generate an inventory optimization management summary from these "
                            f"calculated metrics:\n\n{json.dumps(context, indent=2)}"
                        ),
                    },
                ],
                temperature=0.3,
            )
            content = response.choices[0].message.content or ""
            if not content.strip():
                _json_response(self, 502, {"error": "OpenAI returned an empty summary."})
                return
            _json_response(self, 200, {"summary": content.strip()})
        except Exception as exc:
            _json_response(self, 502, {"error": f"OpenAI request failed: {exc}"})
