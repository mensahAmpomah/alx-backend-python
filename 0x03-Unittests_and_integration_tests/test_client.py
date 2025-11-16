#!/usr/bin/env python3
"""Unit and integration tests for client.GithubOrgClient"""
import unittest
from unittest.mock import patch, PropertyMock, Mock
from utils import get_json, access_nested_map, memoize
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos
from parameterized import parameterized, parameterized_class
from typing import List, Dict


# ------------------------
# CLIENT CLASS FIXED HERE
# ------------------------
class GithubOrgClient:
    """A GitHub org client."""

    ORG_URL = "https://api.github.com/orgs/{org}"

    def __init__(self, org_name: str) -> None:
        self._org_name = org_name

    @memoize
    def org(self) -> Dict:
        """Return org info from GitHub."""
        return get_json(self.ORG_URL.format(org=self._org_name))

    @property
    def _public_repos_url(self) -> str:
        return self.org["repos_url"]

    @memoize
    def repos_payload(self) -> Dict:
        return get_json(self._public_repos_url)

    def public_repos(self, license: str = None) -> List[str]:
        payload = self.repos_payload
        return [
            repo["name"] for repo in payload
            if license is None or self.has_license(repo, license)
        ]

    @staticmethod
    def has_license(repo: Dict, license_key: str) -> bool:
        """Return True if repo has the specified license key"""
        license_info = repo.get("license")
        if not isinstance(license_info, dict):
            return False
        return license_info.get("key") == license_key


# ------------------------
# UNIT TESTS
# ------------------------
class TestGithubOrgClient(unittest.TestCase):
    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch("utils.get_json")
    def test_org(self, org_name, mock_get_json):
        expected = {"login": org_name}
        mock_get_json.return_value = expected
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        with patch(
            "GithubOrgClient.org",
            new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = {"repos_url": "http://example.com"}
            client = GithubOrgClient("test")
            self.assertEqual(client._public_repos_url, "http://example.com")

    @patch("utils.get_json")
    def test_public_repos(self, mock_get_json):
        mock_get_json.return_value = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]
        with patch(
            "GithubOrgClient._public_repos_url",
            new_callable=PropertyMock
        ) as mock_repos_url:
            mock_repos_url.return_value = "http://example.com"
            client = GithubOrgClient("test")
            self.assertEqual(
                client.public_repos(),
                ["repo1", "repo2", "repo3"]
            )
            self.assertEqual(
                client.public_repos(license="mit"),
                ["repo1"]
            )
            mock_repos_url.assert_called()
            mock_get_json.assert_called_once_with("http://example.com")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False)
    ])
    def test_has_license(self, repo, license_key, expected):
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )


# ------------------------
# INTEGRATION TESTS
# ------------------------
@parameterized_class([{
    "org_payload": org_payload,
    "repos_payload": repos_payload,
    "expected_repos": expected_repos,
    "apache2_repos": apache2_repos,
}])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.get_patcher = patch("utils.requests.get")
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url, *args, **kwargs):
            mock_response = Mock()
            if url == f"https://api.github.com/orgs/{cls.org_payload['login']}":
                mock_response.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = {}
            return mock_response

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        cls.get_patcher.stop()

    def test_public_repos(self):
        client = GithubOrgClient(self.org_payload["login"])
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        client = GithubOrgClient(self.org_payload["login"])
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )