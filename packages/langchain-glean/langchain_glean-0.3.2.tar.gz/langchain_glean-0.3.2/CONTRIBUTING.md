# Contributing to langchain-glean

This document provides guidelines and instructions for setting up your development environment and contributing to `langchain-glean`.

## Development Environment

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and [go-task](https://taskfile.dev/) for task running.

### Prerequisites

1. Install uv:

    ```bash
    pip install uv
    ```

1. Install go-task:

    ```bash
    brew install go-task
    ```

### Setup Development Environment

1. Set up the development environment:

    ```bash
    task setup
    ```

This will create a virtual environment and install all dependencies. The virtual environment will be activated automatically by uv.

## Development Tasks

The project uses [go-task](https://taskfile.dev/) to manage development tasks. Here are the available tasks:

### Testing

| Task | Description |
|------|-------------|
| `task test` | Run unit tests |
| `task test:watch` | Run tests in watch mode |
| `task integration:tests` | Run integration tests |
| `task test:all` | Run all tests and lint fixes |

### Linting and Formatting

| Task | Description |
|------|-------------|
| `task lint` | Run all linters |
| `task lint:diff` | Run linters on changed files |
| `task lint:package` | Run linters on package files |
| `task lint:tests` | Run linters on test files |
| `task lint:fix` | Run lint autofixers |
| `task lint:fix:diff` | Run lint autofixers on changed files |
| `task lint:fix:package` | Run lint autofixers on package files |
| `task lint:fix:tests` | Run lint autofixers on test files |
| `task format` | Run code formatters |
| `task format:diff` | Run formatters on changed files |

### Utility Tasks

| Task | Description |
|------|-------------|
| `task spell:check` | Check spelling |
| `task spell:fix` | Fix spelling |
| `task check:imports` | Check imports |

## Pull Request Process

1. Fork the repository and create your branch from `main`.
2. Make your changes and ensure that all tests pass.
3. Update the documentation to reflect any changes.
4. Submit a pull request.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.
