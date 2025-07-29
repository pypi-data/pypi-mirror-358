# 🗂️ bd_fileorganizer

**bd_fileorganizer** is a simple yet powerful Python utility that helps you clean up cluttered folders by automatically moving files into categorized subfolders like `images/`, `documents/`, `archives/`, and more — all based on file extensions.

It’s perfect for tidying up your `Downloads`, `Desktop`, or project folders with just one command.

---
## 📦 HOW TO USE:

** In Your terminal:
If mac use  python3 , if windows use python
- pip install bd-fileorganizer
- from bd_fileorganizer.organizer import organize_folder
- organize_folder("give your folder path with different files")

** In Your ipynb file:
- pip install bd-fileorganizer
- from bd_fileorganizer.organizer import organize_folder
- organize_folder("give your folder path with different files")

## 📦 Features

- 📁 Automatically sorts files into categories
- 🧠 Smart extension detection (`.jpg` → `images`, `.pdf` → `documents`, etc.)
- 🧪 Dry-run mode to preview changes
- 🐍 Easy-to-use Python API and CLI interface
- ✅ Beginner-friendly code and customizable

---

## 🚀 Installation

Install from source:

```bash
pip install bd-fileorganizer
````

> 📌 Available on PyPI!
    https://pypi.org/project/bd-fileorganizer/

---

## 🖥️ CLI Usage

```bash
organize_folder "/path/to/folder"
```

**Dry-run (preview only):**

```bash
organize_folder "/path/to/folder" --dry
```

---

## 🐍 Python API

```python

from bd_fileorganizer.organizer import organize_folder

organize_folder("/Users/you/Downloads")
```

---

## 🧪 Running Tests

```bash
pytest
```

---

## 🗃️ Folder Structure Example

**Before:**

```
Downloads/
├── photo.jpg
├── report.pdf
├── backup.zip
```

**After:**

```
Downloads/
├── images/
│   └── photo.jpg
├── documents/
│   └── report.pdf
├── archives/
│   └── backup.zip
```

---

## 🔧 Extension Mapping

| Category     | Extensions                      |
| ------------ | ------------------------------- |
| `images/`    | `.jpg`, `.jpeg`, `.png`, `.gif` |
| `documents/` | `.pdf`, `.docx`, `.txt`         |
| `archives/`  | `.zip`, `.tar`, `.gz`, `.rar`   |
| `videos/`    | `.mp4`, `.mov`, `.mkv`          |
| `audio/`     | `.mp3`, `.wav`                  |
| `others/`    | Everything else                 |

---

## 📄 License

Licensed under the [GNU License](https://www.gnu.org/licenses/gpl-3.0.html#license-text)

---

## 🤝 Contributing

Contributions, feature ideas, and bug reports are welcome!
Feel free to open an [issue](https://github.com/bhuvan0808/bd-fileorganizer/issues) or a [pull request](https://github.com/bhuvan0808/bd-fileorganizer/pulls).

---

## 👤 Authors

**Bhuvan**
GitHub: [@bhuvan0808](https://github.com/bhuvan0808)
GitHub: [@devaagulla](https://github.com/devaagulla)



---

> 🧹 Make your folders smarter, not messier — with `bd-fileorganizer` 🗂️