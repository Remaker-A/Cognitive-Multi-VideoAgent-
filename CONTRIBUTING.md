# Contributing to VideoGen

First off, thank you for considering contributing to VideoGen! 🎉

It's people like you that make VideoGen such a great tool for AI video generation.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

---

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Standards

- **Be respectful**: Treat everyone with respect and kindness
- **Be collaborative**: Work together and help each other
- **Be inclusive**: Welcome newcomers and diverse perspectives
- **Be constructive**: Provide helpful feedback and suggestions

---

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, screenshots, etc.)
- **Describe the behavior you observed** and what you expected
- **Include your environment details** (OS, Python version, etc.)

**Bug Report Template:**

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Windows 11]
 - Python Version: [e.g. 3.9.7]
 - VideoGen Version: [e.g. 2.0.0]

**Additional context**
Any other context about the problem.
```

### 💡 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any alternative solutions** you've considered

### 🔧 Contributing Code

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** if you've added code that should be tested
4. **Ensure the test suite passes**
5. **Update documentation** as needed
6. **Submit a pull request**

---

## Development Setup

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Node.js 16+ (for frontend)
- Git

### Setup Steps

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/videogen.git
   cd videogen
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

5. **Start infrastructure services**:
   ```bash
   docker-compose up -d
   ```

6. **Initialize database**:
   ```bash
   python scripts/init_blackboard.sh
   ```

7. **Run tests to verify setup**:
   ```bash
   pytest
   ```

---

## Pull Request Process

### Before Submitting

1. **Update your fork** with the latest changes from `main`:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run tests**:
   ```bash
   pytest
   ```

3. **Run linters**:
   ```bash
   black .
   flake8 .
   mypy src/
   ```

4. **Update documentation** if needed

### Submitting the PR

1. **Push your changes**:
   ```bash
   git push origin your-feature-branch
   ```

2. **Create a Pull Request** on GitHub

3. **Fill out the PR template** with:
   - Description of changes
   - Related issue number (if applicable)
   - Type of change (bug fix, feature, docs, etc.)
   - Checklist of completed items

**PR Template:**

```markdown
## Description
Brief description of what this PR does.

## Related Issue
Fixes #(issue number)

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran to verify your changes.

## Checklist:
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

### Review Process

- Maintainers will review your PR within 1-2 weeks
- Address any requested changes
- Once approved, a maintainer will merge your PR

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Imports**: Use absolute imports, group by standard library, third-party, local
- **Type hints**: Use type hints for all function signatures
- **Docstrings**: Use Google-style docstrings

**Example:**

```python
from typing import List, Optional

def process_video(
    project_id: str,
    scenes: List[dict],
    quality: Optional[str] = "high"
) -> dict:
    """Process video scenes and generate final output.

    Args:
        project_id: Unique identifier for the project
        scenes: List of scene dictionaries with metadata
        quality: Output quality level (default: "high")

    Returns:
        Dictionary containing video metadata and URL

    Raises:
        ValueError: If project_id is invalid
        ProcessingError: If video generation fails
    """
    # Implementation here
    pass
```

### Code Formatting

We use **Black** for code formatting:

```bash
# Format all Python files
black .

# Check without modifying
black --check .
```

### Linting

We use **Flake8** for linting:

```bash
# Run flake8
flake8 src/ tests/

# Configuration in .flake8 or setup.cfg
```

### Type Checking

We use **MyPy** for static type checking:

```bash
# Run mypy
mypy src/

# Configuration in mypy.ini or setup.cfg
```

### Frontend Standards

For Vue/TypeScript code:

- Follow [Vue 3 Style Guide](https://vuejs.org/style-guide/)
- Use **ESLint** and **Prettier** for formatting
- Use TypeScript for type safety

---

## Testing Guidelines

### Writing Tests

- Write tests for all new features and bug fixes
- Aim for >80% code coverage
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern

**Example:**

```python
import pytest
from src.agents.script_writer import ScriptWriter

def test_script_writer_generates_valid_script():
    """Test that ScriptWriter generates a valid script structure."""
    # Arrange
    writer = ScriptWriter()
    requirements = {
        "genre": "sci-fi",
        "duration": 30,
        "mood": "suspenseful"
    }

    # Act
    script = writer.generate_script(requirements)

    # Assert
    assert script is not None
    assert "scenes" in script
    assert len(script["scenes"]) > 0
    assert script["total_duration"] == 30
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_script_writer.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

### Test Organization

```
tests/
├── unit/              # Unit tests (fast, isolated)
│   ├── agents/
│   ├── infrastructure/
│   └── ...
├── integration/       # Integration tests (slower, with dependencies)
│   ├── test_event_bus.py
│   └── test_blackboard.py
└── e2e/              # End-to-end tests (full workflow)
    └── test_video_generation.py
```

---

## Documentation

### Code Documentation

- **Docstrings**: All public functions, classes, and modules must have docstrings
- **Comments**: Use comments to explain "why", not "what"
- **Type hints**: Use type hints for better IDE support

### Project Documentation

When adding new features, update:

- **README.md**: If it affects setup or usage
- **QUICKSTART.md**: If it affects getting started
- **API docs**: If you add/modify API endpoints
- **Architecture docs**: If you change system design

### Writing Good Documentation

- **Be clear and concise**
- **Use examples** to illustrate concepts
- **Keep it up-to-date** with code changes
- **Use proper formatting** (Markdown, code blocks, etc.)

---

## Project Structure

Understanding the project structure helps you contribute effectively:

```
videogen/
├── src/
│   ├── agents/              # AI agents
│   │   ├── cognitive/       # 14 specialized agents
│   │   └── interaction/     # User interaction agents
│   ├── infrastructure/      # Core infrastructure
│   │   ├── event_bus/       # Event system
│   │   ├── blackboard/      # Shared state
│   │   ├── orchestrator/    # Task scheduling
│   │   └── storage/         # File storage
│   ├── interfaces/          # API layer
│   │   └── api/
│   └── main.py             # Application entry point
├── tests/                   # Test suite
├── web-new/                # Vue frontend
├── scripts/                # Utility scripts
├── docs/                   # Documentation
└── docker-compose.yml      # Infrastructure setup
```

---

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check README.md and QUICKSTART.md first

---

## Recognition

Contributors will be recognized in:

- **CONTRIBUTORS.md**: List of all contributors
- **Release notes**: Mention of significant contributions
- **GitHub**: Contributor badge on your profile

---

## License

By contributing to VideoGen, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to VideoGen! 🎬✨**

Your contributions make this project better for everyone.
