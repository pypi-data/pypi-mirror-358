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
                            'path': template_dir
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
        overwrite: bool = False
    ) -> bool:
        """Create a new project from a template.
        
        Args:
            template_name: Name of the template to use
            project_path: Path where the project should be created
            context: Dictionary with template variables
            overwrite: Whether to overwrite existing files
            
        Returns:
            bool: True if project was created successfully, False otherwise
        """
        template = self.get_template(template_name)
        if not template:
            print(f"Error: Template '{template_name}' not found")
            return False
        
        project_path = project_path.absolute()
        
        # Create project directory if it doesn't exist
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Check if directory is empty or overwrite is allowed
        if any(project_path.iterdir()) and not overwrite:
            print(f"Error: Directory {project_path} is not empty. Use --overwrite to ignore.")
            return False
        
        # Process template files
        config = template['config']
        template_dir = template['path']
        
        # Create directories
        for dir_path in config.get('directories', []):
            dir_path = project_path / self._render_template(dir_path, context)
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create files
        for file_spec in config.get('files', []):
            if isinstance(file_spec, dict):
                file_path = file_spec['path']
                content = file_spec.get('content')
                template_file = file_spec.get('template')
            else:
                file_path = file_spec
                content = None
                template_file = None
            
            # Render the file path
            file_path = self._render_template(file_path, context)
            dest_path = project_path / file_path
            
            # Create parent directories if they don't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content
            if content is not None:
                # Use direct content
                dest_path.write_text(self._render_template(content, context))
            elif template_file is not None:
                # Use template file
                template_path = template_dir / template_file
                if template_path.exists():
                    template_content = template_path.read_text()
                    rendered = self._render_template(template_content, context)
                    dest_path.write_text(rendered)
            else:
                # Create empty file
                dest_path.touch()
        
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
