"""
Tests for CLI functions with all supported formats.
"""

import pytest
import argparse
import tempfile
from pathlib import Path
from unittest.mock import patch
from io import StringIO

from struct_mcp.cli import validate_command, convert_command, docs_command


def test_validate_command_with_all_formats():
    """Test that validate command works with all supported formats."""
    examples_dir = Path(__file__).parent.parent / "examples"

    example_files = [
        "cheese_catalog.yaml",
        "cheese_catalog.json",
        "cheese_catalog_opensearch.json",
        "cheese_catalog_avro.json",
        "cheese_catalog_pydantic.py",
        "cheese_catalog.proto",
    ]

    for filename in example_files:
        file_path = examples_dir / filename

        if file_path.exists():
            # Create mock args
            args = argparse.Namespace(input_file=str(file_path))

            # Capture stdout
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                # Should not raise an exception
                validate_command(args)

                # Check that it printed a success message
                output = mock_stdout.getvalue()
                assert "✓" in output, f"Validation didn't show success for {filename}"
                assert (
                    str(file_path) in output
                ), f"Output didn't mention filename for {filename}"

                print(f"✓ Validate command succeeded for {filename}")


def test_validate_command_with_nonexistent_file():
    """Test that validate command handles non-existent files properly."""
    args = argparse.Namespace(input_file="nonexistent.yaml")

    with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
        with pytest.raises(SystemExit) as exc_info:
            validate_command(args)

        # Should exit with code 1
        assert exc_info.value.code == 1

        # Should print error message
        error_output = mock_stderr.getvalue()
        assert "does not exist" in error_output


def test_convert_command_with_formats():
    """Test that convert command works for supported conversions."""
    examples_dir = Path(__file__).parent.parent / "examples"
    yaml_file = examples_dir / "cheese_catalog.yaml"

    if yaml_file.exists():
        conversions = [
            "opensearch",
            "avro",
            "pydantic",
            "protobuf",
        ]

        for target_format in conversions:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=f".{target_format}", delete=False
            ) as temp_file:
                temp_path = temp_file.name

            try:
                # Create mock args
                args = argparse.Namespace(
                    input_file=str(yaml_file), to=target_format, output=temp_path
                )

                # Capture stdout
                with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                    convert_command(args)

                    # Check that it printed success message
                    output = mock_stdout.getvalue()
                    assert "Converted to" in output and target_format in output

                    # Check that output file exists and has content
                    output_path = Path(temp_path)
                    assert (
                        output_path.exists()
                    ), f"Output file not created for {target_format}"
                    assert (
                        output_path.stat().st_size > 0
                    ), f"Output file empty for {target_format}"

                    print(f"✓ Convert to {target_format} succeeded")

            finally:
                # Clean up
                Path(temp_path).unlink(missing_ok=True)


def test_convert_command_to_stdout():
    """Test that convert command works with stdout output."""
    examples_dir = Path(__file__).parent.parent / "examples"
    yaml_file = examples_dir / "cheese_catalog.yaml"

    if yaml_file.exists():
        args = argparse.Namespace(
            input_file=str(yaml_file), to="pydantic", output=None  # stdout
        )

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            convert_command(args)

            # Check that it printed the converted content
            output = mock_stdout.getvalue()
            assert len(output) > 0, "No output to stdout"
            assert (
                "class" in output.lower() or "basemodel" in output.lower()
            ), "Doesn't look like Pydantic output"

            print("✓ Convert to stdout succeeded")


def test_docs_command_with_formats():
    """Test that docs command works with supported formats."""
    examples_dir = Path(__file__).parent.parent / "examples"

    example_files = [
        "cheese_catalog.yaml",
        "cheese_catalog.json",
        "cheese_catalog_pydantic.py",
    ]

    for filename in example_files:
        file_path = examples_dir / filename

        if file_path.exists():
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".md", delete=False
            ) as temp_file:
                temp_path = temp_file.name

            try:
                # Create mock args
                args = argparse.Namespace(input_file=str(file_path), output=temp_path)

                # Capture stdout
                with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                    docs_command(args)

                    # Check that it printed success message
                    output = mock_stdout.getvalue()
                    assert "Documentation saved" in output

                    # Check that output file exists and has content
                    output_path = Path(temp_path)
                    assert output_path.exists(), f"Docs file not created for {filename}"
                    assert (
                        output_path.stat().st_size > 0
                    ), f"Docs file empty for {filename}"

                    # Check that it looks like markdown
                    content = output_path.read_text()
                    assert "#" in content, "Doesn't look like markdown (no headers)"

                    print(f"✓ Docs generation succeeded for {filename}")

            finally:
                # Clean up
                Path(temp_path).unlink(missing_ok=True)


def test_docs_command_to_stdout():
    """Test that docs command works with stdout output."""
    examples_dir = Path(__file__).parent.parent / "examples"
    yaml_file = examples_dir / "cheese_catalog.yaml"

    if yaml_file.exists():
        args = argparse.Namespace(input_file=str(yaml_file), output=None)  # stdout

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            docs_command(args)

            # Check that it printed the documentation
            output = mock_stdout.getvalue()
            assert len(output) > 0, "No output to stdout"
            assert "#" in output, "Doesn't look like markdown documentation"

            print("✓ Docs to stdout succeeded")


def test_cli_error_handling():
    """Test that CLI functions handle errors gracefully."""

    # Test validate with malformed file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as temp_file:
        temp_file.write("invalid: yaml: content: [")
        temp_path = temp_file.name

    try:
        args = argparse.Namespace(input_file=temp_path)

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            with pytest.raises(SystemExit) as exc_info:
                validate_command(args)

            # Should exit with code 1
            assert exc_info.value.code == 1

            # Should print error message
            error_output = mock_stderr.getvalue()
            assert "invalid" in error_output.lower()

    finally:
        Path(temp_path).unlink()

    # Test convert with unsupported format
    examples_dir = Path(__file__).parent.parent / "examples"
    yaml_file = examples_dir / "cheese_catalog.yaml"

    if yaml_file.exists():
        args = argparse.Namespace(
            input_file=str(yaml_file), to="unsupported_format", output=None
        )

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            with pytest.raises(SystemExit) as exc_info:
                convert_command(args)

            # Should exit with code 1
            assert exc_info.value.code == 1

            # Should print error message
            error_output = mock_stderr.getvalue()
            assert "Unsupported format" in error_output

    print("✓ CLI error handling works correctly")
