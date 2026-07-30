# Marble Work Report Generator

Desktop Python tool for creating monthly PDF work reports.

## Included
- `report_generator.py`
- `marble_logo.png`
- `requirements.txt`

## Install
```bash
pip install -r requirements.txt
```

## Run
```bash
python report_generator.py
```

The app lets you add multiple rows, choose an image for each row, enter hours, calculate total hours, and save/load the report data as JSON.

## Windows executable
The packaged Windows app is available at:

```text
dist/ReportGeneratorFreelance.exe
```

To rebuild it, install PyInstaller and run:

```powershell
pyinstaller --noconfirm --clean ReportGeneratorFreelance.spec
```
