"""Unit tests for the CLI module."""

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, call

import pytest
from typer.testing import CliRunner

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from wrd.cli import WRDShell, main as cli_main


class TestCLI:
    """Test cases for the CLI module."""

    @pytest.fixture
    def runner(self):
        """Fixture for CLI runner."""
        return CliRunner()
    
    @pytest.fixture
    def mock_template_manager(self):
        """Fixture for a mock TemplateManager."""
        with patch('wrd.cli.TemplateManager') as mock:
            yield mock
    
    def test_cli_help(self, runner):
        """Test the CLI help command."""
        # Since we don't have a direct app object, we'll test the main function
        with patch('sys.argv', ['wrd', '--help']):
            with patch('sys.exit') as mock_exit:
                cli_main()
                # The help should be printed to stdout, but we can't easily capture it here
                # Just verify sys.exit was called (which happens after help is printed)
                mock_exit.assert_called_once()
    
    def test_version_command(self, capsys):
        """Test the version command."""
        from wrd import __version__
        with patch('sys.argv', ['wrd', '--version']):
            with pytest.raises(SystemExit):
                cli_main()
            captured = capsys.readouterr()
            assert f"WRD version: {__version__}" in captured.out
    
    @patch('builtins.input', side_effect=['my-project', 'Test User', 'test@example.com'])
    @patch('wrd.cli.WRDShell._init_python_project')
    def test_init_command(self, mock_init_project, mock_input, mock_template_manager):
        """Test the init command."""
        # Setup mock
        mock_instance = mock_template_manager.return_value
        mock_instance.list_templates.return_value = ["python-basic"]
        
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_path = temp_path / "my-project"
            
            # Create a WRDShell instance
            shell = WRDShell()
            
            # Run the init_project method
            shell.init_project(str(project_path))
            
            # Verify the _init_python_project method was called with the correct arguments
            mock_init_project.assert_called_once()
            args, kwargs = mock_init_project.call_args
            assert str(args[0]) == str(project_path)  # project_path
            assert args[1] == "my-project"  # name
            assert "A new project" in args[2]  # description (default contains this text)
    
    @patch('wrd.cli.WRDShell')
    def test_shell_command(self, mock_shell_class):
        """Test the shell command."""
        # Setup mock
        mock_shell_instance = MagicMock()
        mock_shell_class.return_value = mock_shell_instance
        
        # Call the main function with shell command
        with patch('sys.argv', ['wrd', 'shell']):
            cli_main()
        
        # Verify WRDShell was instantiated and cmdloop was called
        mock_shell_class.assert_called_once()
        mock_shell_instance.cmdloop.assert_called_once()
    
    def test_list_templates(self, capsys):
        """Test listing templates."""
        # Create a WRDShell instance
        shell = WRDShell()
        
        # Mock the template manager
        with patch('wrd.cli.TemplateManager') as mock_tm_class:
            mock_tm = mock_tm_class.return_value
            mock_tm.list_templates.return_value = ["python-basic", "nodejs-basic"]
            
            # Call the method
            shell.do_list_templates("")
            
            # Capture output
            captured = capsys.readouterr()
            
            # Verify the output
            assert "Available templates:" in captured.out
            assert "- python-basic" in captured.out
            assert "- nodejs-basic" in captured.out
            mock_tm.list_templates.assert_called_once()


class TestWRDShell:
    """Test cases for the WRDShell class."""
    
    @pytest.fixture
    def shell(self):
        """Fixture for WRDShell instance."""
        return WRDShell()
    
    def test_do_help(self, shell, capsys):
        """Test the help command."""
        # Test general help
        shell.do_help("")
        captured = capsys.readouterr()
        assert "Documented commands" in captured.out
        
        # Test help for specific command
        shell.do_help("init")
        captured = capsys.readouterr()
        assert "Initialize a new project" in captured.out
    
    def test_do_exit(self, shell):
        """Test the exit command."""
        assert shell.do_exit("") is True
    
    def test_do_EOF(self, shell):
        """Test the EOF command."""
        assert shell.do_EOF("") is True
    
    @patch('builtins.input', side_effect=['Test Project', 'test@example.com', 'A test project'])
    def test_do_init(self, mock_input, shell, tmp_path):
        """Test the init command."""
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_path = temp_path / "my-project"
            
            # Call the init_project method
            shell.init_project(str(project_path))
            
            # Verify project directory was created
            assert project_path.exists()
            
            # Verify essential files were created
            assert (project_path / "README.md").exists()
            assert (project_path / "setup.py").exists()
            assert (project_path / "src").exists()
            assert (project_path / "tests").exists()
    
    @patch('wrd.cli.TemplateManager')
    def test_do_list_templates(self, mock_tm_class, shell, capsys):
        """Test the list-templates command."""
        # Setup mock
        mock_tm = mock_tm_class.return_value
        mock_tm.list_templates.return_value = ["template1", "template2"]
        
        # Call the method
        shell.do_list_templates("")
        
        # Verify output
        captured = capsys.readouterr()
        assert "Available templates:" in captured.out
        assert "- template1" in captured.out
        assert "- template2" in captured.out
        mock_tm.list_templates.assert_called_once()
    
    @patch('wrd.cli.TemplateManager')
    def test_do_use_template(self, mock_tm_class, shell, tmp_path, capsys):
        """Test the use-template command."""
        # Setup mock
        mock_tm = mock_tm_class.return_value
        mock_tm.list_templates.return_value = ["python-basic"]
        mock_tm.create_project.return_value = 0
        
        # Call the method
        shell.do_use_template("python-basic my-project")
        
        # Verify template manager was called correctly
        mock_tm.create_project.assert_called_once()
        call_args = mock_tm.create_project.call_args[1]
        assert call_args["template_name"] == "python-basic"
        assert call_args["context"]["project_name"] == "my-project"
        
        # Verify success message
        captured = capsys.readouterr()
        assert "Project created successfully" in captured.out
    
    def test_complete_use_template(self, shell):
        """Test tab completion for the use-template command."""
        # Mock the template manager
        with patch('wrd.cli.TemplateManager') as mock_tm_class:
            mock_tm = mock_tm_class.return_value
            mock_tm.list_templates.return_value = ["python-basic", "nodejs-basic"]
            
            # Test template name completion
            completions = shell.complete_use_template("", "use-template ".split(), 1)
            assert set(completions) == {"python-basic", "nodejs-basic"}
            
            # Test no completion after template name
            assert shell.complete_use_template("python-basic ", "use-template python-basic ".split(), 2) == []
