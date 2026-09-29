import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from mr_puwlerson.bot import configure_ca_bundle


class CABundleTests(unittest.TestCase):
    def test_missing_default_uses_existing_system_bundle(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("mr_puwlerson.bot.ssl.get_default_verify_paths", return_value=SimpleNamespace(cafile=None)),
            patch.object(Path, "is_file", return_value=True),
        ):
            configure_ca_bundle()
            self.assertEqual(os.environ["SSL_CERT_FILE"], "/etc/ssl/certs/ca-certificates.crt")

    def test_explicit_ca_file_is_preserved(self):
        with patch.dict(os.environ, {"SSL_CERT_FILE": "/custom/ca.pem"}, clear=True):
            configure_ca_bundle()
            self.assertEqual(os.environ["SSL_CERT_FILE"], "/custom/ca.pem")

    def test_existing_default_ca_file_is_preserved(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("mr_puwlerson.bot.ssl.get_default_verify_paths", return_value=SimpleNamespace(cafile="/default/ca.pem")),
        ):
            configure_ca_bundle()
            self.assertNotIn("SSL_CERT_FILE", os.environ)

    def test_no_bundle_does_not_disable_verification(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("mr_puwlerson.bot.ssl.get_default_verify_paths", return_value=SimpleNamespace(cafile=None)),
            patch.object(Path, "is_file", return_value=False),
        ):
            configure_ca_bundle()
            self.assertNotIn("SSL_CERT_FILE", os.environ)


if __name__ == "__main__":
    unittest.main()
