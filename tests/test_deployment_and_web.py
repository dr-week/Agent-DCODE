"""
Unit tests for Web UI Application, WSGI Serverless handler, and API routes.
Verifies production deployment endpoints and WSGI compliance.
"""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.web.app import create_app
from dcode.web.serverless import handler


class TestDeploymentAndWeb(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_wsgi_handler_is_callable(self):
        self.assertTrue(callable(handler))

    def test_index_route_serves_html(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"DCode Agent", res.data)
        self.assertIn(b"style.css", res.data)
        res.close()

    def test_status_api_route(self):
        res = self.client.get("/api/status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("status", data)


if __name__ == "__main__":
    unittest.main()
