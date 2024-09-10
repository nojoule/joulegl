import os
import shutil

import pytest


def delete_all_files_in_folder(folder_path: str) -> None:
    try:
        for filename in os.listdir(folder_path):
            if filename == ".gitkeep":
                continue
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
    except Exception as e:
        print(f"Failed to delete files in {folder_path}. Reason: {e}")


def pytest_sessionstart(session: pytest.Session) -> None:
    os.environ["TESTING"] = "True"


def pytest_sessionfinish(session: pytest.Session) -> None:
    # remove all files in tests/tmp
    folder = "tests/tmp"
    delete_all_files_in_folder(folder)
