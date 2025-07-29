# Contributing to Universal Document Converter MCP Server

We welcome contributions to the Universal Document Converter MCP Server! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Development Workflow](#development-workflow)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please be respectful and constructive in all interactions.

### Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 18.0 or higher
- Git
- Basic understanding of MCP (Model Context Protocol)
- Familiarity with async/await patterns in Python

### Development Setup

1. **Fork and Clone the Repository**

```bash
git clone https://github.com/your-username/universal-document-mcp.git
cd universal-document-mcp
```

2. **Set Up Python Development Environment**

```bash
# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install in development mode
pip install -e .[dev]

# Install Playwright browsers
python -m playwright install chromium
```

3. **Set Up Node.js Development Environment**

```bash
# Install Node.js dependencies
npm install

# Install development dependencies
npm install --dev
```

4. **Verify Setup**

```bash
# Run tests
pytest
npm test

# Check code style
black --check .
flake8 .
```

## Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

- **Bug fixes**: Fix issues in existing functionality
- **Feature additions**: Add new features or capabilities
- **Documentation improvements**: Enhance or clarify documentation
- **Performance optimizations**: Improve speed or resource usage
- **Test coverage**: Add or improve tests
- **Code quality**: Refactoring and code cleanup

### Before You Start

1. **Check existing issues** to see if your contribution is already being worked on
2. **Create an issue** to discuss major changes before implementing them
3. **Review the roadmap** to understand project direction
4. **Read the documentation** to understand the current architecture

### Coding Standards

#### Python Code Style

- Follow PEP 8 style guidelines
- Use Black for code formatting
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Use meaningful variable and function names

Example:
```python
async def convert_document(
    markdown_file: str, 
    optimize_diagrams: bool = True
) -> Dict[str, Any]:
    """
    Convert a markdown file to PDF with optional diagram optimization.
    
    Args:
        markdown_file: Path to the markdown file to convert
        optimize_diagrams: Whether to optimize Mermaid diagrams
        
    Returns:
        Dictionary containing conversion results and metadata
    """
    # Implementation here
    pass
```

#### JavaScript Code Style

- Use ES6+ features
- Follow ESLint configuration
- Use async/await for asynchronous operations
- Write JSDoc comments for functions
- Use meaningful variable names

#### General Guidelines

- Write clear, self-documenting code
- Add comments for complex logic
- Handle errors gracefully
- Log important operations
- Validate inputs
- Use consistent naming conventions

### Testing

#### Python Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=universal_document_mcp

# Run specific test file
pytest tests/test_converter.py

# Run with verbose output
pytest -v
```

#### JavaScript Tests

```bash
# Run Node.js tests
npm test

# Run with coverage
npm run test:coverage
```

#### Test Guidelines

- Write tests for all new functionality
- Maintain or improve test coverage
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies
- Keep tests fast and isolated

### Documentation

- Update README.md for user-facing changes
- Update INSTALL.md for installation changes
- Add docstrings to new functions and classes
- Update configuration examples
- Add usage examples for new features

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**
2. **Update documentation** as needed
3. **Add tests** for new functionality
4. **Follow coding standards**
5. **Update CHANGELOG.md** with your changes

### Pull Request Template

When creating a pull request, please include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

### Review Process

1. **Automated checks** must pass (tests, linting, etc.)
2. **Code review** by maintainers
3. **Testing** on different platforms if needed
4. **Documentation review** for user-facing changes
5. **Approval** and merge by maintainers

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, etc.)
- **Error messages** or logs
- **Sample files** if relevant

### Feature Requests

For feature requests, please include:

- **Clear description** of the proposed feature
- **Use case** and motivation
- **Proposed implementation** (if you have ideas)
- **Alternatives considered**
- **Additional context**

### Issue Labels

We use labels to categorize issues:

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested

## Development Workflow

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add AI-powered layout optimization
fix: resolve Mermaid diagram rendering issue
docs: update installation instructions
refactor: simplify configuration loading
```

### Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release branch
4. Test thoroughly
5. Create GitHub release
6. Publish to PyPI and npm

## Getting Help

If you need help with development:

- **GitHub Discussions**: Ask questions and share ideas
- **GitHub Issues**: Report bugs or request features
- **Documentation**: Read the project wiki
- **Code Review**: Learn from existing pull requests

## Recognition

Contributors will be recognized in:

- CHANGELOG.md for their contributions
- GitHub contributors list
- Release notes for significant contributions

Thank you for contributing to the Universal Document Converter MCP Server!
