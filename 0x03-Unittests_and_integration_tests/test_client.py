#!/usr/bin/env python3
"""Unit tests for client.GithubOrgClient"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch("client.get_json")  # patch get_json in the client module
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value"""
        # Set a fake return value for get_json
        expected_payload = {"login": org_name}
        mock_get_json.return_value = expected_payload

        # Create GithubOrgClient instance
        client = GithubOrgClient(org_name)

        # Access org property
        result = client.org

        # Ensure the result matches expected_payload
        self.assertEqual(result, expected_payload)

        # Ensure get_json was called exactly once with the correct URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
