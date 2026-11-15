# Medicare Plus — Hospital Management System

A Tkinter desktop application for managing common hospital workflows. This refreshed edition focuses on a polished clinical dashboard, a consistent teal-and-navy visual system, clearer typography, and more spacious tables and navigation.

## Modules

- Staff login (Admin, Doctor, Receptionist demo accounts)
- Dashboard with patient, inpatient, doctor and bed-capacity metrics
- Patient registry and patient dossier
- Doctor and staff roster
- Appointment scheduling
- Ward and bed allocation / maintenance
- Billing and invoice management
- SQLite persistence

## Technology

- Python 3
- Tkinter / ttk for the desktop interface
- SQLite for local data storage
- Pillow for dashboard charts and visual assets

## Run on macOS

1. Extract this ZIP file.
2. Open Terminal and move into the extracted folder:

   ```bash
   cd /path/to/hospital_management_system5
   ```

3. Install the visual dependency:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

4. Start the application:

   ```bash
   python3 main.py
   ```

Tkinter is normally included with the standard Python installation on macOS. If Python reports that `_tkinter` is missing, install a Python distribution that includes Tcl/Tk.

## Demo accounts

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Doctor | `doctor` | `doctor123` |
| Receptionist | `reception` | `reception123` |

These are demonstration credentials only. Change them before any real deployment. Do not enter real patient or other sensitive health information into a classroom/demo installation.

## Data

The application uses the included `hospital.db` SQLite file. Keep a backup before experimenting with records. The database is local to this project folder.

## UI refresh highlights

- Updated teal clinical brand color with deep navy navigation
- Soft cool-grey workspace background and clean white surfaces
- More readable typography and improved table row spacing
- Refined sidebar labels, active navigation state and header accent
- New dashboard welcome panel with current date
- Updated chart colors to match the new visual identity

## Notes

This project is intended for learning and demonstration. It is not a certified hospital information system and should not be used for clinical decisions or production patient data.

## Login screen visual upgrades

- Three selectable accent themes: Midnight Emerald, Cyber Violet, and Solaris Gold.
- Theme selection updates the shared accent palette used by the login and subsequently created application screens.
- Animated login illustration built with a native Tkinter Canvas: floating medical bubbles, a moving ambulance, an animated arrow, and an ECG-style pulse line.
- Animation uses Tkinter's `after()` loop and does not require downloaded images or additional packages.
