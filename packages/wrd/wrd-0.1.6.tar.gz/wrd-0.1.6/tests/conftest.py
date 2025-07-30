"""Configuration file for pytest."""

import os
import sys
from pathlib import Path
from typing import Generator, Any, Dict

import pytest

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> Generator[None, None, None]:
    """Set up the test environment."""
    # Set up any test environment variables here
    os.environ["WRD_DEBUG"] = "1"

    # Yield to run the tests
    yield

    # Clean up after tests if needed


@pytest.fixture
def tmp_project_dir(tmp_path):
    """Create a temporary project directory for testing."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def template_manager():
    """Create a template manager instance for testing."""
    from wrd.template_manager import TemplateManager

    return TemplateManager()


@pytest.fixture
def default_template_data() -> Dict[str, Any]:
    """Return default template data for testing."""
    return {
        "project_name": "test_project",
        "author": "Test User",
        "email": "test@example.com",
        "description": "A test project",
        "license": "MIT",
        "version": "0.1.0",
    }
