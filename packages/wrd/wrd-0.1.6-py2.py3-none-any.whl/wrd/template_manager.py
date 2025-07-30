"""Template manager for WRD."""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
import jinja2
import importlib.resources as pkg_resources
from . import templates


class TemplateManager:
    """Manages project templates for different languages and project types."""

    def __init__(self):
        self.templates_dir = Path(pkg_resources.files(templates))
        self.available_templates = self._discover_templates()

    def _discover_templates(self) -> Dict[str, Dict[str, Any]]:
        """Discover all available templates in the templates directory."""
        templates = {}

        if not self.templates_dir.exists():
            return {}

        for template_dir in self.templates_dir.iterdir():
            if template_dir.is_dir() and (template_dir / 'project.yml').exists():
                try:
                    with open(template_dir / 'project.yml', 'r') as f:
                        config = yaml.safe_load(f)
                        templates[config['name']] = {
                            'config': config,
                            'path': template_dir,
                        }
                except (yaml.YAMLError, KeyError) as e:
                    print(f"Error loading template {template_dir.name}: {e}")

        return templates

    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a template by name."""
        return self.available_templates.get(name)

    def list_templates(self) -> List[str]:
        """List all available template names."""
        return list(self.available_templates.keys())

    def create_project(
        self,
        template_name: str,
        project_path: Path,
        context: Dict[str, Any],
        overwrite: bool = False,
    ) -> bool:
        """Create a new project from a template.

        Args:
            template_name: Name of the template to use
            project_path: Path where the project should be created
            context: Dictionary with template variables
            overwrite: Whether to overwrite existing files

        Returns:
            bool: True if project was created successfully

        Raises:
            ValueError: If template is not found
            FileExistsError: If output directory exists and overwrite is False
        """
        template = self.get_template(template_name)
        if not template:
            error_msg = f"Template '{template_name}' not found"
            raise ValueError(error_msg)

        project_path = project_path.absolute()

        # Check if directory exists and handle overwrite
        if project_path.exists():
            if not overwrite:
                error_msg = f"Directory {project_path} already exists. Use --overwrite to ignore."
                raise FileExistsError(error_msg)
        else:
            project_path.mkdir(parents=True, exist_ok=True)

        # Process template files
        config = template['config']
        template_dir = template['path']

        # Create directories first
        for dir_path in config.get('directories', []):
            rendered_dir = self._render_template(dir_path, context)
            full_dir = project_path / rendered_dir
            full_dir.mkdir(parents=True, exist_ok=True)

        # Create files
        for file_spec in config.get('files', []):
            if not isinstance(file_spec, dict):
                continue

            # Handle both 'path' and 'source' keys for file path
            file_path = file_spec.get('path') or file_spec.get('source')
            if not file_path:
                continue

            file_content = file_spec.get('content')
            template_file = file_spec.get('template')

            try:
                # Render the file path
                file_path = self._render_template(file_path, context)
                dest_path = project_path / file_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                if file_content is not None:
                    # Use inline content
                    rendered = self._render_template(file_content, context)
                    dest_path.write_text(rendered)
                elif template_file:
                    # Use template file
                    template_path = template_dir / template_file
                    if template_path.exists():
                        template_content = template_path.read_text()
                        rendered = self._render_template(template_content, context)
                        dest_path.write_text(rendered)
                    else:
                        # Create empty file as fallback
                        dest_path.touch()
                else:
                    # Create empty file
                    dest_path.touch()
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                raise

        # Run post-create commands
        for cmd in config.get('post_create_commands', []):
            cmd = self._render_template(cmd, context)
            os.system(f"cd {project_path} && {cmd}")

        return True

    def _render_template(self, template_str: str, context: Dict[str, Any]) -> str:
        """Render a template string with the given context."""
        return jinja2.Template(template_str).render(**context)

    def get_template_variables(self, template_name: str) -> Dict[str, Any]:
        """Get the required variables for a template."""
        template = self.get_template(template_name)
        if not template:
            return {}

        # Extract variables from template files
        variables = set()

        # Check config files
        for file_spec in template['config'].get('files', []):
            if isinstance(file_spec, dict):
                content = file_spec.get('content', '')
                template_file = file_spec.get('template')

                if template_file:
                    template_path = template['path'] / template_file
                    if template_path.exists():
                        content = template_path.read_text()

                # Simple variable extraction ({{ variable }})
                import re

                variables.update(re.findall(r'\{\{\s*([^\s}]+)\s*\}\}', content))

        return {var: "" for var in variables}


def get_template_manager() -> TemplateManager:
    """Get a template manager instance."""
    return TemplateManager()
