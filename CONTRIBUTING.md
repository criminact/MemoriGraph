# Contributing to MemoriGraph

Thank you for your interest in contributing to MemoriGraph! We welcome contributions from the community and are grateful for your help in making this project better.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Environment details (OS, Python version, Neo4j version, etc.)
- Relevant error messages or logs

### Suggesting Features

We'd love to hear your ideas! Open an issue with:
- A clear description of the feature
- Use cases and examples
- Potential implementation approach (if you have one)

### Code Contributions

1. **Fork the repository** and clone it locally
2. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following our coding standards:
   - Follow PEP 8 style guidelines
   - Add docstrings to new functions/classes
   - Write clear, descriptive commit messages
   - Add tests if applicable
4. **Test your changes**:
   ```bash
   # Run the application locally
   python run.py
   
   # Test with Docker
   docker-compose up -d
   ```
5. **Update documentation** if needed
6. **Commit your changes**:
   ```bash
   git commit -m "Add: descriptive commit message"
   ```
7. **Push to your fork** and open a Pull Request

### Pull Request Process

1. Ensure your code follows the project's style guidelines
2. Update the CHANGELOG.md with your changes
3. Make sure all tests pass (if applicable)
4. Request review from maintainers
5. Address any feedback or requested changes

### Code Style

- Use Python 3.12+ features where appropriate
- Follow PEP 8 style guidelines
- Use type hints where possible
- Add docstrings to public functions and classes
- Keep functions focused and single-purpose

### Project Structure

```
.
├── app/              # FastAPI application
├── api/              # API routes
├── models/           # Pydantic schemas
├── services/         # Business logic
├── utils/            # Utilities and helpers
└── tests/            # Tests (if applicable)
```

### Questions?

Feel free to open an issue with the `question` label or start a discussion in the GitHub Discussions section.

Thank you for contributing to MemoriGraph! 🚀

