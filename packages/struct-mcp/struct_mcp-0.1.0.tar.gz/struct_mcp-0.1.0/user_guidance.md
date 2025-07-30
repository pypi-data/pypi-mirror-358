# User Guidance: Testing struct-mcp Before PyPI Publication

This guide will help you test your struct-mcp package thoroughly before publishing to PyPI.

## Initial Setup

### 1. Create Development Environment

```bash
# Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package in development mode
uv pip install -e ".[dev]"
```

### 2. Verify Installation

```bash
# Check if the CLI is available
struct-mcp --help

# Should show available commands: serve, validate, convert, docs
```

## Testing the Package

### 1. Run the Test Suite

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=struct_mcp

# Run with verbose output
pytest -v
```

### 2. Test CLI Commands

```bash
# Test validation
struct-mcp validate examples/cheese_catalog.yaml

# Test conversion to different formats
struct-mcp convert examples/cheese_catalog.yaml --to pydantic
struct-mcp convert examples/cheese_catalog.yaml --to opensearch
struct-mcp convert examples/cheese_catalog.yaml --to avro

# Test documentation generation
struct-mcp docs examples/cheese_catalog.yaml
```

### 3. Test MCP Server (Basic)

```bash
# Start the MCP server (this will run until you stop it)
struct-mcp serve examples/cheese_catalog.yaml

# In another terminal, you can test if it's running
# (The server communicates via stdio, so direct testing is limited)
```

### 4. Test Python API

Create a test script (`test_api.py`) to verify the Python API:

```python
#!/usr/bin/env python3
from struct_mcp import StructMCP

# Load the cheese example
struct_mcp = StructMCP.from_yaml("examples/cheese_catalog.yaml")

# Test basic functionality
print("Structure names:", struct_mcp.get_structure_names())
print("Fields:", list(struct_mcp.get_fields("cheese_inventory").keys()))

# Test queries
nullable_fields = struct_mcp.find_fields_with_property("cheese_inventory", "nullable", True)
print("Nullable fields:", list(nullable_fields.keys()))

# Test question answering
question = "What does cheese_id represent?"
answer = struct_mcp.answer_question(question, "cheese_inventory")
print(f"Q: {question}")
print(f"A: {answer}")

# Test conversions
print("\n--- Pydantic Model ---")
print(struct_mcp.to_pydantic())

print("\n--- Documentation ---")
print(struct_mcp.generate_docs())
```

Run it with:
```bash
python test_api.py
```

## Pre-Publication Testing

### 1. Build the Package

```bash
# Build source and wheel distributions
uv build

# Check the built package
ls dist/
# Should see: struct_mcp-0.1.0.tar.gz and struct_mcp-0.1.0-py3-none-any.whl
```

### 2. Test Installation from Built Package

```bash
# Create a fresh virtual environment
uv venv test-env
source test-env/bin/activate

# Install from wheel
uv pip install dist/struct_mcp-0.1.0-py3-none-any.whl

# Test the installation
struct-mcp --help
struct-mcp validate examples/cheese_catalog.yaml

# Clean up
deactivate
rm -rf test-env
```

### 3. Test with TestPyPI (Recommended)

```bash
# First, create account at https://test.pypi.org/account/register/
# Generate API token at https://test.pypi.org/manage/account/token/

# Upload to TestPyPI
uv publish --repository testpypi dist/*
# You'll be prompted for your TestPyPI token

# Test installation from TestPyPI
uv venv testpypi-env
source testpypi-env/bin/activate
uv pip install --index-url https://test.pypi.org/simple/ struct-mcp

# Test the installed package
struct-mcp validate examples/cheese_catalog.yaml

# Clean up
deactivate
rm -rf testpypi-env
```

## Common Issues and Troubleshooting

### 1. Missing Dependencies

If you get import errors, check that all dependencies are properly listed in `pyproject.toml`:

```bash
# Check what's actually imported
python -c "from struct_mcp import StructMCP; print('Import successful')"
```

### 2. CLI Not Working

If `struct-mcp` command is not found:

```bash
# Check if it's in your PATH
which struct-mcp

# Try running directly
python -m struct_mcp --help
```

### 3. MCP Server Issues

The MCP server uses stdio for communication, so direct testing is limited. Issues might include:
- Import errors in the MCP library
- Async/await syntax issues
- JSON serialization problems

### 4. Converter Issues

If converters fail:
- Check optional dependencies are installed for converters
- Verify the YAML structure is being parsed correctly
- Test with simpler YAML files first

## Publishing to PyPI

Once all tests pass:

### 1. Final Build

```bash
# Clean previous builds
rm -rf dist/

# Build fresh
uv build
```

### 2. Publish to PyPI

```bash
# Create PyPI account at https://pypi.org/account/register/
# Generate API token at https://pypi.org/manage/account/token/

# Upload to PyPI
uv publish dist/*
```

### 3. Verify Publication

```bash
# Install from PyPI
uv venv verify-env
source verify-env/bin/activate
uv pip install struct-mcp

# Test installation
struct-mcp --help
struct-mcp validate examples/cheese_catalog.yaml

# Clean up
deactivate
rm -rf verify-env
```

## Post-Publication

### 1. Update Documentation

- Update README.md with installation instructions
- Consider adding examples to the repository
- Update version number for next release

### 2. Monitor Issues

- Check PyPI download statistics
- Monitor GitHub issues (if you create a repository)
- Gather user feedback

## Quick Test Checklist

Before publishing, ensure:

- [ ] All tests pass: `pytest`
- [ ] CLI commands work: `struct-mcp --help`
- [ ] Example files validate: `struct-mcp validate examples/cheese_catalog.yaml`
- [ ] Conversions work: `struct-mcp convert examples/cheese_catalog.yaml --to pydantic`
- [ ] Package builds: `uv build`
- [ ] Built package installs: `uv pip install dist/struct_mcp-0.1.0-py3-none-any.whl`
- [ ] TestPyPI upload works (optional but recommended)
- [ ] Python API works: Test with `test_api.py` script above

Good luck with your PyPI publication!
