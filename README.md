# SmartMed Egypt
*An Expert System for Medical Specialty and Hospital Recommendation*
Educational rule-based decision-support project. **Not a diagnostic device. No medicines or treatment are suggested.**
For emergencies call the ambulance (123) and do not delay care to search for a hospital.

## Six stages
1. Patient form (name, age, sex, governorate, address, optional phone)  2. Symptoms, duration, severity (multi-select)  3. Knowledge base (`knowledge_base.py`)
4. Inference engine (`inference_engine.py`)  5. Hospital search (`hospital_database.py`, SQL filters)
6. ONE results screen (patient summary, symptoms, rule assessment, specialty, recommended hospitals by name, tests to discuss, guidance) + saved case history (SQLite, local only)

## Files
main.py (entry) | gui.py (Tkinter Arabic RTL screens) | knowledge_base.py (symptoms, specialties, 46 IF-THEN rules)
| report_builder.py (builds the one-screen result + form validation + automatic hospital recommendation) | inference_engine.py (forward chaining + scoring + urgent warnings) | hospital_database.py (SQLite layer)
| seed_data.py (hospital records + sources) | hospitals.db (prebuilt, 40 hospitals) | tests.py | requirements.txt

## Install & run (Windows)
1. Install Python 3.10+ from python.org (tick "Add Python to PATH"; keep "tcl/tk" selected).
2. Open the folder in Command Prompt: `cd SmartMed_Egypt`
3. `pip install -r requirements.txt` (no external packages needed)
4. `python main.py`

## Add / update hospitals
Edit `seed_data.py` (use `H(...)`; leave unknown fields blank; every record needs a real `source_url`;
add a specialty only with a source), then run `python hospital_database.py` to rebuild `hospitals.db`
(saved cases are kept). Add Arabic names via `name_ar="..."` once verified.

## Tests
`python tests.py` - covers DB loading, governorate/type/specialty/combined filters, empty results,
missing fields, cases save/delete, and the main inference rules.

## Search behaviour
A hospital matches a specialty only if a record supports it. Tick "show unverified" to also list hospitals
with no specialty data (flagged "Not verified").

## Known limitations / data sources
- 40 hospitals: Cairo, Giza, Alexandria, Beni Suef, Minya, Luxor, Aswan, South Sinai, Red Sea. Other governorates: **no verified data yet**.
- Most records come from the UK FCDO list (gov.uk, 2022 edition): names, phones, addresses, public/private. Phones may have changed.
- Beni Suef: address and phones from the official Beni Suef University contact page (some online directories list a different street). Minya: phones from Minia University's official telephone page; the street (Corniche El Nil) comes from public directories, not an official page. Kasr Al Ainy: address/phone are those of the Faculty of Medicine contact page, not a dedicated hospital line.
- Kasr Al Ainy, Abu El Reesh, National Cancer Institute: Wikipedia source; Dar Al Fouad specialties: a secondary directory.
- **Arabic hospital names are not verified, so `name_ar` is blank** (the GUI shows the English name). Ministry of Health directories were not accessible.
- Governorate was assigned by the author from the city/area (e.g. Mohandessin, 6th October -> Giza).
- Rules are simplified teaching rules, not clinical guidelines.

## Quick start (Windows)
- Double-click `run.bat` to run with Python.
- To make an .exe: double-click `build_exe.bat` (needs internet once). The program appears in `dist\SmartMedEgypt\`.
  Copy that whole folder to any laptop; Python is not needed there.

## What changed in version 2 (UI update)
- New blue/white medical GUI with icons and a welcome screen; friendlier success/warning messages.
- New personal-data form (name, age, sex, governorate, address, optional phone) with validation.
- Results appear on ONE screen. The hospital is chosen **automatically** from the database (`recommend_hospitals`) and shown by **name**, address, phone, website and source. Fallback order: same governorate with the specialty documented -> same governorate with undocumented specialties (flagged) -> other governorates with the specialty documented -> same governorate (specialty unconfirmed) -> none.
- Urgent cases show a red banner (call 123) at the top and in the hospital section.
- New "tests to discuss with the doctor" list (`TESTS_TO_DISCUSS` in knowledge_base.py): educational, written by the project author, NOT taken from the hospital sources; the doctor alone decides.
- Two safety rules added: R45 chest pain alone -> cardiology + urgent warning; R46 shortness of breath alone -> pulmonology.
- Saved cases now also store name, address, phone and governorate (local SQLite file only). Old `hospitals.db` files are upgraded automatically. Delete cases from the History screen if you do not want them kept.
- The old hospital search screen is still available ("بحث متقدم عن مستشفى") and history view/delete still work.
- Double-click `run.bat` to start (it checks that Python is installed).

## Testing status
`python tests.py` runs 39 automated tests (logic, database, filters, report builder, validation, migration, web app).
The GUI screens were checked with a stub Tkinter (button logic and screen content), not with a real window, because the build environment has no Tkinter. Please open the app once on Windows and check the Arabic layout visually.

## Web version (version 3)
Same project, same `hospitals.db`, same knowledge base / inference engine / report builder, now also as a web app that works on laptops and phones.
- `webapp.py` - WSGI web app (Python standard library only; no Flask needed). Pages: home, patient form, symptoms, one-screen results, hospital search, history.
- `wsgi.py` - entry point for hosting. `run_web.py` / `run_web.bat` - run locally (also reachable from a phone on the same Wi-Fi).
- `Procfile`, `render.yaml`, `requirements.txt` (gunicorn only for online hosting).
- Beginner guide in Arabic: **WEB_DEPLOY_AR.md** (local run + free PythonAnywhere link).
- Web history is private per browser (anonymous cookie stored in a new `owner` column; old databases are upgraded automatically). Saved cases are still stored on the server's SQLite file, so tell test users not to enter real personal data on a public link.
- Security: all output is HTML-escaped, strict Content-Security-Policy, no JavaScript, HttpOnly cookie. Not included: login, HTTPS setup (hosting providers give HTTPS), rate limiting.
- The desktop app (`main.py`, `gui.py`) still works unchanged.
- Testing status: the web app was run as a real server and tested with HTTP requests (curl) and 39 automated tests. Not tested: visual look in real phone browsers, and the actual hosting services.

## Why this web version does not use Streamlit
The web app uses only Python's standard library (`webapp.py`). Reasons: it needs no installation, it was tested here as a real server, Arabic right-to-left layout is fully under our control (Streamlit's RTL support is limited), and it can be hosted on free services. All features, the knowledge base and `hospitals.db` are the same.
## Verification dates
Hospital contact data was last checked on 16 Oct 2026 using web search. Phones/addresses change; confirm by calling before visiting.
