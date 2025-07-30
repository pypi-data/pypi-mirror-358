"""Unit tests for the TemplateManager class."""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import yaml

from wrd.template_manager import TemplateManager


class TestTemplateManager:
    """Test cases for the TemplateManager class."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up test fixtures."""
        self.temp_dir = tmp_path
        self.templates_dir = self.temp_dir / "templates"
        self.templates_dir.mkdir()
        
        # Create a test template
        self.test_template = self.templates_dir / "python-basic"
        self.test_template.mkdir()
        
        # Create a project.yml for the test template
        self.template_config = {
            "name": "python-basic",
            "description": "Basic Python project template",
            "author": "WRD Team",
            "version": "1.0.0",
            "variables": [
                {"name": "project_name", "description": "Name of the project"},
                {"name": "author", "description": "Author name"},
            ],
            "files": [
                {
                    "source": "{{project_name}}/README.md",
                    "content": "# {{project_name}}\n\nCreated by {{author}}"
                },
                {
                    "source": "{{project_name}}/setup.py",
                    "content": "from setuptools import setup\n\nsetup(\n    name='{{project_name}}',\n    version='0.1.0',\n    author='{{author}}'\n)"
                }
            ]
        }
        
        with open(self.test_template / "project.yml", "w") as f:
            yaml.dump(self.template_config, f)
        
        # Create a test file in the template
        (self.test_template / "test_file.txt").write_text("Test content")
        
        # Patch pkg_resources to use our test templates directory
        self.patcher = patch('wrd.template_manager.pkg_resources.files')
        self.mock_files = self.patcher.start()
        self.mock_files.return_value = self.templates_dir
        
        yield
        
        # Cleanup
        self.patcher.stop()
    
    def test_discover_templates(self):
        """Test that templates are discovered correctly."""
        manager = TemplateManager()
        templates = manager.available_templates
        
        assert "python-basic" in templates
        assert templates["python-basic"]["config"]["name"] == "python-basic"
        assert templates["python-basic"]["path"] == self.test_template
    
    def test_get_template(self):
        """Test getting a template by name."""
        manager = TemplateManager()
        template = manager.get_template("python-basic")
        
        assert template is not None
        assert template["config"]["name"] == "python-basic"
        
        # Test non-existent template
        assert manager.get_template("nonexistent") is None
    
    def test_list_templates(self):
        """Test listing available templates."""
        manager = TemplateManager()
        templates = manager.list_templates()
        
        assert isinstance(templates, list)
        assert "python-basic" in templates
    
    def test_create_project(self):
        """Test creating a project from a template."""
        manager = TemplateManager()
        project_path = self.temp_dir / "output" / "test-project"
        project_path.parent.mkdir(parents=True, exist_ok=True)

        context = {
            "project_name": "test-project",
            "author": "Test User"
        }

        result = manager.create_project(
            template_name="python-basic",
            project_path=project_path,
            context=context,
            overwrite=False
        )

        # Verify the project directory was created
        assert project_path.exists()
        assert (project_path / "README.md").exists()
        
        # Verify the template files were created
        assert (project_path / "src").exists()
        assert (project_path / "tests").exists()
        assert (project_path / "setup.py").exists()
        
        # Verify the context was applied to templates
        readme = (project_path / "README.md").read_text()
        assert "test-project" in readme
        assert "Test User" in readme
    
    def test_create_project_invalid_template(self):
        """Test creating a project with an invalid template name."""
        manager = TemplateManager()
        project_path = self.temp_dir / "output" / "test-project"
        project_path.parent.mkdir(parents=True, exist_ok=True)

        with pytest.raises(ValueError, match="Template 'nonexistent' not found"):
            manager.create_project(
                template_name="nonexistent",
                project_path=project_path,
                context={"project_name": "test"}
            )
    
    def test_create_project_existing_output(self):
        """Test creating a project when output directory exists."""
        manager = TemplateManager()
        project_path = self.temp_dir / "output" / "test-project"
        project_path.parent.mkdir(parents=True, exist_ok=True)
        project_path.mkdir()  # Create the project directory to cause conflict

        # Test with overwrite=False (should raise FileExistsError)
        with pytest.raises(FileExistsError):
            manager.create_project(
                template_name="python-basic",
                project_path=project_path,
                context={"project_name": "test-project"},
                overwrite=False
            )
            
        # Test with overwrite=True (should work)
        result = manager.create_project(
            template_name="python-basic",
            project_path=project_path,
            context={"project_name": "test-project"},
            overwrite=True
        )
        assert result is True  # Should complete successfully with overwrite
