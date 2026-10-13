"""Local integrated HTTP smoke tests.

Run with synthetic fixture directory:
    python demo/launch_agent_v03/test_integrated_http.py --data-dir /path/to/zelda_agent_v03

No production data, network integration or external dependency.
"""
from __future__ import annotations
import argparse
import json
import sys
import threading
import unittest
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "integrated"))
from server import LocalServer  # noqa: E402

FIXTURES = None


class TestIntegratedHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = LocalServer("127.0.0.1", 0, FIXTURES)
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = "http://127.0.0.1:" + str(cls.http.server_address[1])

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()

    def get(self, path):
        with urlopen(self.url + path, timeout=30) as res:
            return json.load(res)

    def post(self, data):
        req = Request(self.url + "/api/investigate", data=json.dumps(data).encode(),
                      headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(req, timeout=30) as res:
            return json.load(res)

    def test_health(self):
        self.assertTrue(self.get("/api/health")["ok"])

    def test_semantic_overview(self):
        data = self.get("/api/overview?launch_id=ZELDA_2026")
        self.assertEqual(data["metrics"]["purchasing_customers"], 53)
        self.assertEqual(data["metrics"]["reached"], 1657)

    def test_context_and_evidence(self):
        first = self.post({"launch_id": "ZELDA_2026", "question": "Why are new customers buying less?"})
        second = self.post({"launch_id": "ZELDA_2026", "question": "Is it understanding or audience?",
                            "session_id": first["session_id"]})
        self.assertEqual((first["turn_count"], second["turn_count"]), (1, 2))
        self.assertEqual(first["session_id"], second["session_id"])
        self.assertEqual(len(second["answer"]["hypothesis_comparison"]["evidence_matrix"]), 8)
        self.assertEqual(second["answer"]["orchestration"]["outbound_actions"], [])

    def test_checkout_and_baseline(self):
        data = self.get("/api/overview?launch_id=SWITCH2_2025")
        self.assertEqual(data["metrics"]["purchasing_customers"], 87)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    args = parser.parse_args()
    FIXTURES = Path(args.data_dir)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestIntegratedHTTP)
    sys.exit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
