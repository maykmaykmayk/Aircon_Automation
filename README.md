# Aircon Automation (CLI) - Sir Edward Project

# Testing for possible improvements

## Requirements

- Python 3.10+
- Dependencies from `requirements.txt`:
  - `rich`
  - `inquirer`
  - `pyinstaller`

How to Install dependencies:
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


