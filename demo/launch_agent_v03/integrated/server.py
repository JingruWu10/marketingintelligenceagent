"""Read-only local HTTP bridge for Marketing Intelligence Agent v0.3.

Development/synthetic fixtures only. Do NOT deploy this server publicly: no auth,
privacy/consent controls, rate limiting, or hardened tenancy.
"""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import RLock
from uuid import uuid4
from urllib.parse import urlsplit, parse_qs

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from conversation_agent import new_session, respond
from semantic_launch import run

LAUNCHES = {"ZELDA_2026", "SWITCH2_2025"}
MAX_BODY = 16_384


class SessionStore:
    def __init__(self):
        self.lock = RLock()
        self.items = {}

    def answer(self, folder, question, launch_id, session_id):
        with self.lock:
            state = self.items.get(session_id) if session_id else None
            if state and state['launch_id'] != launch_id:
                raise ValueError('Session belongs to a different launch; start a new session.')
            response, next_state = respond(folder, question, state, launch_id)
            if not session_id:
                session_id = str(uuid4())
            self.items[session_id] = next_state
            return {"session_id": session_id, "answer": response, "turn_count": len(next_state['turns'])}


class LocalServer(ThreadingHTTPServer):
    def __init__(self, host, port, folder):
        super().__init__((host, port), AgentHandler)
        self.data_dir = Path(folder).resolve()
        self.sessions = SessionStore()
        self.frontend = Path(__file__).parent / 'executive.html'


class AgentHandler(BaseHTTPRequestHandler):
    def _json(self, value, status=200):
        body = json.dumps(value, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlsplit(self.path)
        if parsed.path in ('/', '/executive.html'):
            try:
                html = self.server.frontend.read_bytes()
            except OSError:
                return self._json({'error': 'frontend not installed'}, 500)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'")
            self.send_header('Content-Length', str(len(html)))
            self.end_headers()
            self.wfile.write(html)
        elif parsed.path == '/api/health':
            self._json({'ok': True, 'mode': 'synthetic_read_only', 'version': 'v0.3'})
        elif parsed.path == '/api/overview':
            lid = parse_qs(parsed.query).get('launch_id', ['ZELDA_2026'])[0]
            if lid not in LAUNCHES:
                return self._json({'error': 'Unsupported launch ID'}, 400)
            try:
                result = run(self.server.data_dir, lid)
                self._json(result)
            except (ValueError, OSError, KeyError) as ex:
                self._json({'error': str(ex)}, 422)
        else:
            self._json({'error': 'Not found'}, 404)

    def do_POST(self):
        if urlsplit(self.path).path != '/api/investigate':
            return self._json({'error': 'Not found'}, 404)
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 1 <= size <= MAX_BODY:
                return self._json({'error': 'Invalid payload size'}, 413)
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                return self._json({'error': 'Invalid payload'}, 400)
            question = payload.get('question')
            launch_id = payload.get('launch_id', 'ZELDA_2026')
            sid = payload.get('session_id')
            if not isinstance(question, str) or not question.strip() or len(question) > 1000:
                return self._json({'error': 'Question required (max 1000 chars)'}, 400)
            if launch_id not in LAUNCHES:
                return self._json({'error': 'Unsupported launch ID'}, 400)
            if sid is not None and (not isinstance(sid, str) or len(sid) > 64):
                return self._json({'error': 'Invalid session ID'}, 400)
            result = self.server.sessions.answer(self.server.data_dir, question, launch_id, sid)
            self._json(result)
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as ex:
            self._json({'error': str(ex)}, 400)
        except OSError as ex:
            self._json({'error': f'Source data unavailable: {ex.filename}'}, 503)


def main():
    parser = argparse.ArgumentParser(description='Local read-only launch investigation service')
    parser.add_argument('--data-dir', type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8787)
    args = parser.parse_args()
    server = LocalServer(args.host, args.port, args.data_dir)
    print(f'Open http://{args.host}:{args.port} — synthetic read-only local demo', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()