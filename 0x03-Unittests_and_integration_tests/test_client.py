
class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    def test_org_google(self):
        """Test that GithubOrgClient.org returns the correct value for google"""
        with patch("client.get_json") as mock_get_json:
            expected_payload = {"login": "google"}
            mock_get_json.return_value = expected_payload
            client = GithubOrgClient("google")
            self.assertEqual(client.org, expected_payload)
            expected_url = "https://api.github.com/orgs/google"
            mock_get_json.assert_called_once_with(expected_url)

    def test_org_abc(self):
        """Test that GithubOrgClient.org returns the correct value for abc"""
        with patch("client.get_json") as mock_get_json:
            expected_payload = {"login": "abc"}
            mock_get_json.return_value = expected_payload
            client = GithubOrgClient("abc")
            self.assertEqual(client.org, expected_payload)
            expected_url = "https://api.github.com/orgs/abc"
            mock_get_json.assert_called_once_with(expected_url)

    def test_public_repos_url(self):
        """Test that _public_repos_url returns correct URL based on org"""
        org_payload_local = {"repos_url": "https://api.github.com/orgs/test/repos"}
        client = GithubOrgClient("test")
        with patch(
            "client.GithubOrgClient.org",
            new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = org_payload_local
            result = client._public_repos_url
            self.assertEqual(result, org_payload_local["repos_url"])

    def test_public_repos(self):
        """Test that public_repos returns list of repo names"""
        repos_payload_local = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"}
        ]
        with patch("client.get_json") as mock_get_json:
            mock_get_json.return_value = repos_payload_local
            client = GithubOrgClient("test")
            with patch(
                "client.GithubOrgClient._public_repos_url",
                new_callable=PropertyMock
            ) as mock_url:
                mock_url.return_value = "fake_url"
                result = client.public_repos()
                self.assertEqual(result, ["repo1", "repo2", "repo3"])
                result_license = client.public_repos(license="mit")
                self.assertEqual(result_license, ["repo1"])

    def test_has_license(self):
        """Test GithubOrgClient.has_license returns correct boolean"""
        repo1 = {"license": {"key": "my_license"}}
        repo2 = {"license": {"key": "other_license"}}
        self.assertTrue(GithubOrgClient.has_license(repo1, "my_license"))
        self.assertFalse(GithubOrgClient.has_license(repo2, "my_license"))


@parameterized_class([{
    "org_payload": org_payload,
    "repos_payload": repos_payload,
    "expected_repos": expected_repos,
    "apache2_repos": apache2_repos
}])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos"""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get for all tests"""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        # Side effect for requests.get
        def side_effect(url, *args, **kwargs):
            mock_resp = Mock()
            if url == "https://api.github.com/orgs/test":
                mock_resp.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                mock_resp.json.return_value = cls.repos_payload
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
        """Integration test for public_repos with license filter"""
        client = GithubOrgClient("test")
        self.assertEqual(
            client.public_repos(license="apache-2.0"), self.apache2_repos
        )
