# Unittests and Integration Tests

This project focuses on writing effective **unit tests** and **integration tests** in Python using the `unittest` framework. The goal is to understand how to test small isolated functions (unit tests) and how to test full code execution paths (integration tests). The project also covers concepts such as **mocking**, **memoization**, and **parameterized test cases**.

## Project Objectives

By the end of this project, you should be able to:

- Explain the difference between **unit tests** and **integration tests**.
- Write unit tests that validate individual function behavior using various inputs.
- Apply **mocking** to isolate functions from external dependencies such as:
  - HTTP requests
  - Database access
  - File I/O
- Use `parameterized.expand` to test multiple input/output combinations efficiently.
- Write integration tests that cover an end-to-end code path with minimal mocking.
- Use `unittest.mock` features including:
  - `patch`
  - `Mock`
  - `PropertyMock`
- Understand how memoization affects function testing.

## Technologies Used

- Python 3.7 (Ubuntu 18.04 LTS)
- `unittest` (Standard Library)
- `unittest.mock`
- `parameterized` package
- `pycodestyle` for formatting

## Requirements

- All Python files must be executable.
- Code must follow the **pycodestyle (v2.5)** standard.
- Every module, class, and function must contain meaningful documentation.
- All functions and methods must use **type annotations**.
- Tests must be run using:

  ```bash
  python3 -m unittest path/to/test_file.py