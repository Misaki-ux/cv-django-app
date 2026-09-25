# CV Builder

A Django application for managing a profile, building CVs, importing an existing CV, and downloading CVs as PDFs.

## Requirements

- Windows with Python **3.11** (the current project environment has been set up for Python 3.11)
- pip

Use Python 3.11 consistently for creating the virtual environment, installing packages, and running Django. If `py` is available, `py -3.11` selects that interpreter.

## First-time setup (Windows PowerShell)

From the project directory:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_templates
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser. If PowerShell prevents virtual-environment activation, run the commands explicitly with `.\.venv\Scripts\python.exe` instead, for example:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_templates
.\.venv\Scripts\python.exe manage.py runserver
```

## Login and accounts

There are no shared default username or password credentials. Create an account from the **Register** page in the application, then sign in at <http://127.0.0.1:8000/accounts/login/>. User accounts are stored in the local SQLite database (`db.sqlite3`).

To create an administrator account for Django's admin site, run:

```powershell
python manage.py createsuperuser
```

Then sign in at <http://127.0.0.1:8000/admin/> using the username and password you chose. If you forget a local account password, reset it with:

```powershell
python manage.py changepassword YOUR_USERNAME
```

## Languages

Use the **EN** and **FR** controls in the navigation to change the interface language. CV preview and PDF headings follow the selected language; for example, **Skills** is shown as **Compétences** in French.

## CV builder

1. Register and sign in, then choose **New CV** to select a template and create a CV.
2. In the CV editor, add or edit contact details, education, work experience, skills, and languages. Click a skill name to edit its rating from 1 to 5.
3. Use **Design** to change the CV template, colors, and sidebar width. Template cards show each template's preview icon and colors; the current template is highlighted.
4. Use the **Show photo on CV** checkbox to include or hide the photo area in the preview and downloaded PDF.
5. In **Experience**, drag an experience card to reorder it, then select **Save experience order**. Drag a card onto **Education** or use its **Move** button to convert it into an education entry. Its title, company, dates, description, and location are carried over.
6. Open **Preview** to view the CV or **PDF** to download it.

## Importing an existing CV

Use the CV import page to upload a PDF or DOCX. Review the extracted information before importing it into the profile and CV Builder. The importer extracts contact details, skills, education, and experience; it recognizes experience dates formatted as `YYYY`, `MM/YYYY`, `DD/MM/YYYY`, or `DD/MM/YY`, including date ranges. Education entries containing terms such as **Bac**, **BTS**, **Master**, **Licence**, **Highschool**, or **Faculté** are classified as education instead of work experience. Review imported entries in the CV editor and correct any PDF extraction errors before downloading.

## Optional API keys

External API integrations are optional. Copy `.env.example` to `.env` and set the keys you use (`GOOGLE_MAPS_API_KEY`, `HUGGINGFACE_API_KEY`, and, if desired, `DJANGO_SECRET_KEY`). Keep `.env` private; it is excluded from Git.
