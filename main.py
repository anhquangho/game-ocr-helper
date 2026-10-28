###############################################
# Game OCR Helper — Tóm tắt nhanh (overview)
#
# - Mục đích: Hỗ trợ đọc nhanh chữ (OCR) trong game ở 1 vùng màn hình do người dùng chỉ định.
# - Cách dùng nhanh: Mở app, chỉnh vùng chụp (top/left/width/height) nếu cần, sau đó chuyển qua game và nhấn TAB.
# - Hotkey: Phím TAB (global) — được đăng ký bằng thư viện `keyboard`, sự kiện được chuyển về main thread Tk qua `root.after`.
# - Luồng chính khi nhấn TAB:
#     1) capture_region() chụp vùng -> PIL.Image
#     2) get_text_from_image(): grayscale + threshold(150) -> pytesseract OCR (lang=OCR_LANG)
#     3) Nếu có text: cập nhật preview + các cửa sổ phụ (Live/OBS) và hiển thị text trong khung kết quả.
# - UI chính (Tkinter + ttk):
#     • Khối cấu hình vùng chụp bằng Spinbox
#     • Nút: Áp dụng, Chụp thử, Kiểm tra vùng (Live), Mở cửa sổ Output (OBS)
#     • Khu preview ảnh và khung kết quả có scrollbar
# - Cửa sổ phụ:
#     • Live Preview: cập nhật ảnh khi nhấn TAB (fit theo width của cửa sổ)
#     • OBS Output: cửa sổ riêng kích thước = vùng chụp, ảnh được set khi nhấn TAB
# - Xử lý OCR: dùng `pytesseract` (đường dẫn Tesseract chỉ định trong biến tesseract_cmd). Mặc định OCR_LANG = "eng".
# - Phụ thuộc chính: mss (chụp màn hình), opencv-python, pytesseract, Pillow (PIL), tkinter, keyboard, numpy.
# - Lưu ý/giới hạn:
#     • Đường dẫn Tesseract hiện hard-code. Cần cài đúng và có quyền truy cập.
#     • Chỉ cập nhật khi nhấn TAB (không có vòng lặp auto).
#     • Chất lượng OCR phụ thuộc tiền xử lý ảnh/độ tương phản UI game và gói ngôn ngữ Tesseract đã cài.
#     • Keyboard hook có thể cần quyền admin trên Windows.
# - Gợi ý mở rộng (nếu cần):
#     • Thêm chế độ auto-polling theo chu kỳ; tinh chỉnh tiền xử lý (blur/adaptive threshold);
#     • Parser/regex để trích thông tin quan trọng; lưu log kết quả; hỗ trợ đa vùng.
###############################################
import mss
import cv2
import pytesseract
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
import tkinter.ttk as ttk
import keyboard
import os
import sys

# Cấu hình stdout/stderr về UTF-8 để tránh UnicodeEncodeError khi in tiếng Việt trên PowerShell
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
    sys.stderr.reconfigure(encoding="utf-8", errors="ignore")
except Exception:
    pass

# --- CONFIG ---
# Chỉ định đường dẫn Tesseract (sửa nếu bạn cài ở nơi khác)
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Ngôn ngữ OCR (mặc định 'eng'). Nếu muốn OCR tiếng Việt, đặt thành 'vie' và đảm bảo đã cài vie.traineddata trong tessdata
OCR_LANG = "eng"

# Vùng chụp màn hình (bạn chỉnh theo độ phân giải và UI game)
REGION = {"top": 120, "left": 1520, "width": 400, "height": 400}


def capture_region(region):
    """Chụp vùng màn hình theo dict region {top,left,width,height}"""
    with mss.mss() as sct:
        img = sct.grab(region)
        return Image.frombytes("RGB", img.size, img.rgb)

def get_text_from_image(pil_img):
    """OCR ảnh sang text đơn giản để kiểm tra nội dung."""
    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(thresh, lang=OCR_LANG)
    return text.strip()


class OCRApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Game OCR Helper")

        # Biến vùng chụp (có thể chỉnh trong UI)
        self.top_var = tk.IntVar(value=REGION["top"])
        self.left_var = tk.IntVar(value=REGION["left"])
        self.width_var = tk.IntVar(value=REGION["width"])
        self.height_var = tk.IntVar(value=REGION["height"])

        # Khu điều khiển vùng chụp
        ctrl = ttk.LabelFrame(self.root, text="Vùng chụp (top, left, width, height)")
        ctrl.pack(fill="x", padx=10, pady=8)

        ttk.Label(ctrl, text="Top").grid(row=0, column=0, padx=5, pady=4, sticky="e")
        ttk.Label(ctrl, text="Left").grid(row=0, column=2, padx=5, pady=4, sticky="e")
        ttk.Label(ctrl, text="Width").grid(row=1, column=0, padx=5, pady=4, sticky="e")
        ttk.Label(ctrl, text="Height").grid(row=1, column=2, padx=5, pady=4, sticky="e")

        self.sp_top = tk.Spinbox(ctrl, from_=0, to=10000, textvariable=self.top_var, width=7)
        self.sp_left = tk.Spinbox(ctrl, from_=0, to=10000, textvariable=self.left_var, width=7)
        self.sp_width = tk.Spinbox(ctrl, from_=1, to=10000, textvariable=self.width_var, width=7)
        self.sp_height = tk.Spinbox(ctrl, from_=1, to=10000, textvariable=self.height_var, width=7)
        self.sp_top.grid(row=0, column=1, padx=5, pady=4)
        self.sp_left.grid(row=0, column=3, padx=5, pady=4)
        self.sp_width.grid(row=1, column=1, padx=5, pady=4)
        self.sp_height.grid(row=1, column=3, padx=5, pady=4)

        btns = ttk.Frame(ctrl)
        btns.grid(row=0, column=4, rowspan=2, padx=8, pady=4, sticky="nsw")
        ttk.Button(btns, text="Áp dụng", command=self.apply_region).pack(fill="x", pady=2)
        ttk.Button(btns, text="Chụp thử", command=self.test_capture).pack(fill="x", pady=2)
        ttk.Button(btns, text="Kiểm tra vùng (Live)", command=self.open_live_preview).pack(fill="x", pady=2)
        ttk.Button(btns, text="Mở cửa sổ Output (OBS)", command=self.open_obs_output).pack(fill="x", pady=2)

        # Label hướng dẫn + trạng thái
        self.status = ttk.Label(self.root, text="Nhấn TAB trong game để OCR + cập nhật UI")
        self.status.pack(fill="x", padx=10)

        # Kiểm tra Tesseract ngay khi khởi động
        self.check_tesseract()

        # Preview vùng chụp
        self.preview_label = ttk.Label(self.root, text="(Xem trước vùng chụp sẽ hiển thị ở đây)")
        self.preview_label.pack(fill="x", padx=10, pady=6)

        # Khu kết quả có cuộn
        self.results_container = ttk.Frame(self.root)
        self.results_container.pack(fill="both", expand=True, padx=10, pady=8)
        self.canvas = tk.Canvas(self.results_container, height=260)
        self.scrollbar = ttk.Scrollbar(self.results_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.results_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.results_frame, anchor="nw")
        self.results_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind(
            "<Configure>", lambda e: self.canvas.itemconfigure(self.canvas_window, width=e.width)
        )

        # Lưu ref ảnh Tk để tránh GC
        self._tk_imgs = []
        self._preview_tk = None
        self._live_preview_tk = None
        self._obs_tk = None

        # Cửa sổ Live Preview / OBS Output
        self.live_preview_win = None
        self.live_preview_label = None
        self.live_preview_running = False

        self.obs_win = None
        self.obs_label = None
        self.obs_running = False

        # Đăng ký hotkey (scheduling về main thread để an toàn với Tk)
        try:
            self.hotkey_id = keyboard.add_hotkey("tab", lambda: self.root.after(0, self.on_tab_pressed))
            self.status.configure(text="Sẵn sàng. Nhấn TAB trong game để OCR.")
        except Exception as e:
            self.hotkey_id = None
            self.status.configure(text=f"Không đăng ký được hotkey TAB: {e}")

        # Dọn dẹp khi đóng
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.root.mainloop()

    def get_region(self):
        return {
            "top": int(self.top_var.get()),
            "left": int(self.left_var.get()),
            "width": int(self.width_var.get()),
            "height": int(self.height_var.get()),
        }

    def apply_region(self):
        r = self.get_region()
        self.status.configure(text=f"Đã áp dụng: top={r['top']}, left={r['left']}, w={r['width']}, h={r['height']}")

    def test_capture(self):
        try:
            img = capture_region(self.get_region())
            self.show_preview(img)
            self.status.configure(text="Chụp thử thành công")
        except Exception as e:
            self.status.configure(text=f"Lỗi chụp thử: {e}")

    def on_tab_pressed(self):
        # Gọi từ main thread (đã được schedule qua root.after)
        self.capture_and_ocr()

    def capture_and_ocr(self):
        try:
            screenshot = capture_region(self.get_region())
        except Exception as e:
            self.status.configure(text=f"Lỗi chụp màn hình: {e}")
            return

        # OCR trước, chỉ cập nhật UI khi có text (dùng phương pháp đơn giản)
        try:
            text = get_text_from_image(screenshot)
        except Exception as e:
            self.status.configure(text=f"OCR lỗi: {e}")
            return
        if not text:
            self.status.configure(text="Không phát hiện text trong vùng chụp — giữ nguyên hình ảnh cũ")
            return

        # Có text: cập nhật preview và các cửa sổ phụ
        self.show_preview(screenshot)
        try:
            if self.live_preview_win and tk.Toplevel.winfo_exists(self.live_preview_win):
                self.set_live_preview_image(screenshot.copy())
            if self.obs_win and tk.Toplevel.winfo_exists(self.obs_win):
                self.set_obs_output_image(screenshot.copy())
        except Exception as e:
            self.status.configure(text=f"Lỗi cập nhật cửa sổ phụ: {e}")

        # Xoá kết quả cũ
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self._tk_imgs = []

        # Hiển thị kết quả text đơn giản
        ttk.Label(self.results_frame, text=text, anchor="w", justify="left", wraplength=480).pack(fill="x", padx=6, pady=6)

        self.status.configure(text="Đã OCR xong (simple text)")
        print(">>> OCR text:", text)

    def show_preview(self, pil_img):
        # Resize preview vừa khung
        max_w = 500
        w, h = pil_img.size
        if w > max_w:
            ratio = max_w / float(w)
            pil_img = pil_img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
        self._preview_tk = ImageTk.PhotoImage(pil_img)
        self.preview_label.configure(image=self._preview_tk)

    def set_live_preview_image(self, pil_img):
        """Cập nhật ảnh cho cửa sổ 'Kiểm tra vùng (Live)' một lần."""
        if not (self.live_preview_win and tk.Toplevel.winfo_exists(self.live_preview_win)):
            return
        w = self.live_preview_win.winfo_width() or pil_img.width
        if w > 10 and pil_img.width > 0:
            ratio = w / float(pil_img.width)
            pil_img = pil_img.resize((int(pil_img.width * ratio), int(pil_img.height * ratio)), Image.LANCZOS)
        self._live_preview_tk = ImageTk.PhotoImage(pil_img)
        self.live_preview_label.configure(image=self._live_preview_tk, text="")

    def set_obs_output_image(self, pil_img):
        """Cập nhật ảnh cho cửa sổ 'Region Output (OBS)' một lần, fit theo kích thước cửa sổ."""
        if not (self.obs_win and tk.Toplevel.winfo_exists(self.obs_win)):
            return
        win_w = max(self.obs_win.winfo_width(), 1)
        win_h = max(self.obs_win.winfo_height(), 1)
        if pil_img.width != win_w or pil_img.height != win_h:
            scale = min(win_w / pil_img.width, win_h / pil_img.height)
            new_w, new_h = int(pil_img.width * scale), int(pil_img.height * scale)
            pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)
        self._obs_tk = ImageTk.PhotoImage(pil_img)
        self.obs_label.configure(image=self._obs_tk)

    # --- Live region tester ---
    def open_live_preview(self):
        if self.live_preview_win and tk.Toplevel.winfo_exists(self.live_preview_win):
            return
        self.live_preview_win = tk.Toplevel(self.root)
        self.live_preview_win.title("Kiểm tra vùng chụp (nhấn TAB để cập nhật)")
        self.live_preview_label = ttk.Label(self.live_preview_win, text="Nhấn TAB để cập nhật ảnh")
        self.live_preview_label.pack(fill="both", expand=True)
        self.live_preview_win.protocol("WM_DELETE_WINDOW", self.close_live_preview)

    def close_live_preview(self):
        try:
            if self.live_preview_win and tk.Toplevel.winfo_exists(self.live_preview_win):
                self.live_preview_win.destroy()
        except Exception:
            pass
        self.live_preview_win = None
        self.live_preview_label = None

    # --- Dedicated output window for OBS ---
    def open_obs_output(self):
        if self.obs_win and tk.Toplevel.winfo_exists(self.obs_win):
            return
        # Tạo cửa sổ chỉ hiển thị vùng chụp, kích thước = vùng chụp
        r = self.get_region()
        self.obs_win = tk.Toplevel(self.root)
        self.obs_win.title("Region Output (OBS) - nhấn TAB để cập nhật")
        self.obs_win.configure(bg="black")
        try:
            self.obs_win.wm_attributes("-topmost", True)
        except Exception:
            pass
        self.obs_win.geometry(f"{r['width']}x{r['height']}")
        self.obs_label = ttk.Label(self.obs_win)
        self.obs_label.pack(fill="both", expand=True)
        self.obs_win.protocol("WM_DELETE_WINDOW", self.close_obs_output)

    # Bỏ cập nhật tuần hoàn; ảnh sẽ được set khi nhấn TAB qua set_obs_output_image()

    def close_obs_output(self):
        try:
            if self.obs_win and tk.Toplevel.winfo_exists(self.obs_win):
                self.obs_win.destroy()
        except Exception:
            pass
        self.obs_win = None
        self.obs_label = None

    def on_close(self):
        try:
            if getattr(self, "hotkey_id", None) is not None:
                keyboard.remove_hotkey(self.hotkey_id)
        except Exception:
            pass
        # Đóng các cửa sổ phụ nếu còn mở
        self.close_live_preview()
        self.close_obs_output()
        self.root.destroy()

    # --- Kiểm tra & cấu hình Tesseract (đơn giản) ---
    def check_tesseract(self):
        """Kiểm tra đường dẫn tesseract.exe đã chỉ định và hiển thị phiên bản."""
        try:
            cmd = pytesseract.pytesseract.tesseract_cmd
            if not cmd or not os.path.exists(cmd):
                self.status.configure(
                    text=(
                        "Không tìm thấy Tesseract tại: "
                        f"{cmd}. Cài từ UB Mannheim hoặc chỉnh đường dẫn trong mã."
                    )
                )
                return False

            ver = pytesseract.get_tesseract_version()
            self.status.configure(text=f"Tesseract OK: v{ver} (lang={OCR_LANG})")
            return True
        except Exception as e:
            self.status.configure(text=f"Lỗi Tesseract: {e}. Kiểm tra cài đặt hoặc quyền truy cập.")
            return False


if __name__ == "__main__":
    try:
        print("App chạy rồi. Nhấn TAB để OCR + show kết quả.")
    except Exception:
        pass
    OCRApp()
