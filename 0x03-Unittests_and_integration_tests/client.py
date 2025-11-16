#!/usr/bin/env python3
"""
Test module for GithubOrgClient class
Contains unit and integration tests for GithubOrgClient
"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient methods"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that org() returns correct organization data and is memoized"""
        expected_result = {"login": org_name}
        mock_get_json.return_value = expected_result

        client = GithubOrgClient(org_name)

        # Call the org method
        result = client.org()
        self.assertEqual(result, expected_result)

        # Assert get_json called once with correct URL
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

        # Test memoization by calling again
        result2 = client.org()
        self.assertEqual(result2, expected_result)
        # get_json should still have been called only once
        mock_get_json.assert_called_once()

    def test_public_repos_url(self):
        """Test that _public_repos_url property returns correct repos URL"""
        test_payload = {
            "repos_url": "https://api.github.com/orgs/test-org/repos",
            "login": "test-org",
            "id": 123456
        }

        # Mock the org property
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            mock_org.return_value = test_payload
            client = GithubOrgClient("test-org")

            # Call _public_repos_url
            result = client._public_repos_url
            self.assertEqual(result, test_payload["repos_url"])

            # Ensure org property was accessed
            mock_org.assert_called_once()

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos returns correct list of repository names"""
        mock_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]
        mock_get_json.return_value = mock_repos_payload
        mock_repos_url = "https://api.github.com/orgs/test-org/repos"
        client = GithubOrgClient("test-org")

        # Mock _public_repos_url property
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock,
            return_value=mock_repos_url
        ) as mock_public_repos_url:

            result = client.public_repos()
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected_repos)

            # Ensure property and get_json were called once
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(mock_repos_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected_result):
        """Test has_license returns correct boolean for given repo and license"""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected_result)


@parameterized_class([
    {
        'org_payload': TEST_PAYLOAD[0][0],
        'repos_payload': TEST_PAYLOAD[0][1],
        'expected_repos': TEST_PAYLOAD[0][2],
        'apache2_repos': TEST_PAYLOAD[0][3]
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient using fixtures"""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get to return fixture payloads"""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        # Return different payloads based on URL
        def side_effect(url):
            class MockResponse:
                @staticmethod
                def json():
                    if url.endswith('/orgs/test-org'):
                        return cls.org_payload
                    elif url.endswith('/repos'):
                        return cls.repos_payload
                    return None
            return MockResponse()

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop requests.get patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration test: public_repos returns all repository names"""
        client = GithubOrgClient("test-org")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Integration test: public_repos filters repositories by license"""
        client = GithubOrgClient("test-org")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == "__main__":
    unittest.main()