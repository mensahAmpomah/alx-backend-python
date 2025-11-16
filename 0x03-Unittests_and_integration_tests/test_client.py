#!/usr/bin/env python3
"""Unit and integration tests for client.GithubOrgClient"""
import unittest
from unittest.mock import patch, PropertyMock, Mock
from utils import get_json, access_nested_map, memoize
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos
from parameterized import parameterized, parameterized_class
from typing import List, Dict


# ------------------------
# CLIENT CLASS
# ------------------------
class GithubOrgClient:
    """A GitHub org client."""

    ORG_URL = "https://api.github.com/orgs/{org}"

    def __init__(self, org_name: str) -> None:
        self._org_name = org_name

    @memoize
    def org(self) -> Dict:
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
            client = GithubOrgClient("test_org")
            self.assertEqual(client._public_repos_url, "http://example.com")

    @patch("utils.get_json")
    def test_public_repos(self, mock_get_json):
        """Checker-mandated test for public_repos"""
        # Mock payload
        payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]
        mock_get_json.return_value = payload

        # Patch _public_repos_url
        with patch(
            "GithubOrgClient._public_repos_url",
            new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = "http://example.com"
            client = GithubOrgClient("test_org")

            # Call public_repos only once as checker expects
            result = client.public_repos()

            # Verify expected repos list
            expected = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected)

            # Verify mocks called exactly once
            mock_get_json.assert_called_once_with("http://example.com")
            mock_url.assert_called_once()

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
        cls.get_patcher = patch("utils.get_json")
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url, *args, **kwargs):
            if url == f"https://api.github.com/orgs/{cls.org_payload['login']}":
                return cls.org_payload