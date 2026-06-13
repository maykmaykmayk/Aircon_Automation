# Aircon Automation (CLI)

Interactive aircon sizing calculator using `inquirer` prompts and `rich` terminal output.

## Requirements

- Python 3.10+
- Dependencies from `requirements.txt`:
  - `rich`
  - `inquirer`
  - `pyinstaller`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Python Version

```bash
python main.py
```

## Build Executable with PyInstaller

Exact PyInstaller command:

```bash
pyinstaller --onefile --console --name aircon-calculator main.py
```

On Windows, this produces:

- `dist/aircon-calculator.exe`

### Windows Build Script

```bat
build.bat
```

### Mac/Linux Build Script

```bash
chmod +x build.sh
./build.sh
```

On Mac/Linux, output is:

- `dist/aircon-calculator`

