from __future__ import annotations

import os
import tkinter.messagebox as messagebox

import customtkinter as ctk
import numpy as np
from PIL import Image, ImageOps

try:
    import cv2
except ImportError:  # pragma: no cover - depends on environment
    cv2 = None

from views import theme as th


class _BaseFaceWindow(ctk.CTkToplevel):
    """Base camera window for face registration and face login."""

    def __init__(self, parent, role: str, on_done, on_cancel) -> None:
        super().__init__(parent)
        self.role = role
        self.on_done = on_done
        self.on_cancel = on_cancel

        self.title("Face Access")
        self.geometry("760x620")
        self.minsize(720, 560)
        self.configure(fg_color=th.BG_DARKEST)
        self.transient(parent)
        self.grab_set()
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()
        self.update_idletasks()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        self._camera = None
        self._face_cascade = None
        self._verified = False
        self._detected_frames = 0
        self._build_ui()

        if cv2 is None:
            self.status_label.configure(text="OpenCV belum terinstal. Anda dapat melanjutkan secara manual.")
            self.continue_button.configure(state="normal")
            self.after(150, self._show_dependency_warning)
            return

        self.after(150, self._start_camera)

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(24, 12), sticky="ew")
        header.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=self._title,
            font=th.FONT_HEADING_MD,
            text_color=th.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text=self._subtitle,
            font=th.FONT_BODY_SM,
            text_color=th.TEXT_SECONDARY,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.video_label = ctk.CTkLabel(
            self,
            text="Menyiapkan kamera...",
            width=640,
            height=460,
            fg_color=th.BG_DARK,
            corner_radius=16,
        )
        self.video_label.grid(row=1, column=0, padx=24, pady=(0, 12), sticky="nsew")

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, padx=24, pady=(0, 24), sticky="ew")
        footer.columnconfigure(0, weight=1)
        footer.columnconfigure(1, weight=0)

        self.status_label = ctk.CTkLabel(
            footer,
            text="Mencari kamera...",
            font=th.FONT_BODY_SM,
            text_color=th.TEXT_SECONDARY,
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        button_row = ctk.CTkFrame(footer, fg_color="transparent")
        button_row.grid(row=0, column=1, sticky="e")

        self.continue_button = ctk.CTkButton(
            button_row,
            text="Lanjutkan",
            command=self._finish_action,
            state="normal",
            **th.btn_primary(width=140, height=40),
        )
        self.continue_button.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            button_row,
            text="Batal",
            command=self._cancel,
            **th.btn_ghost(width=120, height=40),
        ).pack(side="left")

    @property
    def _title(self) -> str:
        return ""  # implemented by subclasses

    @property
    def _subtitle(self) -> str:
        return ""

    def _show_dependency_warning(self) -> None:
        messagebox.showwarning(
            "Face Access",
            "OpenCV belum terinstal. Aplikasi tetap bisa dilanjutkan secara manual.",
        )

    def _start_camera(self) -> None:
        self.status_label.configure(text="Mencoba menghubungkan kamera...")
        self._camera = self._open_camera()
        if self._camera is None:
            self.status_label.configure(text="Kamera tidak terdeteksi. Pastikan kamera sudah aktif dan diizinkan.")
            self.continue_button.configure(state="normal")
            return

        self._face_cascade = self._load_face_cascade()
        self.status_label.configure(text="Kamera terhubung. Menampilkan preview...")
        self._update_frame()

    def _open_camera(self):
        if cv2 is None:
            return None

        backends = []
        if hasattr(cv2, "CAP_DSHOW"):
            backends.append(cv2.CAP_DSHOW)
        if hasattr(cv2, "CAP_MSMF"):
            backends.append(cv2.CAP_MSMF)
        backends.append(cv2.CAP_ANY)

        for index in range(3):
            for backend in backends:
                try:
                    cap = cv2.VideoCapture(index, backend)
                    if cap.isOpened():
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        return cap
                    cap.release()
                except Exception:
                    continue

        return None

    def _load_face_cascade(self):
        try:
            cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            if cascade.empty():
                return None
            return cascade
        except Exception:
            return None

    def _extract_face(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self._face_cascade is None:
            return None, None, gray

        try:
            faces = self._face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(80, 80),
            )
        except Exception:
            faces = []

        if len(faces) == 0:
            return None, None, gray

        x, y, w, h = faces[0]
        face_region = gray[y:y + h, x:x + w]
        face_region = cv2.resize(face_region, (100, 100))
        return face_region, (x, y, w, h), gray

    def _draw_face_box(self, frame, box):
        if box is None:
            return frame
        x, y, w, h = box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return frame

    def _update_frame(self) -> None:
        if self._verified or not self.winfo_exists():
            return

        if self._camera is None or not self._camera.isOpened():
            self.after(200, self._update_frame)
            return

        ret, frame = self._camera.read()
        if ret:
            face_region, box, _ = self._extract_face(frame)
            frame = self._draw_face_box(frame, box)
            self._handle_frame(face_region, box, frame)
        else:
            self.status_label.configure(text="Kamera belum memberikan frame. Coba lagi.")
            self._camera.release()
            self._camera = None
            self.after(500, self._start_camera)
            return

        self.after(15, self._update_frame)

    def _handle_frame(self, face_region, box, frame) -> None:
        raise NotImplementedError

    def _finish_action(self) -> None:
        self._verified = True
        self._cleanup()
        self.on_done(self.role)
        self.destroy()

    def _cancel(self) -> None:
        self._cleanup()
        self.on_cancel()
        self.destroy()

    def _cleanup(self) -> None:
        if self._camera is not None and self._camera.isOpened():
            self._camera.release()


