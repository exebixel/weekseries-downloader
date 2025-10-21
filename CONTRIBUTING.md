# 🤝 Contributing to WeekSeries Downloader

Thank you for considering contributing to this project!

## 🚀 Development Environment Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/weekseries-downloader.git
cd weekseries-downloader

# Add the original repository as upstream
git remote add upstream https://github.com/ORIGINAL_USERNAME/weekseries-downloader.git
```

### 2. Poetry Configuration

```bash
# Configure Poetry to use local .venv
poetry config virtualenvs.in-project true

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### 3. Installation Verification

```bash
# Test the command
poetry run weekseries-dl --help

# Run tests (when available)
pytest

# Check formatting
black --check weekseries_downloader/
flake8 weekseries_downloader/
```

## 📝 Contribution Process

### 1. Create a Branch

```bash
# Always create a new branch for your changes
git checkout -b feature/new-feature
# or
git checkout -b fix/bug-fix
# or
git checkout -b docs/documentation-improvement
```

### 2. Make Your Changes

- Keep code clean and well documented
- Follow existing code conventions
- Add tests if necessary
- Update documentation if relevant

### 3. Test Your Changes

```bash
# Format code
black weekseries_downloader/

# Check linting
flake8 weekseries_downloader/

# Run tests
pytest

# Test CLI command
poetry run weekseries-dl --help
```

### 4. Commit and Push

```bash
# Add modified files
git add .

# Commit with descriptive message
git commit -m "✨ feat: add new feature X

- Implement functionality Y
- Fix issue Z
- Update documentation"

# Push to your fork
git push origin feature/new-feature
```

### 5. Open a Pull Request

- Go to GitHub and open a Pull Request
- Clearly describe your changes
- Reference related issues if any

## 🎯 Types of Contributions

### 🐛 Bug Fixes
- Report bugs via Issues
- Include steps to reproduce
- Provide system information

### ✨ New Features
- Discuss the feature in an Issue first
- Keep scope focused
- Add tests and documentation

### 📚 Documentation
- Improve README
- Add examples
- Fix typos

### 🧹 Refactoring
- Improve code structure
- Optimize performance
- Maintain compatibility

## 📋 Conventions

### Commit Messages

Use the format:
```
<type>: <description>

<optional body>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Refactoring
- `test`: Tests
- `chore`: Maintenance tasks

### Code

- Use type hints when possible
- Docstrings for public functions
- Descriptive variable names
- Keep functions small and focused

### Tests

- Test critical functionality
- Use descriptive test names
- Include error cases

## 🏷️ Versioning

We follow [Semantic Versioning](https://semver.org/):

- `MAJOR`: Incompatible changes
- `MINOR`: Backwards-compatible new features
- `PATCH`: Bug fixes

## 📞 Support

- Open Issues for bugs and suggestions
- Use Discussions for general questions
- Be respectful and constructive

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.
