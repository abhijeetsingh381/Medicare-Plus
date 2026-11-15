"""
Main Entry Point for Medicare Plus Hospital Management System.
Features Full Authentication Flow (Login Page), Chief Profile Customization,
Real-time Doctor Status Updates, and Bed Maintenance Operations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
from styles import Theme, setup_ttk_styles
from ui_components import ModernSidebar, ModernHeader, LiveVitalsTicker, EditChiefProfileModal
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.patients_view import PatientsView, AddPatientModal, PatientDossierModal
from views.doctors_view import DoctorsView
from views.appointments_view import AppointmentsView
from views.wards_view import WardsView
from views.billing_view import BillingView


class HospitalManagementApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("MEDICARE PLUS • Hospital Operations Center")
        self.configure(bg=Theme.BG_MAIN)
        self.minsize(1050, 680)

        # Auto-calibrate window geometry based on user's display size
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        target_w = min(1320, max(1050, sw - 80))
        target_h = min(840, max(680, sh - 90))
        pos_x = max(20, (sw - target_w) // 2)
        pos_y = max(30, (sh - target_h) // 2)
        self.geometry(f"{target_w}x{target_h}+{pos_x}+{pos_y}")

        # Initialize SQLite database, seed tables & demo accounts
        database.init_db()

        # Apply Modern TTK Styles
        self.style = setup_ttk_styles(self)

        # Current logged in user info
        self.current_user = database.get_chief_profile()

        # Container for screens (Login vs Main Dashboard)
        self.root_container = tk.Frame(self, bg=Theme.BG_MAIN)
        self.root_container.pack(fill="both", expand=True)

        # Build Login View
        self.login_view = LoginView(self.root_container, on_login_success=self.on_login_success,
                                    on_theme_change=self.on_theme_change)
        self.login_view.pack(fill="both", expand=True)

        # Main Workspace Wrapper (hidden until login)
        self.main_wrapper = tk.Frame(self.root_container, bg=Theme.BG_MAIN)

        self.sidebar = None
        self.header = None
        self.vitals_ticker = None
        self.view_container = None
        self.views = {}
        self.current_view_name = None

    def on_theme_change(self, theme_name):
        """Refresh ttk widget styles after a login-screen palette change."""
        self.style = setup_ttk_styles(self)

    def on_login_success(self, user):
        """Called when user successfully authenticates on the login screen."""
        self.current_user = user
        self.login_view.pack_forget()

        if not self.sidebar:
            self._build_dashboard_layout()

        # Update sidebar with logged in user profile
        self.sidebar.update_profile_display(self.current_user)

        # Show main workspace
        self.main_wrapper.pack(fill="both", expand=True)

        # Navigate to Dashboard
        self.sidebar.select_tab("dashboard")

    def on_logout(self):
        """Logs out the user and returns to the login screen."""
        confirm = messagebox.askyesno("Log Out", "Are you sure you want to log out of Medicare OS?")
        if confirm:
            self.main_wrapper.pack_forget()
            self.login_view.pack(fill="both", expand=True)

    def _build_dashboard_layout(self):
        # 1. Left Navigation Sidebar
        self.sidebar = ModernSidebar(
            self.main_wrapper,
            on_navigate=self.navigate_to_view,
            on_edit_profile=self.on_chief_profile_edited,
            on_logout=self.on_logout
        )
        self.sidebar.pack(side="left", fill="y")

        # 2. Right Content Wrapper
        self.right_wrapper = tk.Frame(self.main_wrapper, bg=Theme.BG_MAIN)
        self.right_wrapper.pack(side="right", fill="both", expand=True)

        # 3. Top Header
        self.header = ModernHeader(
            self.right_wrapper,
            on_quick_action=self.on_global_quick_admission
        )
        self.header.pack(fill="x")

        # 4. Live Mission Control Vitals Ribbon
        self.vitals_ticker = LiveVitalsTicker(self.right_wrapper)
        self.vitals_ticker.pack(fill="x")

        # 5. Dynamic Views Container
        self.view_container = tk.Frame(self.right_wrapper, bg=Theme.BG_MAIN)
        self.view_container.pack(fill="both", expand=True)

        # Instantiate View Frames
        self.views = {
            "dashboard": DashboardView(
                self.view_container,
                on_navigate=lambda tab: self.sidebar.select_tab(tab),
                on_view_patient=self.open_patient_dossier
            ),
            "patients": PatientsView(
                self.view_container,
                on_view_patient=self.open_patient_dossier
            ),
            "doctors": DoctorsView(self.view_container),
            "appointments": AppointmentsView(self.view_container),
            "wards": WardsView(self.view_container),
            "billing": BillingView(self.view_container)
        }

    def on_chief_profile_edited(self, updated_profile):
        """Called when Chief profile is updated."""
        self.current_user.update(updated_profile)
        if self.sidebar:
            self.sidebar.update_profile_display(self.current_user)
        if self.current_view_name:
            self.navigate_to_view(self.current_view_name)

    def navigate_to_view(self, view_name):
        """Switches the active visible view frame with clean titles."""
        if view_name not in self.views:
            return

        if self.current_view_name and self.current_view_name in self.views:
            self.views[self.current_view_name].pack_forget()

        target_view = self.views[view_name]
        target_view.pack(fill="both", expand=True)
        self.current_view_name = view_name

        user_name = self.current_user.get("full_name", "Chief")
        view_headers = {
            "dashboard": ("Dashboard Overview", f"Welcome, {user_name} • Real-time clinical analytics"),
            "patients": ("Patient Registry", "Manage admissions, records, and clinical triage"),
            "doctors": ("Physicians & Staff Roster", "Directory of active clinical doctors and OPD schedules"),
            "appointments": ("Appointments Schedule", "Manage consultation slots and diagnostic visits"),
            "wards": ("Ward Capacity & Bed Matrix", "Floor status across ICU, General, and Recovery wings"),
            "billing": ("Billing & Accounts Ledger", "Invoicing, itemized services, and payment status")
        }

        title, subtitle = view_headers.get(view_name, ("Hospital Management", "Medicare System"))
        self.header.set_view_title(title, subtitle)

        if hasattr(target_view, "refresh_data"):
            target_view.refresh_data()
        elif hasattr(target_view, "refresh_table"):
            target_view.refresh_table()
        elif hasattr(target_view, "refresh_doctors"):
            target_view.refresh_doctors()
        elif hasattr(target_view, "refresh_wards"):
            target_view.refresh_wards()

    def on_global_quick_admission(self):
        """Triggered by the top header '+ New Admission' button."""
        def on_admitted():
            if self.current_view_name:
                self.navigate_to_view(self.current_view_name)
        AddPatientModal(self, on_save=on_admitted)

    def open_patient_dossier(self, patient_id):
        """Opens medical record modal for a given patient ID."""
        PatientDossierModal(self, patient_id=patient_id)


def main():
    app = HospitalManagementApp()
    app.mainloop()


if __name__ == "__main__":
    main()
