# Saigon Route Lab

An AI101 Lab 1 project that compares graph-search algorithms while planning
tourist routes between landmarks in Ho Chi Minh City.

## Project structure

- `lab-1-backend`: FastAPI, OSM graph loading, six search algorithms,
  multi-location optimization, tests, and route explanations.
- `lab-1-frontend`: React, TypeScript, Vite, Leaflet, live search animation,
  comparison mode, and multi-landmark mode.

The repositories are linked here as Git submodules. After cloning, initialize
them with:

```powershell
git submodule update --init --recursive
```

## Start the application

Terminal 1 (Backend - Linux / macOS):

```bash
cd lab-1-backend
python3 -m venv venv
source venv/bin/activate
pip install -e .
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Terminal 1 (Backend - Windows PowerShell):

```powershell
cd lab-1-backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -e .
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Terminal 2 (Frontend):

```bash
cd lab-1-frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173` for the application and
`http://127.0.0.1:8000/docs` for the API explorer.

## Deliverables

- [Technical report](docs/TECHNICAL_REPORT.md)
- [Final 13-page report PDF](output/pdf/1%20-%20Report.pdf)
- [Full-score readiness audit](docs/FULL_SCORE_AUDIT.md)
- [Dataset description](docs/DATA_DESCRIPTION.md)
- [Algorithm walkthrough](docs/ALGORITHM_WALKTHROUGH.md)
- [Demo script](docs/DEMO_SCRIPT.md)
- [Submission checklist](docs/SUBMISSION_CHECKLIST.md)
- [Verified 20-slide presentation](output/presentation/1%20-%20Slide.pptx)
- 70 automated backend tests and a verified production frontend build

## Export the report PDF

The submission report uses the supplied academic LaTeX style. With TeX Live
and XeLaTeX installed, rebuild it with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\build_report_latex.ps1
```

The editable LaTeX source is `docs/TECHNICAL_REPORT.tex`. The Markdown and
ReportLab path below remains available as a content-oriented fallback.

Create `docs/group_metadata.json` from the provided example, replace every
sample value with the verified Group ID, full names, and student IDs, then run:

```powershell
python -m pip install reportlab
python scripts\build_report.py `
  --metadata docs\group_metadata.json `
  --output "output\pdf\<official-group-id> - Report.pdf"
```

The exporter rejects missing/sample identity values and produces a Unicode A4
report with a contents page, page numbers, tables, flow diagrams, and the three
verified application screenshots.

## Build the submission ZIP

After the final report PDF and public video URL are available, run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\build_submission.ps1 `
  -GroupId "<official-group-id>" `
  -ReportPdf "<absolute-path-to-report.pdf>" `
  -VideoUrl "https://<public-video-url>"
```

The script validates the inputs and creates one ZIP containing exactly the five
filenames required by the Lab 1 specification.
