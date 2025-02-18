# Python Package Downloader

## Overview
This program allows you to download Python packages from the PyPI repository based on various criteria. You can specify package names, version conditions, file extensions, and filters to refine your search. Additionally, you can download the latest version of a package or simply view the available versions without downloading them.

## Features
- Download specific versions of Python packages.
- Specify version conditions (e.g., `>=2.0.0` or `==1.2.3`).
- Filter downloads by file extensions (e.g., `.whl`, `.zip`, `.tar.gz`).
- Display available versions of packages without downloading.
- Automatically download the latest version of a package.

## Requirements
- Python 3.x
- `requests` library: You can install it using `pip install requests`.
- `packaging` library: for versioning checking. `pip install packaging`.

## Installation
1. Clone or download the script to your local machine.
2. Ensure you have Python 3.x installed.
3. Install the required Python dependencies by running:

   ```bash
   pip install requests packaging
   ```

## Usage

### Basic Usage
To download a package, simply provide the package specification (e.g., `flask`, `flask>=2`, `flask==1.2.3`) and an optional destination folder:

```bash
python pip_get.py flask
python pip_get.py flask>=2 --dest /path/to/destination
python pip_get.py flask>=2 --filter=py2 --ext=whl --dest=/path/to/destination
python pip_get.py flask<3 --latest --ext=whl --dest /path/to/destination
python pip_get.py flask<3 --latest --filter=py3  --dest /path/to/destination
```

### Optional Arguments
- `package_spec`: Specify the package name and version condition (e.g., `flask>=2.0.0`).
- `version_condition`: Optionally, provide a version condition if not specified in `package_spec` (e.g., `==1.2.3`).
- `--dest`: Specify the destination directory for downloaded packages. Defaults to the current working directory.
- `-s` or `--show-only`: Show package file names and versions without downloading.
- `--filter`: Comma-separated list of strings to filter file names (e.g., `arm,x86`).
- `--ext`: Specify file extensions to download (default: `whl,zip,tgz,gz`).
- `-l` or `--latest`: Download the latest version of the package.

### Example Commands
1. **Download the `flask` package:**
   ```bash
   python pip_get.py flask
   ```

2. **Download `flask` version greater than or equal to `2.0.0`:**
   ```bash
   python pip_get.py flask>=2.0.0
   ```

3. **Show available `flask` versions without downloading:**
   ```bash
   python pip_get.py flask -s
   ```

4. **Download the latest version of `flask`:**
   ```bash
   python pip_get.py flask --latest
   ```

5. **Download packages with specific filters (e.g., for ARM architecture):**
   ```bash
   python pip_get.py flask --filter arm
   ```

6. **Download specific file extensions (e.g., only `.whl` files):**
   ```bash
   python pip_get.py flask --ext whl
   ```


## License
This project is licensed under the MIT License - see the LICENSE file for details.
