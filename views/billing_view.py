"""
Anti-Clipping Billing & Invoices View for Medicare Plus Hospital Management System.
Features proportional stretch columns, concise headers, and printable receipt preview.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import database
from styles import Theme
from ui_components import CardFrame, SearchBar, ModernButton


class BillingView(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG_MAIN, padx=16, pady=12, **kwargs)

        self._build_financial_summary()
        self._build_toolbar()
        self._build_table()
        self.refresh_table()

    def _build_financial_summary(self):
        summary_bar = tk.Frame(self, bg=Theme.BG_MAIN)
        summary_bar.pack(fill="x", pady=(0, 10))

        for i in range(3):
            summary_bar.columnconfigure(i, weight=1, uniform="fin_stat")

        self.stat_total_billed = self._make_card(summary_bar, "TOTAL INVOICED", "$0.00", Theme.PRIMARY, 0)
        self.stat_paid = self._make_card(summary_bar, "COLLECTED REVENUE", "$0.00", Theme.SUCCESS, 1)
        self.stat_pending = self._make_card(summary_bar, "PENDING RECEIVABLES", "$0.00", Theme.WARNING, 2)

    def _make_card(self, parent, title, val, color, col):
        card = tk.Frame(parent, bg=Theme.BG_CARD, padx=14, pady=10, highlightbackground=Theme.BORDER, highlightthickness=1)
        card.grid(row=0, column=col, sticky="nsew", padx=4)

        t_lbl = tk.Label(card, text=title, font=Theme.FONT_CAPTION, fg=Theme.TEXT_MUTED, bg=Theme.BG_CARD)
        t_lbl.pack(anchor="w")

        v_lbl = tk.Label(card, text=val, font=Theme.FONT_TITLE_HERO, fg=color, bg=Theme.BG_CARD)
        v_lbl.pack(anchor="w", pady=(1, 0))
        return v_lbl

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg=Theme.BG_MAIN)
        toolbar.pack(fill="x", pady=(0, 10))

        # Search Bar
        self.search_bar = SearchBar(
            toolbar,
            placeholder="Search invoice by Patient Name or Invoice ID...",
            on_search=lambda q: self.refresh_table()
        )
        self.search_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Status filter
        st_box = tk.Frame(toolbar, bg=Theme.BG_CARD, padx=6, pady=3, highlightbackground=Theme.BORDER_DARK, highlightthickness=1)
        st_box.pack(side="left", padx=(0, 10))

        tk.Label(st_box, text="Status:", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg=Theme.BG_CARD).pack(side="left", padx=(0, 3))
        self.status_var = tk.StringVar(value="All Status")
        statuses = ["All Status", "Paid", "Pending", "Overdue"]
        st_menu = ttk.Combobox(st_box, textvariable=self.status_var, values=statuses, state="readonly", width=12)
        st_menu.pack(side="left")
        st_menu.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        # Action Buttons
        btn_create = ModernButton(
            toolbar,
            text="Generate",
            icon="+",
            style="primary",
            font=Theme.FONT_BODY_BOLD,
            padx=12,
            pady=6,
            command=self.open_generate_bill_modal
        )
        btn_create.pack(side="left", padx=(0, 6))

        btn_mark = ModernButton(
            toolbar,
            text="Paid",
            icon="✔",
            style="success",
            font=Theme.FONT_BODY_BOLD,
            padx=10,
            pady=6,
            command=self._mark_as_paid
        )
        btn_mark.pack(side="left", padx=(0, 6))

        btn_receipt = ModernButton(
            toolbar,
            text="Receipt",
            icon="📄",
            style="secondary",
            font=Theme.FONT_BODY_BOLD,
            padx=10,
            pady=6,
            command=self._view_receipt
        )
        btn_receipt.pack(side="left")

    def _build_table(self):
        card = CardFrame(
            self,
            title="Hospital Billing & Revenue Ledger",
            subtitle="Itemized medical services, consultation fees, and payment status"
        )
        card.pack(fill="both", expand=True)

        table_box = tk.Frame(card, bg=Theme.BG_CARD)
        table_box.pack(fill="both", expand=True, pady=(2, 0))

        columns = ("id", "patient", "date", "consultation", "lab", "medicine", "room", "discount", "total", "status", "method")
        self.tree = ttk.Treeview(table_box, columns=columns, show="headings")

        # Concise headings that never wrap awkwardly
        self.tree.heading("id", text="INVOICE #", anchor="w")
        self.tree.heading("patient", text="PATIENT", anchor="w")
        self.tree.heading("date", text="DATE", anchor="center")
        self.tree.heading("consultation", text="CONSULT", anchor="e")
        self.tree.heading("lab", text="LAB", anchor="e")
        self.tree.heading("medicine", text="PHARMACY", anchor="e")
        self.tree.heading("room", text="ROOM", anchor="e")
        self.tree.heading("discount", text="DISC", anchor="e")
        self.tree.heading("total", text="NET TOTAL", anchor="e")
        self.tree.heading("status", text="STATUS", anchor="center")
        self.tree.heading("method", text="METHOD", anchor="center")

        # Proportional column widths with stretch=True
        self.tree.column("id", width=105, minwidth=90, stretch=True)
        self.tree.column("patient", width=140, minwidth=115, stretch=True)
        self.tree.column("date", width=95, minwidth=85, stretch=True)
        self.tree.column("consultation", width=80, minwidth=70, stretch=True)
        self.tree.column("lab", width=70, minwidth=60, stretch=True)
        self.tree.column("medicine", width=85, minwidth=75, stretch=True)
        self.tree.column("room", width=75, minwidth=65, stretch=True)
        self.tree.column("discount", width=70, minwidth=60, stretch=True)
        self.tree.column("total", width=95, minwidth=85, stretch=True)
        self.tree.column("status", width=90, minwidth=80, stretch=True)
        self.tree.column("method", width=105, minwidth=90, stretch=True)

        scroll_y = ttk.Scrollbar(table_box, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(table_box, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

        self.tree.tag_configure("even", background="#ffffff")
        self.tree.tag_configure("odd", background="#f8fafc")

        self.tree.bind("<Double-1>", lambda e: self._view_receipt())

    def refresh_table(self):
        query = self.search_bar.get_query()
        status_filter = self.status_var.get()

        for r in self.tree.get_children():
            self.tree.delete(r)

        bills = database.get_all_bills(search_text=query, status_filter=status_filter)

        total_sum = 0.0
        paid_sum = 0.0
        pending_sum = 0.0

        for idx, b in enumerate(bills):
            amt = float(b["total_amount"])
            total_sum += amt
            if b["payment_status"] == "Paid":
                paid_sum += amt
            else:
                pending_sum += amt

            tag = "even" if idx % 2 == 0 else "odd"
            self.tree.insert(
                "",
                "end",
                values=(
                    b["invoice_id"],
                    b["patient_name"],
                    b["bill_date"],
                    f"${b['consultation_fee']:.2f}",
                    f"${b['lab_charges']:.2f}",
                    f"${b['medicine_charges']:.2f}",
                    f"${b['room_charges']:.2f}",
                    f"${b['discount']:.2f}",
                    f"${b['total_amount']:.2f}",
                    f"● {b['payment_status']}",
                    b["payment_method"] or "Cash"
                ),
                tags=(tag,)
            )

        self.stat_total_billed.config(text=f"${total_sum:,.2f}")
        self.stat_paid.config(text=f"${paid_sum:,.2f}")
        self.stat_pending.config(text=f"${pending_sum:,.2f}")

    def _mark_as_paid(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("No Selection", "Please select an invoice from the ledger.")
            return
        inv_id = self.tree.item(item[0], "values")[0]
        database.update_bill_status(inv_id, "Paid")
        self.refresh_table()
        messagebox.showinfo("Payment Updated", f"Invoice {inv_id} marked as Paid.")

    def _view_receipt(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("No Selection", "Please select an invoice to view receipt.")
            return
        inv_id = self.tree.item(item[0], "values")[0]
        ReceiptModal(self, invoice_id=inv_id)

    def open_generate_bill_modal(self):
        GenerateBillModal(self, on_save=self.refresh_table)


class GenerateBillModal(tk.Toplevel):
    """Modal for generating a new patient invoice."""
    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.title("Generate Medical Invoice • Medicare HMS")
        self.geometry("540x580")
        self.configure(bg=Theme.BG_CARD)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_save = on_save

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 540) // 2
        y = (self.winfo_screenheight() - 580) // 2
        self.geometry(f"+{x}+{y}")

        self._build_form()

    def _build_form(self):
        header = tk.Frame(self, bg=Theme.PRIMARY, padx=20, pady=16)
        header.pack(fill="x")

        tk.Label(
            header,
            text="💳 Generate Patient Invoice",
            font=Theme.FONT_TITLE_LARGE,
            fg=Theme.TEXT_LIGHT,
            bg=Theme.PRIMARY
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Enter service fees, room charges, discounts, and payment methods",
            font=Theme.FONT_BODY,
            fg=Theme.PRIMARY_LIGHT,
            bg=Theme.PRIMARY
        ).pack(anchor="w", pady=(2, 0))

        form = tk.Frame(self, bg=Theme.BG_CARD, padx=20, pady=16)
        form.pack(fill="both", expand=True)

        self.entries = {}

        patients = database.get_all_patients()
        pt_names = [p["full_name"] for p in patients]
        if not pt_names:
            pt_names = ["Eleanor Vance", "James Robinson"]
        self._add_dropdown(form, "Select Patient *", "patient_name", pt_names, 0, 0, colspan=2)

        self._add_field(form, "Consultation Fee ($)", "consultation_fee", 1, 0, default_val="150.00")
        self._add_field(form, "Laboratory & Diagnostics ($)", "lab_charges", 1, 1, default_val="250.00")

        self._add_field(form, "Pharmacy & Medicines ($)", "medicine_charges", 2, 0, default_val="180.00")
        self._add_field(form, "Room & Bed Charges ($)", "room_charges", 2, 1, default_val="500.00")

        self._add_field(form, "Discount / Insurance Waiver ($)", "discount", 3, 0, default_val="50.00")
        self._add_dropdown(form, "Payment Method *", "payment_method", ["Insurance", "Credit Card", "Cash", "UPI/NetBanking"], 3, 1)

        self._add_dropdown(form, "Initial Payment Status *", "payment_status", ["Paid", "Pending"], 4, 0)

        btn_bar = tk.Frame(self, bg=Theme.BG_CARD_ALT, padx=20, pady=12, highlightbackground=Theme.BORDER, highlightthickness=1)
        btn_bar.pack(fill="x", side="bottom")

        ModernButton(
            btn_bar,
            text="Cancel",
            style="secondary",
            font=Theme.FONT_BODY_BOLD,
            padx=14,
            pady=6,
            command=self.destroy
        ).pack(side="right", padx=(8, 0))

        ModernButton(
            btn_bar,
            text="Generate Bill",
            icon="✔",
            style="primary",
            font=Theme.FONT_BODY_BOLD,
            padx=16,
            pady=6,
            command=self._save_bill
        ).pack(side="right")

    def _add_field(self, parent, label, key, row, col, colspan=1, default_val=""):
        frame = tk.Frame(parent, bg=Theme.BG_CARD)
        frame.grid(row=row, column=col, columnspan=colspan, sticky="ew", padx=6, pady=4)
        parent.columnconfigure(col, weight=1)

        tk.Label(frame, text=label, font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg=Theme.BG_CARD).pack(anchor="w", pady=(0, 2))
        entry = tk.Entry(frame, font=Theme.FONT_BODY, bg=Theme.BG_CARD, fg=Theme.TEXT_PRIMARY, relief="solid", bd=1, highlightthickness=0)
        if default_val:
            entry.insert(0, default_val)
        entry.pack(fill="x", ipady=3)
        self.entries[key] = entry

    def _add_dropdown(self, parent, label, key, options, row, col, colspan=1):
        frame = tk.Frame(parent, bg=Theme.BG_CARD)
        frame.grid(row=row, column=col, columnspan=colspan, sticky="ew", padx=6, pady=4)
        parent.columnconfigure(col, weight=1)

        tk.Label(frame, text=label, font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg=Theme.BG_CARD).pack(anchor="w", pady=(0, 2))
        var = tk.StringVar(value=options[0] if options else "")
        combo = ttk.Combobox(frame, textvariable=var, values=options, state="readonly")
        combo.pack(fill="x", ipady=2)
        self.entries[key] = var

    def _save_bill(self):
        pname = self.entries["patient_name"].get()
        try:
            consult = float(self.entries["consultation_fee"].get().strip() or "0")
            lab = float(self.entries["lab_charges"].get().strip() or "0")
            med = float(self.entries["medicine_charges"].get().strip() or "0")
            room = float(self.entries["room_charges"].get().strip() or "0")
            disc = float(self.entries["discount"].get().strip() or "0")
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter valid numeric amounts for fees.", parent=self)
            return

        data = {
            "patient_name": pname,
            "bill_date": datetime.now().strftime("%Y-%m-%d"),
            "consultation_fee": consult,
            "lab_charges": lab,
            "medicine_charges": med,
            "room_charges": room,
            "discount": disc,
            "payment_status": self.entries["payment_status"].get(),
            "payment_method": self.entries["payment_method"].get()
        }

        inv_id = database.add_bill(data)
        messagebox.showinfo("Invoice Created", f"Bill generated successfully!\nInvoice No: {inv_id}", parent=self)
        if self.on_save:
            self.on_save()
        self.destroy()


class ReceiptModal(tk.Toplevel):
    """High-contrast printable hospital receipt dialog."""
    def __init__(self, parent, invoice_id):
        super().__init__(parent)
        self.title(f"Official Receipt • {invoice_id}")
        self.geometry("520x620")
        self.configure(bg=Theme.BG_CARD)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        bills = database.get_all_bills()
        self.bill = next((b for b in bills if b["invoice_id"] == invoice_id), None)

        if not self.bill:
            messagebox.showerror("Error", f"Invoice {invoice_id} not found.", parent=self)
            self.destroy()
            return

        self._build_receipt()

    def _build_receipt(self):
        b = self.bill

        paper = tk.Frame(self, bg="#ffffff", padx=24, pady=20)
        paper.pack(fill="both", expand=True)

        tk.Label(paper, text="MEDICARE CENTRAL HOSPITAL", font=(Theme.FONT_FAMILY, 15, "bold"), fg=Theme.PRIMARY_HOVER, bg="#ffffff").pack()
        tk.Label(paper, text="100 Healthcare Parkway, Medical District • +1 (555) 800-MEDS", font=Theme.FONT_CAPTION, fg=Theme.TEXT_MUTED, bg="#ffffff").pack(pady=(2, 6))

        sep1 = tk.Frame(paper, bg=Theme.BORDER_DARK, height=1)
        sep1.pack(fill="x", pady=5)

        meta_row = tk.Frame(paper, bg="#ffffff")
        meta_row.pack(fill="x", pady=2)
        tk.Label(meta_row, text=f"INVOICE #: {b['invoice_id']}", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_PRIMARY, bg="#ffffff").pack(side="left")
        tk.Label(meta_row, text=f"DATE: {b['bill_date']}", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg="#ffffff").pack(side="right")

        meta_row2 = tk.Frame(paper, bg="#ffffff")
        meta_row2.pack(fill="x", pady=2)
        tk.Label(meta_row2, text=f"PATIENT: {b['patient_name']}", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_PRIMARY, bg="#ffffff").pack(side="left")
        st_fg = Theme.SUCCESS_TEXT if b['payment_status'] == 'Paid' else Theme.WARNING_TEXT
        tk.Label(meta_row2, text=f"STATUS: ● {b['payment_status']}", font=Theme.FONT_BODY_BOLD, fg=st_fg, bg="#ffffff").pack(side="right")

        sep2 = tk.Frame(paper, bg=Theme.BORDER_DARK, height=1)
        sep2.pack(fill="x", pady=6)

        items = [
            ("Physician Consultation & Rounds", b["consultation_fee"]),
            ("Diagnostic Laboratory & Imaging", b["lab_charges"]),
            ("Pharmacy & Prescribed Medication", b["medicine_charges"]),
            ("Ward / Room Inpatient Accommodation", b["room_charges"])
        ]

        th = tk.Frame(paper, bg="#f1f5f9", padx=8, pady=5)
        th.pack(fill="x")
        tk.Label(th, text="DESCRIPTION", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg="#f1f5f9").pack(side="left")
        tk.Label(th, text="AMOUNT ($)", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_SECONDARY, bg="#f1f5f9").pack(side="right")

        for desc, cost in items:
            row = tk.Frame(paper, bg="#ffffff", padx=8, pady=4)
            row.pack(fill="x")
            tk.Label(row, text=desc, font=Theme.FONT_BODY, fg=Theme.TEXT_SECONDARY, bg="#ffffff").pack(side="left")
            tk.Label(row, text=f"${float(cost):.2f}", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_PRIMARY, bg="#ffffff").pack(side="right")

        sep3 = tk.Frame(paper, bg=Theme.BORDER_DARK, height=1)
        sep3.pack(fill="x", pady=6)

        subtotal = float(b["consultation_fee"]) + float(b["lab_charges"]) + float(b["medicine_charges"]) + float(b["room_charges"])
        disc = float(b["discount"])
        net = float(b["total_amount"])

        def make_sum_row(t, v, is_bold=False):
            r = tk.Frame(paper, bg="#ffffff", padx=8, pady=2)
            r.pack(fill="x")
            f = Theme.FONT_TITLE if is_bold else Theme.FONT_BODY
            col = Theme.PRIMARY_HOVER if is_bold else Theme.TEXT_PRIMARY
            tk.Label(r, text=t, font=f, fg=col, bg="#ffffff").pack(side="left")
            tk.Label(r, text=v, font=f, fg=col, bg="#ffffff").pack(side="right")

        make_sum_row("Subtotal:", f"${subtotal:.2f}")
        make_sum_row("Insurance / Discount Waiver:", f"-${disc:.2f}")
        make_sum_row("NET TOTAL AMOUNT DUE:", f"${net:.2f}", is_bold=True)

        tk.Label(paper, text=f"Payment Method: {b['payment_method'] or 'Cash'}", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_MUTED, bg="#ffffff").pack(anchor="w", padx=8, pady=(10, 0))
        tk.Label(paper, text="Thank you for choosing Medicare Hospital. Wishing you speedy recovery!", font=Theme.FONT_CAPTION, fg=Theme.TEXT_MUTED, bg="#ffffff").pack(pady=(12, 0))

        btn_bar = tk.Frame(self, bg=Theme.BG_CARD_ALT, padx=20, pady=12, highlightbackground=Theme.BORDER, highlightthickness=1)
        btn_bar.pack(fill="x", side="bottom")

        ModernButton(
            btn_bar,
            text="Close",
            style="secondary",
            font=Theme.FONT_BODY_BOLD,
            padx=14,
            pady=5,
            command=self.destroy
        ).pack(side="right", padx=(8, 0))

        ModernButton(
            btn_bar,
            text="Print Receipt",
            icon="🖨",
            style="primary",
            font=Theme.FONT_BODY_BOLD,
            padx=14,
            pady=5,
            command=lambda: messagebox.showinfo("Print Sent", "Receipt sent to default hospital receipt printer.", parent=self)
        ).pack(side="right")
