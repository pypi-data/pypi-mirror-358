import os
from pathlib import Path
from bd_fileorganizer.organizer import organize_folder

def test_organize_folder(tmp_path):
    # create dummy files
    (tmp_path / "file1.jpg").write_text("image")
    (tmp_path / "file2.pdf").write_text("pdf")
    (tmp_path / "file3.zip").write_text("zip")

    actions = organize_folder(str(tmp_path))

    categories = [a[1].parent.name for a in actions]
    assert "images" in categories
    assert "documents" in categories
    assert "archives" in categories

    assert not (tmp_path / "file1.jpg").exists()
