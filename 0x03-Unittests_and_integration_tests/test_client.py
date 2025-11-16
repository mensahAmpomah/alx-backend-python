#!/usr/bin/env python3
"""Unit and integration tests for GithubOrgClient"""
import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


# ------------------------
# UNIT TESTS
# ------------------------
class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Unit test for has_license static method"""
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)

    @patch("utils.get_json")
    def test_public_repos(self, mock_get_json):
        """Unit test for public_repos method"""
        payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]
        mock_get_json.return_value = payload

        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = "http://example.com"
            client = GithubOrgClient("test_org")

            result = client.public_repos()
            self.assertEqual(result, ["repo1", "repo2", "repo3"])

            # Ensure mocks are called exactly once
            mock_get_json.assert_called_once_with("http://example.com")
            mock_url.assert_called_once()


# ------------------------
# INTEGRATION TESTS
# ------------------------
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient using fixtures"""

    # Fixtures as class attributes
    org_payload = org_payload
    repos_payload = repos_payload
    expected_repos = expected_repos
    apache2_repos = apache2_repos

    @classmethod
    def setUpClass(cls):
        """Patch requests.get to return fixture payloads"""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url, *args, **kwargs):
            mock_resp = Mock()
            if url == f"https://api.github.com/orgs/{cls.org_payload['login']}":
                mock_resp.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                mock_resp.json.return_value = cls.repos_payload
            else:
                mock_resp.json.return_value = {}
            return mock_resp

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration test: public_repos returns all repos"""
        client = GithubOrgClient(self.org_payload["login"])
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Integration test: public_repos filters by license"""
        client = GithubOrgClient(self.org_payload["login"])
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )