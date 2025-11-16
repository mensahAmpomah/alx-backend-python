#!/usr/bin/env python3
"""Unit tests for client.GithubOrgClient"""
import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    # ===== PARAMETERIZED + PATCHED DECORATORS =====
    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct value"""
        # Arrange: mocked get_json returns a fake payload
        expected_payload = {"login": org_name}
        mock_get_json.return_value = expected_payload

        # Act: create client and access .org property
        client = GithubOrgClient(org_name)
        result = client.org

        # Assert: .org returns the mocked payload
        self.assertEqual(result, expected_payload)

        # Assert: get_json called exactly once with correct URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