class FaceRegistrationWindow(_BaseFaceWindow):
    """Register a face sample for the selected role."""

    def __init__(self, parent, role: str, on_done, on_cancel) -> None:
        self._sample_count = 0
        self._sample_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "faces", role)
        super().__init__(parent, role, on_done, on_cancel)

    @property
    def _title(self) -> str:
        return f"Daftarkan wajah untuk {self.role}"

    @property
    def _subtitle(self) -> str:
        return "Posisikan wajah Anda di depan kamera. Sistem akan menyimpan beberapa sampel wajah."

    def _handle_frame(self, face_region, box, frame) -> None:
        if face_region is None:
            self._detected_frames = max(0, self._detected_frames - 1)
            self.status_label.configure(text="Belum ada wajah yang terlihat. Arahkan wajah ke kamera.")
        else:
            self._detected_frames += 1
            if self._detected_frames >= 5:
                self._save_face_sample(face_region)
                self._detected_frames = 0
                self.status_label.configure(text=f"Sampel wajah tersimpan ({self._sample_count}/3)")
            else:
                self.status_label.configure(text=f"Menjaga posisi wajah... {self._detected_frames}/5")

        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        image = ImageOps.contain(image, (640, 460))
        ctk_image = ctk.CTkImage(light_image=image, size=image.size)
        self.video_label.configure(image=ctk_image, text="")
        self.video_label.image = ctk_image

    def _save_face_sample(self, face_region) -> None:
        os.makedirs(self._sample_dir, exist_ok=True)
        if self._sample_count >= 3:
            self.status_label.configure(text="Pendaftaran wajah selesai. Anda bisa menutup jendela ini.")
            self.continue_button.configure(text="Selesai")
            self._verified = True
            self.after(600, self._finish_action)
            return

        hist = self._compute_hist(face_region)
        path = os.path.join(self._sample_dir, f"sample_{self._sample_count + 1}.npy")
        np.save(path, hist)
        self._sample_count += 1

        if self._sample_count >= 3:
            self.status_label.configure(text="Pendaftaran wajah selesai. Anda bisa menutup jendela ini.")
            self.continue_button.configure(text="Selesai")
            self._verified = True
            self.after(600, self._finish_action)
        else:
            self.status_label.configure(text=f"Sampel wajah tersimpan ({self._sample_count}/3)")

    def _compute_hist(self, face_region):
        hist = cv2.calcHist([face_region], [0], None, [32], [0, 256])
        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
        return hist


class FaceLoginWindow(_BaseFaceWindow):
    """Login using a previously registered face sample."""

    def __init__(self, parent, role: str, on_done, on_cancel) -> None:
        self._registered_histograms = []
        self._sample_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "faces", role)
        super().__init__(parent, role, on_done, on_cancel)
        self._load_registered_histograms()

    @property
    def _title(self) -> str:
        return f"Login wajah untuk {self.role}"

    @property
    def _subtitle(self) -> str:
        return "Arahkan wajah Anda ke kamera. Jika cocok dengan data yang sudah didaftarkan, Anda akan masuk."

    def _load_registered_histograms(self) -> None:
        if not os.path.isdir(self._sample_dir):
            self._registered_histograms = []
            return

        self._registered_histograms = []
        for file_name in sorted(os.listdir(self._sample_dir)):
            if file_name.endswith(".npy"):
                path = os.path.join(self._sample_dir, file_name)
                hist = np.load(path)
                self._registered_histograms.append(hist)

    def _handle_frame(self, face_region, box, frame) -> None:
        if face_region is None:
            self._detected_frames = max(0, self._detected_frames - 1)
            self.status_label.configure(text="Belum ada wajah yang terlihat.")
        else:
            self._detected_frames += 1
            if self._detected_frames >= 4:
                match_score = self._match_face(face_region)
                if match_score is not None and match_score >= 0.55:
                    self._verified = True
                    self.status_label.configure(text="Wajah cocok. Mengalihkan ke dashboard...")
                    self.after(500, self._finish_action)
                else:
                    self.status_label.configure(text="Wajah belum cocok. Daftarkan wajah dulu atau coba lagi.")
                    self._detected_frames = 0
            else:
                self.status_label.configure(text=f"Mencocokkan wajah... {self._detected_frames}/4")

        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        image = ImageOps.contain(image, (640, 460))
        ctk_image = ctk.CTkImage(light_image=image, size=image.size)
        self.video_label.configure(image=ctk_image, text="")
        self.video_label.image = ctk_image

    def _match_face(self, face_region):
        if not self._registered_histograms:
            return None

        current_hist = self._compute_hist(face_region)
        scores = []
        for registered_hist in self._registered_histograms:
            score = cv2.compareHist(current_hist, registered_hist, cv2.HISTCMP_CORREL)
            scores.append(float(score))

        if not scores:
            return None
        return max(scores)

    def _compute_hist(self, face_region):
        hist = cv2.calcHist([face_region], [0], None, [32], [0, 256])
        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
        return hist
