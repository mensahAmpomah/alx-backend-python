#!/usr/bin/env python3
"""Fixtures for GithubOrgClient tests"""

# Organization payload
org_payload = {
    "login": "test_org",
    "repos_url": "http://example.com/repos"
}

# Repositories payload
repos_payload = [
    {"name": "repo1", "license": {"key": "mit"}},
    {"name": "repo2", "license": {"key": "apache-2.0"}},
    {"name": "repo3", "license": None},
]

# Expected repo names for public_repos()
expected_repos = ["repo1", "repo2", "repo3"]

# Expected repo names with Apache license
apache2_repos = ["repo2"]