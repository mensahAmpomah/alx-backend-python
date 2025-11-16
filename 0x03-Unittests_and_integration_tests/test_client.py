#!/usr/bin/env python3
"""Unit and integration tests for client.GithubOrgClient"""
import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    # ===== Task 4: Parameterize org test =====
    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct value"""
        expected_payload = {"login": org_name}
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org

        self.assertEqual(result, expected_payload)
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

    # ===== Task 5: Mocking a property (_public_repos_url) =====
    def test_public_repos_url(self):
        """Unit test GithubOrgClient._public_repos_url with mocked org"""
        client = GithubOrgClient("test_org")

        with patch(
            "client.GithubOrgClient.org",
            new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = {"repos_url": "https://api.github.com/orgs/test_org/repos"}
            result = client._public_repos_url
            self.assertEqual(result, "https://api.github.com/orgs/test_org/repos")

    # ===== Task 6: More patching for public_repos =====
    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Unit test GithubOrgClient.public_repos"""
        payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"}
        ]
        mock_get_json.return_value = payload
        client = GithubOrgClient("test_org")

        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = "fake_url"

            result = client.public_repos()
            result_license = client.public_repos(license="mit")

            self.assertEqual(result, ["repo1", "repo2", "repo3"])
            self.assertEqual(result_license, ["repo1"])

            mock_get_json.assert_called_once_with("fake_url")
            self.assertEqual(mock_url.call_count, 2)

    # ===== Task 7: Parameterized test_has_license =====
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, repo, license_key, expected):
        """Unit test for GithubOrgClient.has_license"""
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)


# ===== Task 8: Integration tests using fixtures =====
@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos"""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get for all tests"""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url, *args, **kwargs):
            mock_resp = Mock()
            if url == cls.org_payload.get("repos_url"):
                mock_resp.json.return_value = cls.repos_payload
            elif url == "https://api.github.com/orgs/test":
                mock_resp.json.return_value = cls.org_payload
            else:
                mock_resp.json.return_value = {}
            return mock_resp

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop patcher after all tests"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration test for public_repos returns all repos"""
        client = GithubOrgClient("test")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Integration test for public_repos filtered by license"""
        client = GithubOrgClient("test")
        self.assertEqual(
            client.public_repos(license="apache-2.0"), self.apache2_repos
        )