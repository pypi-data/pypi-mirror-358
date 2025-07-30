"""Integration tests for the WRD CLI."""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from unittest.mock import patch

import pytest

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from wrd.cli import WRDShell, main as cli_main
from wrd.template_manager import TemplateManager


class TestCLIIntegration:
    """Integration tests for the WRD CLI."""
    
    @pytest.fixture
    def shell(self):
        """Fixture for WRDShell instance."""
        return WRDShell()
    
    def test_init_command_integration(self, shell, tmp_path):
        """Test the init command with a real template manager."""
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_path = temp_path / "my-project"
            
            # Mock user input
            with patch('builtins.input', side_effect=['Test Project', 'test@example.com', 'A test project']):
                # Call the init_project method
                shell.init_project(str(project_path))
            
            # Verify project structure
            assert project_path.exists()
            assert (project_path / "README.md").exists()
            assert (project_path / "setup.py").exists()
            assert (project_path / "src").exists()
            assert (project_path / "tests").exists()
    
    @patch('builtins.input', side_effect=['Test Project', 'test@example.com', 'A test project'])
    def test_use_template_command(self, mock_input, shell, tmp_path, capsys):
        """Test the use-template command with a real template manager."""
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_path = temp_path / "test-project"
            
            # Call the use_template method
            shell.use_template(str(project_path), "python-basic")
            
            # Verify project structure
            assert project_path.exists()
            assert (project_path / "README.md").exists()
            assert (project_path / "setup.py").exists()
            assert (project_path / "src").exists()
            assert (project_path / "tests").exists()
    
    def test_list_templates_integration(self, shell, capsys):
        """Test the list-templates command with a real template manager."""
        # Call the list_templates method
        shell.list_templates()
        
        # Verify output
        captured = capsys.readouterr()
        assert "Available templates:" in captured.out
        assert "python-basic" in captured.out


class TestTemplateManagerIntegration:
    """Integration tests for the TemplateManager class."""
    
    def test_create_project_integration(self, tmp_path):
        """Test creating a project from a template."""
        # Setup
        manager = TemplateManager()
        project_path = tmp_path / "test-project"
        
        # Get the first available template
        templates = manager.list_templates()
        assert templates, "No templates found for testing"
        template_name = templates[0]
        
        # Create project
        context = {
            "project_name": "test-project",
            "author": "Test User",
            "email": "test@example.com",
            "description": "A test project",
            "license": "MIT",
            "version": "0.1.0",
        }
        
        result = manager.create_project(
            template_name=template_name,
            project_path=project_path,
            context=context,
            overwrite=False
        )
        
        # Verify
        assert result is True
        assert project_path.exists()
        assert (project_path / "README.md").exists()
    
    def test_get_template_integration(self):
        """Test getting a template by name."""
        manager = TemplateManager()
        
        # Get the first available template
        templates = manager.list_templates()
        assert templates, "No templates found for testing"
        template_name = templates[0]
        
        # Get template
        template = manager.get_template(template_name)
        assert template is not None
        assert "config" in template
        assert "path" in template
        assert template["config"]["name"] == template_name
