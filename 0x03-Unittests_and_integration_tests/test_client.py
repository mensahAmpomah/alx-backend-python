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
        # Arrange: mock payload from get_json
        payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"}
        ]
        mock_get_json.return_value = payload

        client = GithubOrgClient("test_org")

        # Patch _public_repos_url property
        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = "fake_url"

            # Act
            result = client.public_repos()
            result_license = client.public_repos(license="mit")

            # Assert
            self.assertEqual(result, ["repo1", "repo2", "repo3"])
            self.assertEqual(result_license, ["repo1"])

            # Ensure mocks were called exactly once
            mock_get_json.assert_called_once_with("fake_url")
            self.assertEqual(mock_url.call_count, 2)  # accessed twice