# views/login_view.py
# The application entry screen — role selection (Kasir / Admin).

from __future__ import annotations
import os
import shutil
import tkinter.messagebox as messagebox
import customtkinter as ctk
from typing import Callable
from views import theme as th
from views.face_recognition_view import FaceLoginWindow, FaceRegistrationWindow


class DeleteFaceWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Hapus Data Wajah")
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()
        
        self.faces = []
        self.base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "faces")
        self._load_faces()
        
        self._build_ui()
        
    def _load_faces(self):
        self.faces = []
        for role in ["kasir", "admin"]:
            role_dir = os.path.join(self.base_dir, role)
            if os.path.exists(role_dir):
                for name in os.listdir(role_dir):
                    name_dir = os.path.join(role_dir, name)
                    if os.path.isdir(name_dir):
                        self.faces.append(f"{name} ({role.title()})")
                        
    def _build_ui(self):
        self.configure(fg_color=th.BG_DARKEST)
        
        ctk.CTkLabel(self, text="Pilih Wajah untuk Dihapus", font=th.FONT_HEADING_MD).pack(pady=20)
        
        if not self.faces:
            ctk.CTkLabel(self, text="Belum ada data wajah terdaftar.", text_color=th.TEXT_SECONDARY).pack()
            ctk.CTkButton(self, text="Tutup", command=self.destroy, **th.btn_ghost()).pack(pady=20)
            return
            
        self.selected_face = ctk.StringVar(value=self.faces[0])
        self.dropdown = ctk.CTkOptionMenu(self, values=self.faces, variable=self.selected_face)
        self.dropdown.pack(pady=10)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame, 
            text="Hapus", 
            command=self._delete_selected, 
            **th.btn_primary(fg_color=th.ACCENT_DANGER, hover_color="#DC2626", width=100)
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame, 
            text="Batal", 
            command=self.destroy, 
            **th.btn_ghost(width=100)
        ).pack(side="left")
        
    def _delete_selected(self):
        selection = self.selected_face.get()
        import re
        match = re.match(r"(.+)\s+\((Kasir|Admin)\)", selection)
        if match:
            name = match.group(1).strip()
            role = match.group(2).lower()
            
            target_dir = os.path.join(self.base_dir, role, name)
            if messagebox.askyesno("Konfirmasi", f"Hapus data wajah untuk {name} ({role.title()})?"):
                try:
                    shutil.rmtree(target_dir)
                    messagebox.showinfo("Berhasil", "Data wajah berhasil dihapus.")
                    self.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal menghapus: {e}")


class LoginView(ctk.CTkFrame):
    """
    Entry screen presented at application startup.

    The user selects their role (Kasir or Admin/Manajer) to proceed
    to the appropriate dashboard.  No password is required in this
    prototype — authentication can be added later.

    Attributes:
        on_login (Callable[[str], None]): Callback invoked with the chosen
                                          role string ("kasir" or "admin").
    """

    def __init__(self, parent, on_login: Callable[[str], None]) -> None:
        super().__init__(parent, fg_color=th.BG_DARKEST)
        self.on_login = on_login
        self._build_ui()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _start_face_registration(self) -> None:
        """Open a camera-based window to register a face sample."""
        FaceRegistrationWindow(
            self.winfo_toplevel(),
            on_done=self.on_login,
            on_cancel=lambda: None,
        )

    def _start_face_login(self, role: str) -> None:
        """Open a camera-based window to log in using a registered face sample."""
        FaceLoginWindow(
            self.winfo_toplevel(),
            role,
            on_done=self.on_login,
            on_cancel=lambda: None,
        )

    def _delete_face_data(self) -> None:
        """Open a window to delete specific face data."""
        DeleteFaceWindow(self.winfo_toplevel())

    def _build_ui(self) -> None:
        self.pack(fill="both", expand=True)

        # ── Center column ────────────────────────────────────────────
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Logo / restaurant name
        ctk.CTkLabel(
            center,
            text="🍽️",
            font=(th.FONT_FAMILY, 56),
        ).pack(pady=(0, th.PAD_SM))

        ctk.CTkLabel(
            center,
            text="RESTO POS",
            font=th.FONT_HEADING_XL,
            text_color=th.ACCENT_PRIMARY,
        ).pack()

        ctk.CTkLabel(
            center,
            text="Sistem Informasi Point of Sales & Manajemen Pemesanan",
            font=th.FONT_BODY_SM,
            text_color=th.TEXT_SECONDARY,
        ).pack(pady=(0, th.PAD_XL))

        # Role selection prompt
        ctk.CTkLabel(
            center,
            text="Pilih Peran Anda",
            font=th.FONT_HEADING_MD,
            text_color=th.TEXT_PRIMARY,
        ).pack(pady=(0, th.PAD_MD))

        ctk.CTkButton(
            center,
            text="Masuk sebagai Kasir",
            command=lambda: self._start_face_login("kasir"),
            **th.btn_primary(width=320, height=52, font=(th.FONT_FAMILY, 15, "bold")),
        ).pack(pady=(0, th.PAD_SM))

        ctk.CTkButton(
            center,
            text="Masuk sebagai Admin / Manajer",
            command=lambda: self._start_face_login("admin"),
            **th.btn_primary(width=320, height=52, font=(th.FONT_FAMILY, 15, "bold")),
        ).pack(pady=(0, th.PAD_XL))

        ctk.CTkLabel(
            center,
            text="Belum punya akses?",
            font=th.FONT_BODY_SM,
            text_color=th.TEXT_SECONDARY,
        ).pack(pady=(0, th.PAD_XS))

        ctk.CTkButton(
            center,
            text="📝 Daftarkan Wajah",
            command=self._start_face_registration,
            **th.btn_ghost(width=320, height=46, font=(th.FONT_FAMILY, 14, "bold")),
        ).pack()

        ctk.CTkButton(
            center,
            text="🗑️ Hapus Data Wajah",
            command=self._delete_face_data,
            **th.btn_ghost(width=320, height=46, font=(th.FONT_FAMILY, 14, "bold"), text_color=th.ACCENT_DANGER),
        ).pack(pady=(th.PAD_SM, 0))

        # Footer
        ctk.CTkLabel(
            center,
            text="v1.0.0  •  © 2026 Resto POS",
            font=th.FONT_BODY_SM,
            text_color=th.TEXT_DISABLED,
        ).pack(pady=(th.PAD_XL, 0))
