import os
import re
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import yt_dlp
except ImportError:
    yt_dlp = None


QUALITY_FORMATS = {
    "أفضل جودة فيديو": "bestvideo+bestaudio/best",
    "1080p أو أقل": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720p أو أقل": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480p أو أقل": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "صوت فقط (MP3)": "bestaudio/best",
}


def is_valid_url(url: str) -> bool:
    return bool(re.match(r"^https?://(www\.)?(youtube\.com|youtu\.be)/", url.strip(), re.I))


def format_bytes(value):
    if not value:
        return "غير معروف"
    units = ["B", "KB", "MB", "GB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024


def bundled_ffmpeg_path() -> str | None:
    """Return the bundled FFmpeg executable path when running from PyInstaller."""
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.append(Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)) / "ffmpeg.exe")
    candidates.append(Path(__file__).resolve().parent / "vendor" / "ffmpeg.exe")
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


class YouTubeDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("منزّل فيديوهات يوتيوب")
        self.geometry("620x430")
        self.minsize(560, 390)
        self.configure(bg="#f6f7fb")
        self.download_running = False
        self._build_ui()

    def _build_ui(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Arial", 20, "bold"), foreground="#172033", background="#f6f7fb")
        style.configure("Subtitle.TLabel", font=("Arial", 10), foreground="#62708a", background="#f6f7fb")
        style.configure("TLabel", font=("Arial", 11), background="#f6f7fb")
        style.configure("TButton", font=("Arial", 11), padding=7)
        style.configure("Accent.TButton", font=("Arial", 12, "bold"), padding=9, foreground="white", background="#246bce")
        style.map("Accent.TButton", background=[("active", "#1957ad"), ("disabled", "#9aa8bd")])
        style.configure("TCombobox", padding=6, font=("Arial", 11))

        main = ttk.Frame(self, padding=(30, 24, 30, 20))
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="منزّل فيديوهات يوتيوب", style="Title.TLabel", anchor="center").pack(fill="x")
        ttk.Label(main, text="الصق الرابط، اختر الجودة والمجلد ثم اضغط تنزيل", style="Subtitle.TLabel", anchor="center").pack(fill="x", pady=(4, 24))

        ttk.Label(main, text="رابط الفيديو", anchor="e").pack(fill="x")
        url_row = ttk.Frame(main)
        url_row.pack(fill="x", pady=(5, 15))
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_row, textvariable=self.url_var, justify="left")
        self.url_entry.pack(fill="x", ipady=6)

        ttk.Label(main, text="الجودة", anchor="e").pack(fill="x")
        self.quality_var = tk.StringVar(value="أفضل جودة فيديو")
        self.quality_box = ttk.Combobox(main, textvariable=self.quality_var, values=list(QUALITY_FORMATS), state="readonly", justify="right")
        self.quality_box.pack(fill="x", pady=(5, 15))

        ttk.Label(main, text="مجلد الحفظ", anchor="e").pack(fill="x")
        folder_row = ttk.Frame(main)
        folder_row.pack(fill="x", pady=(5, 20))
        self.folder_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        ttk.Entry(folder_row, textvariable=self.folder_var, justify="left").pack(side="left", fill="x", expand=True, ipady=6)
        ttk.Button(folder_row, text="اختيار...", command=self.choose_folder).pack(side="right", padx=(8, 0))

        self.progress = ttk.Progressbar(main, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(0, 7))
        self.status_var = tk.StringVar(value="جاهز للتنزيل")
        ttk.Label(main, textvariable=self.status_var, foreground="#62708a", anchor="center").pack(fill="x")

        self.download_button = ttk.Button(main, text="بدء التنزيل", style="Accent.TButton", command=self.start_download)
        self.download_button.pack(fill="x", pady=(18, 0))

        ttk.Label(main, text="استخدم البرنامج لتنزيل المحتوى الذي تملك حق تنزيله أو لديك إذن باستخدامه.", style="Subtitle.TLabel", wraplength=540, anchor="center").pack(fill="x", pady=(16, 0))

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_var.get() or os.path.expanduser("~"))
        if folder:
            self.folder_var.set(folder)

    def start_download(self):
        if self.download_running:
            return
        url = self.url_var.get().strip()
        folder = os.path.expanduser(self.folder_var.get().strip())
        quality = self.quality_var.get()

        if yt_dlp is None:
            messagebox.showerror("مكتبة ناقصة", "ثبّت المتطلبات أولاً عبر الأمر: pip install -r requirements.txt")
            return
        if not is_valid_url(url):
            messagebox.showwarning("رابط غير صحيح", "من فضلك الصق رابطًا صحيحًا من YouTube.")
            self.url_entry.focus_set()
            return
        if not folder:
            messagebox.showwarning("مجلد غير محدد", "اختر مجلدًا لحفظ الفيديو.")
            return
        try:
            os.makedirs(folder, exist_ok=True)
        except OSError as exc:
            messagebox.showerror("خطأ في المجلد", str(exc))
            return

        self.download_running = True
        self.download_button.configure(state="disabled")
        self.progress.configure(mode="indeterminate")
        self.progress.start(10)
        self.status_var.set("جارٍ تجهيز الفيديو...")
        threading.Thread(target=self._download, args=(url, folder, quality), daemon=True).start()

    def _progress_hook(self, data):
        if data.get("status") != "downloading":
            return
        total = data.get("total_bytes") or data.get("total_bytes_estimate")
        downloaded = data.get("downloaded_bytes", 0)
        speed = data.get("speed")
        if total:
            percent = downloaded / total * 100
            text = f"جارٍ التنزيل: {percent:.1f}% — {format_bytes(downloaded)} من {format_bytes(total)}"
            if speed:
                text += f" — {format_bytes(speed)}/ث"
            self.after(0, self._set_progress, percent, text)

    def _set_progress(self, percent, text):
        self.progress.stop()
        self.progress.configure(mode="determinate", value=percent)
        self.status_var.set(text)

    def _download(self, url, folder, quality):
        is_audio = quality == "صوت فقط (MP3)"
        options = {
            "format": QUALITY_FORMATS[quality],
            "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
            "progress_hooks": [self._progress_hook],
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "merge_output_format": "mp4",
        }
        ffmpeg_path = bundled_ffmpeg_path()
        if ffmpeg_path:
            options["ffmpeg_location"] = str(Path(ffmpeg_path).parent)
        if is_audio:
            options["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                downloader.download([url])
            self.after(0, self._download_finished, True, "تم التنزيل بنجاح")
        except Exception as exc:
            error = str(exc).split("\\n")[-1][:300]
            self.after(0, self._download_finished, False, error or "حدث خطأ أثناء التنزيل")

    def _download_finished(self, success, message):
        self.download_running = False
        self.download_button.configure(state="normal")
        self.progress.stop()
        if success:
            self.progress.configure(value=100, mode="determinate")
            self.status_var.set(message)
            messagebox.showinfo("اكتمل التنزيل", message)
        else:
            self.progress.configure(value=0, mode="determinate")
            self.status_var.set("فشل التنزيل")
            messagebox.showerror("تعذر التنزيل", message)


if __name__ == "__main__":
    YouTubeDownloader().mainloop()
