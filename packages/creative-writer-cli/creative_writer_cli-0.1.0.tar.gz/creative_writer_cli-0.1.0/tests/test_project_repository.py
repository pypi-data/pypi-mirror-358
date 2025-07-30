import os
import shutil
import unittest
from creative_writer_cli.data.repositories.project_repository import ProjectRepository

class TestProjectRepository(unittest.TestCase):
    def setUp(self):
        self.test_base_dir = "test_projects"
        self.repo = ProjectRepository(base_dir=self.test_base_dir)
        # Ensure the test_projects directory is clean before each test
        if os.path.exists(self.test_base_dir):
            shutil.rmtree(self.test_base_dir)
        os.makedirs(self.test_base_dir)

    def tearDown(self):
        # Clean up the test_projects directory after each test
        if os.path.exists(self.test_base_dir):
            shutil.rmtree(self.test_base_dir)

    def test_create_project(self):
        success, message = self.repo.create_project("MyTestNovel", "Novel")
        self.assertTrue(success)
        self.assertIn("created successfully", message)
        self.assertTrue(os.path.exists(os.path.join(self.test_base_dir, "MyTestNovel")))
        self.assertTrue(os.path.exists(os.path.join(self.test_base_dir, "MyTestNovel", "meta.json")))

    def test_delete_project(self):
        self.repo.create_project("ProjectToDelete", "Novel")
        self.assertTrue(os.path.exists(os.path.join(self.test_base_dir, "ProjectToDelete")))

        success, message = self.repo.delete_project("ProjectToDelete")
        self.assertTrue(success)
        self.assertIn("deleted", message)
        self.assertFalse(os.path.exists(os.path.join(self.test_base_dir, "ProjectToDelete")))

    def test_create_existing_project(self):
        self.repo.create_project("ExistingProject", "Novel")
        success, message = self.repo.create_project("ExistingProject", "Novel")
        self.assertFalse(success)
        self.assertIn("already exists", message)

    def test_delete_non_existing_project(self):
        success, message = self.repo.delete_project("NonExistingProject")
        self.assertFalse(success)
        self.assertIn("not found", message)
