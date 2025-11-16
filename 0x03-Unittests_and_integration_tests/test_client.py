#!/usr/bin/env python3
"""Unit tests for client.GithubOrgClient"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


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

        # Patch the .org property using PropertyMock
        with patch(
            "client.GithubOrgClient.org",
            new_callable=PropertyMock
        ) as mock_org:
            # Mocked payload with repos_url
            mock_org.return_value = {"repos_url": "https://api.github.com/orgs/test_org/repos"}

            # Access _public_repos_url property
            result = client._public_repos_url

            # Assert the property returns the mocked repos_url
            self.assertEqual(result, "https://api.github.com/orgs/test_org/repos")