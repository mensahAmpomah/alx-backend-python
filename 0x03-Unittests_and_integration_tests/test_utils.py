#!/usr/bin/env python3
"""Unit tests for utils.py functions"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Tests for the access_nested_map function"""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2)
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test access_nested_map returns expected results"""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b")
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key):
        """Test KeyError is raised when path is invalid"""
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        # KeyError message includes quotes in Python
        self.assertEqual(str(context.exception), f"'{expected_key}'")


class TestGetJson(unittest.TestCase):
    """Tests for utils.get_json"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False})
    ])
    def test_get_json(self, test_url, test_payload):
        """Test get_json returns expected payload with mocked requests.get"""
        # Create mock response object
        mock_response = Mock()
        # Set mock json return value
        mock_response.json.return_value = test_payload

        # Patch requests.get where it's used in utils.py
        with patch(
                "utils.requests.get", return_value=mock_response) as mock_get:
            result = get_json(test_url)
            # Ensure requests.get was called exactly once with test_url
            mock_get.assert_called_once_with(test_url)
            # Ensure get_json returns the expected payload
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test utils.memoize decorator"""

    def test_memoize(self):
        """Test that memoize caches method results"""

        class TestClass:
            """Test class for memoize"""

            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        # Create instance
        test_obj = TestClass()

        # Patch a_method
        with patch.object(
                TestClass, "a_method", return_value=42) as mock_method:
            result1 = test_obj.a_property
            result2 = test_obj.a_property

            # Ensure the value is correct
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)

            # Ensure a_method was called only once
            mock_method.assert_called_once()
