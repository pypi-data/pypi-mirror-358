import pytest
from src.document_brain.server import read_any_document

# Fixture to create a temporary text file
@pytest.fixture
def temp_text_file(tmp_path):
    file_path = tmp_path / "test_document.txt"
    file_path.write_text("This is a test document.")
    return file_path

# Test reading a valid text file
def test_read_valid_document(temp_text_file):
    content = read_any_document(str(temp_text_file))
    assert "This is a test document." in content

# Test reading a non-existent file
def test_read_nonexistent_file():
    content = read_any_document("nonexistent_file.txt")
    assert "Error reading file" in content