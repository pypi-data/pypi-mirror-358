import shutil
from pathlib import Path

EXTENSION_MAP = {
    "images": [".jpg", ".jpeg", ".png", ".gif"],
    "documents": [".pdf", ".docx", ".txt"],
    "archives": [".zip", ".tar", ".gz", ".rar"],
    "videos": [".mp4", ".mov", ".mkv"],
    "audio": [".mp3", ".wav"],
}

def get_category(extension: str) -> str:
    for category, extensions in EXTENSION_MAP.items():
        if extension.lower() in extensions:
            return category
    return "others"

def organize_folder(folder_path: str, dry_run: bool = False) -> list:
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"{folder_path} is not a valid folder")

    actions = []

    for file in folder.iterdir():
        if file.is_file():
            category = get_category(file.suffix)
            target_dir = folder / category
            target_dir.mkdir(exist_ok=True)

            target_file = target_dir / file.name
            actions.append((file, target_file))

            if not dry_run:
                shutil.move(str(file), str(target_file))

    return actions
