# 🏥 Medicare Plus — Hospital Management System

**Medicare Plus** is a modern Python Tkinter-based Hospital Management System designed to simplify and manage common hospital operations through an interactive desktop application.

The application provides a unified platform for patient management, doctor management, appointment scheduling, ward allocation, billing and hospital administration.

It features a polished clinical dashboard, a consistent teal-and-navy visual system, interactive components and SQLite database integration.

---

## ✨ Key Features

- 🔐 **Staff Authentication** – Separate login access for Admin, Doctor and Receptionist.
- 📊 **Dashboard** – Overview of patients, inpatients, doctors and bed capacity.
- 🧑‍🤝‍🧑 **Patient Management** – Register, search and manage patient records.
- 🩺 **Doctor Management** – Manage doctor profiles, departments and availability.
- 📅 **Appointment Management** – Schedule and track patient appointments.
- 🏥 **Ward Management** – Allocate beds and monitor occupancy and maintenance.
- 💳 **Billing Management** – Manage invoices, payments and receipts.
- 🗄️ **SQLite Database** – Store and maintain application records locally.

---

## 🖥️ Technology Stack

| Technology | Purpose |
|---|---|
| Python 3 | Core programming language |
| Tkinter | Desktop GUI development |
| ttk | Modern styled interface components |
| SQLite | Local database management |
| Pillow | Dashboard charts and visual assets |
| Git & GitHub | Version control and collaboration |

---

## 🎨 UI & Design Highlights

Medicare Plus features a modern healthcare-inspired interface.

### Visual Features

- Deep navy sidebar navigation.
- Modern teal clinical accent colour.
- Clean white cards and cool-grey workspace.
- Improved typography and table spacing.
- Dashboard welcome panel with current date.
- Refined navigation and active menu indicators.

### Login Screen Themes

Three selectable accent themes:

1. 🌿 **Midnight Emerald**
2. 💜 **Cyber Violet**
3. 🌟 **Solaris Gold**

### Animated Login Illustration

The login interface includes a native Tkinter Canvas animation:

- Floating medical bubbles.
- Moving ambulance illustration.
- Animated directional arrow.
- ECG-style pulse animation.
- Tkinter `after()` animation loop.

No external animation assets are required for these Canvas animations.

---

## 📂 Project Modules

| Module | Description |
|---|---|
| Login | Role-based demo authentication |
| Dashboard | Hospital statistics and overview |
| Patients | Patient registration and records |
| Doctors | Doctor directory and availability |
| Appointments | Appointment scheduling |
| Wards | Bed allocation and occupancy |
| Billing | Invoice and payment management |

---

# 🚀 Installation & Setup

Medicare Plus can be run on both **Windows and macOS**.

## 🍎 Run on macOS

### Step 1: Install Python

Download Python 3:

https://www.python.org/downloads/

### Step 2: Clone Repository

Open Terminal:

```bash
git clone https://github.com/abhijeetsingh381/Medicare-Plus.git
```

### Step 3: Open Project Folder

```bash
cd Medicare-Plus
```

### Step 4: Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

### Step 5: Run Application

```bash
python3 main.py
```

---

## 🪟 Run on Windows

### Step 1: Install Python

Download Python 3:

https://www.python.org/downloads/

**Important:** During installation, enable:

`Add Python to PATH`

### Step 2: Install Git

Download Git for Windows:

https://git-scm.com/downloads/win

### Step 3: Clone Repository

Open Command Prompt or PowerShell:

```bash
git clone https://github.com/abhijeetsingh381/Medicare-Plus.git
```

### Step 4: Open Project Folder

```bash
cd Medicare-Plus
```

### Step 5: Install Dependencies

```bash
py -m pip install -r requirements.txt
```

If `py` is unavailable, use:

```bash
python -m pip install -r requirements.txt
```

### Step 6: Run Application

```bash
py main.py
```

Alternatively:

```bash
python main.py
```

---

## 🔐 Demo Login Credentials

The application includes demonstration login accounts.

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Doctor | `doctor` | `doctor123` |
| Receptionist | `reception` | `reception123` |

**Note:** These credentials are for academic demonstration only. Change them before any real deployment.

---

## 🗄️ Database Information

Medicare Plus uses SQLite for local data persistence.

- Database: SQLite
- Database file: `hospital.db`
- Storage: Local project directory
- Purpose: Persistent hospital application records

Keep a backup of the database before experimenting with records.

---

## 📸 Application Screenshots

Screenshots of the application can be added here to demonstrate its interface and functionality.

Recommended screenshots:

1. Login Screen
2. Dashboard
3. Patient Management
4. Doctor Management
5. Appointment Management
6. Ward Management
7. Billing Dashboard
8. Invoice / Receipt

---

## 👨‍💻 Project Team

| Team Member | Registration Number |
|---|---|
| Abhijeet Singh | RA2511047010124 |
| Sarthak Nagelia | RA2511047010087 |
| Parth Bhandari | RA2511047010077 |

---

## 🔮 Future Scope

- Online appointment booking.
- Email and SMS notifications.
- Advanced reporting and analytics.
- Role-based permission improvements.
- Cloud database integration.
- Secure patient record management.
- Automated invoice generation.

---

## ⚠️ Disclaimer

Medicare Plus is an academic learning and demonstration project.

It is not a certified hospital information system and must not be used for clinical decisions or production patient data.

Demo credentials and local database storage are not suitable for handling real patient information.

---

## 📌 Repository

**GitHub:** https://github.com/abhijeetsingh381/Medicare-Plus

---

<div align="center">

### 🏥 MEDICARE PLUS

**Care Operations, Connected.**

*Designed and developed by Team Medicare Plus.*

</div>