To **build and upload your PyQt app as a Linux executable** to GitHub Releases, we'll use **`PyInstaller`** and **GitHub Actions**.

This setup will:

* Build your PyQt app as a standalone `.AppImage` or `.tar.gz` package.
* Trigger when a **Git tag** is pushed.
* Upload the artifact to **GitHub Releases**.

---

## ✅ Step-by-Step Setup

### 📦 1. Add `pyinstaller` to your project dependencies (optional for local dev):

```bash
pip install pyinstaller
```

Or add to `pyproject.toml` (if using `pip-tools` or poetry):

```toml
[project.optional-dependencies.dev]
build = ["pyinstaller"]
```

---

### 🧰 2. Create a PyInstaller spec (optional)

Create a basic one using:

```bash
pyinstaller --onefile --windowed --icon=icon.png --name PIPLibraryUploader main.py

```

This generates:

* `dist/pip-uploader`
* `build/`
* `pip-uploader.spec`

---

### 🛠️ 3. Create GitHub Actions Workflow

Create the following file:
📁 `.github/workflows/build-linux.yml`

```yaml
name: Build Linux Executable

on:
  push:
    tags:
      - 'v*'  # Triggers on version tags like v0.1.0, v1.0.1, etc.

permissions:
  contents: write  # Needed to upload release assets

jobs:
  build-linux:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout source code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pyinstaller
        pip install -r requirements.txt || true  # Or use pip install .[build]

    - name: Build executable
      run: |
        pyinstaller --name=pip-uploader --onefile main.py
        mkdir -p dist-upload
        cp dist/pip-uploader dist-upload/
        tar -czvf dist-upload/pip-uploader.tar.gz -C dist-upload pip-uploader

    - name: Upload to GitHub Release
      uses: softprops/action-gh-release@v2
      with:
        tag_name: ${{ github.ref_name }}
        files: |
          dist-upload/pip-uploader.tar.gz
          dist/pip-uploader
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

### 📁 4. Create `requirements.txt` (for GitHub runner)

Even though you’re using `pyproject.toml`, GitHub Actions prefers a `requirements.txt`:

```bash
pip freeze > requirements.txt
```

---

### 🏁 5. Usage

When you are ready to release:

```bash
cz bump --yes --changelog  # OR manually tag:
git tag v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

➡️ GitHub Actions will:

* Build your app on Linux.
* Upload the binary and `.tar.gz` to the **GitHub Release**.

---

## 📦 Optional Enhancements

* 🧊 Use [AppImage](https://appimage.org/) to create a truly portable Linux GUI binary.
* 📜 Add license, version info, icons using `--icon`, `--version-file`, or `.spec` customization.
* 🧪 Add CI build matrix for **Windows/Mac/Linux**.

---

Would you also like:

* Windows `.exe` builds via GitHub Actions?
* `.deb` packaging for Linux?
