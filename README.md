# Game OCR Helper

Công cụ hỗ trợ chụp một vùng màn hình trong game và nhận diện chữ (OCR) khi bạn nhấn phím TAB. Ứng dụng có giao diện đơn giản, có thể xem trước vùng chụp, mở cửa sổ Output cho OBS, và chỉ chạy OCR khi bạn yêu cầu (không chạy liên tục).

---

## Tính năng chính
- Chụp vùng màn hình tùy chỉnh (top, left, width, height).
- OCR đơn giản bằng Tesseract để lấy text từ ảnh.
- Chỉ cập nhật UI khi phát hiện có chữ (tránh update không cần thiết).
- Live Preview: kiểm tra nhanh hình vùng chụp.
- Region Output (OBS): cửa sổ riêng để đưa vào OBS.
- Hotkey TAB: Nhấn TAB trong game để chụp + OCR + cập nhật UI.

---

## Yêu cầu hệ thống
- Windows 10/11
- Python 3.9+ (khuyến nghị 3.10+)
- Tesseract OCR for Windows (UB Mannheim build)

---

## Cài đặt
1) Cài Python và các gói phụ thuộc
```powershell
# Tại thư mục dự án
python -m pip install -r requirements.txt
```
`requirements.txt` gồm: `mss`, `pytesseract`, `opencv-python`, `Pillow`, `keyboard`, `numpy`.

2) Cài Tesseract cho Windows
- Tải bản cài đặt từ UB Mannheim: https://github.com/UB-Mannheim/tesseract/wiki
- Cài đặt theo mặc định (ví dụ: `C:\Program Files\Tesseract-OCR\tesseract.exe`).
- (Tùy chọn) Cài thêm ngôn ngữ `vie` nếu cần OCR tiếng Việt (tệp `vie.traineddata` đặt vào thư mục `tessdata`).

3) Chỉ định đường dẫn `tesseract.exe`
- Mở `main.py` và điều chỉnh dòng:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```
- Nếu vị trí cài đặt khác, sửa lại chuỗi đường dẫn cho đúng.

4) Kiểm tra Tesseract
- Chạy ứng dụng, phần `check_tesseract()` sẽ hiển thị phiên bản. Hoặc tự kiểm tra:
```powershell
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```

---

## Sử dụng
1) Chạy ứng dụng
```powershell
python main.py
```
2) Tùy chỉnh vùng chụp trong giao diện (Top, Left, Width, Height) → bấm "Áp dụng".
3) Bấm "Chụp thử" để xem trước hình vùng chụp.
4) (Tùy chọn) Bấm "Kiểm tra vùng (Live)" để mở cửa sổ Live Preview. Cửa sổ này sẽ cập nhật khi bạn nhấn TAB.
5) (Tùy chọn) Bấm "Mở cửa sổ Output (OBS)" để mở cửa sổ đúng kích thước vùng chụp, tiện đưa vào OBS.
6) Trong game, nhấn phím TAB:
   - Ứng dụng chụp vùng, chạy OCR.
   - Nếu phát hiện có chữ: preview và các cửa sổ phụ sẽ cập nhật; phần kết quả hiển thị nội dung text.
   - Nếu không có chữ: trạng thái thông báo và không cập nhật ảnh.

Gợi ý: Bạn có thể đổi ngôn ngữ OCR bằng cách sửa hằng số `OCR_LANG` trong `main.py` (mặc định `eng`, có thể đổi `vie`).

---

## Tùy chỉnh nhanh
- Ngưỡng xử lý ảnh: Trong `get_text_from_image()`, tham số ngưỡng `threshold` (mặc định 150) có thể chỉnh về 120–180 để phù hợp từng game/skin.
- Chỉ kiểm tra có/không có chữ: Ứng dụng có thể chỉ dùng OCR để xác định có chữ mà không cần hiển thị nội dung. (Mặc định bản hiện tại có hiển thị text.)
- Vùng chụp: Giữ vùng nhỏ để tăng tốc độ và giảm sử dụng tài nguyên.

---

## Hiệu năng
- Ở trạng thái chờ (idle), app hầu như không dùng CPU.
- Khi nhấn TAB, sẽ có spike CPU ngắn do Tesseract xử lý ~100–300ms cho vùng ~400x400 (tùy máy).
- RAM ổn định, ảnh tạm thời nhỏ (<1MB mỗi ảnh). Không có dấu hiệu rò rỉ vì ảnh và widget cũ được dọn trước khi tạo mới.

---

## Khắc phục sự cố (Troubleshooting)
- WinError 740: "The requested operation requires elevation"
  - Bỏ tích "Run this program as an administrator" ở Properties > Compatibility của `tesseract.exe`.
  - Kiểm tra và xóa flag `RUNASADMIN` tại:
    - `HKCU/Software/Microsoft/Windows NT/CurrentVersion/AppCompatFlags/Layers`
    - `HKLM/Software/Microsoft/Windows NT/CurrentVersion/AppCompatFlags/Layers`
  - Đảm bảo `tesseract_cmd` trỏ trực tiếp tới `tesseract.exe` (không phải shortcut `.lnk`).
- "Không tìm thấy Tesseract": Kiểm tra lại đường dẫn trong `main.py` hoặc cài Tesseract từ UB Mannheim.
- OCR tiếng Việt không ra chữ: Cần `vie.traineddata` trong `tessdata` và đặt `OCR_LANG = "vie"`.

---

## Câu hỏi thường gặp (FAQ)
- App có cần chạy quyền Admin không? – Không. Nếu Tesseract bị ép chạy Admin, hãy tắt flag Compatibility như mục trên.
- Có chạy OCR liên tục được không? – Có thể, nhưng không khuyến nghị vì CPU sẽ cao. Thiết kế hiện tại chỉ OCR khi nhấn TAB.
- Có hỗ trợ OBS? – Có. Dùng "Mở cửa sổ Output (OBS)" rồi thêm cửa sổ đó vào OBS.

---

## Thư mục & file quan trọng
- `main.py`: mã nguồn chính, UI Tkinter, hotkey TAB, OCR.
- `requirements.txt`: danh sách phụ thuộc Python.
- `assets/`: chứa một vài hình ảnh mẫu (nếu có).

---

## Giấy phép
Dự án dùng nội bộ/cá nhân. Tesseract là phần mềm mã nguồn mở (Apache License 2.0); vui lòng tuân thủ giấy phép của Tesseract khi phân phối.
