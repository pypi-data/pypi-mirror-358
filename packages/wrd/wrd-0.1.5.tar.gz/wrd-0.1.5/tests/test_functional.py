"""Functional tests for the WRD package."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class TestWRDFunctional(unittest.TestCase):
    """Functional test cases for the WRD package."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

        # Create a test project directory
        self.project_name = "test_project"
        self.project_path = Path(self.test_dir) / self.project_name
        self.project_path.mkdir(exist_ok=True)

        # Mock the user's home directory
        self.patcher = patch('pathlib.Path.home')
        self.mock_home = self.patcher.start()
        self.mock_home.return_value = Path(self.test_dir)

    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_project_creation(self):
        """Test creating a new project."""
        from wrd.__main__ import WRDManager

        manager = WRDManager()
        # Store the project object to avoid unused variable warning
        project = manager.create_project(
            name=self.project_name, project_type="python", description="A test project"
        )

        # Check if project directory was created
        self.assertTrue(self.project_path.exists())

        # Check if essential files were created
        self.assertTrue((self.project_path / "README.md").exists())
        self.assertTrue((self.project_path / "CLAUDE.md").exists())
        self.assertTrue((self.project_path / "requirements.txt").exists())

        # Check if .wrd directory was created
        self.assertTrue((self.project_path / ".wrd").exists())
        self.assertTrue((self.project_path / ".wrd" / "config.json").exists())

    @patch('wrd.__main__.subprocess.run')
    def test_commit_command(self, mock_run):
        """Test the commit command."""
        from wrd.__main__ import WRDManager

        # Create a test project
        manager = WRDManager()
        manager.create_project(
            name=self.project_name, project_type="python", description="A test project"
        )

        # Test commit
        manager.commit_project(self.project_name)

        # Check if git commands were called
        self.assertTrue(mock_run.called)

    def test_list_projects(self):
        """Test listing projects."""
        from wrd.__main__ import WRDManager

        # Create a test project
        manager = WRDManager()
        manager.create_project(
            name=self.project_name, project_type="python", description="A test project"
        )

        # Test listing projects
        projects = manager.list_projects()
        self.assertIn(self.project_name, projects)


if __name__ == '__main__':
    unittest.main()
