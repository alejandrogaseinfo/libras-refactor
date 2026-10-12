import unittest

from libras_agents.evidence import is_private_blob_url


class BlobCitationTests(unittest.TestCase):
    def test_private_blob_urls_are_suppressed(self):
        for url in (
            "blob:anything",
            "https://store.blob.core.windows.net/container/file?sig=hidden",
            "https://STORE.BLOB.CORE.WINDOWS.NET./file",
            "https://store.blob.core.usgovcloudapi.net/file",
            "https://store.blob.core.chinacloudapi.cn/file",
        ):
            with self.subTest(url=url):
                self.assertTrue(is_private_blob_url(url))

    def test_public_and_non_blob_urls_are_allowed(self):
        for url in (
            "https://example.org/document",
            "https://example.sharepoint.com/document",
            "https://blob.core.windows.net.attacker.example/document",
            "https://store.blob.core.windows.net.attacker.example/file",
            "",
            None,
        ):
            with self.subTest(url=url):
                self.assertFalse(is_private_blob_url(url))

    def test_malformed_url_is_handled(self):
        self.assertFalse(is_private_blob_url("https://[invalid"))


if __name__ == "__main__":
    unittest.main()
