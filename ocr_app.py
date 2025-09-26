import os
from tkinter import Tk, Button, filedialog, Text, Scrollbar, RIGHT, Y, END, messagebox, Frame
from tkinter.ttk import Progressbar
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

custom_config = r'--oem 3 --psm 6'
ocr_result = ""  # Biến toàn cục để lưu kết quả OCR

def log_message(msg):
    """Hiển thị log ra Text box ngay lập tức"""
    text_box.insert(END, msg + "\n")
    text_box.see(END)  # tự động scroll
    root.update_idletasks()  # cập nhật GUI ngay

def ocr_file():
    global ocr_result
    filepath = filedialog.askopenfilename(
        title="Chọn file ảnh hoặc PDF",
        filetypes=[
            ("PDF files", "*.pdf"),
            ("Image files", "*.png *.jpg *.jpeg *.tiff *.bmp"),
            ("All supported files", "*.pdf *.png *.jpg *.jpeg *.tiff *.bmp")
        ]
    )
    if not filepath:
        return

    # Disable button trong khi xử lý
    btn_frame.config(state="disabled")
    btn_save.config(state="disabled")
    
    text_box.delete("1.0", END)
    ocr_result = ""
    log_message(f"📂 File: {os.path.basename(filepath)}")
    log_message("🔍 Bắt đầu OCR...\n")

    try:
        if filepath.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp")):
            progress_bar["value"] = 0
            log_message("🖼️ Đang xử lý ảnh...")
            
            # Mở và xử lý ảnh
            img = Image.open(filepath)
            
            # Hiển thị thông tin ảnh
            log_message(f"📊 Kích thước ảnh: {img.size}")
            
            # OCR với xử lý lỗi
            text = pytesseract.image_to_string(img, config=custom_config, lang="eng")
            ocr_result = text.strip()
            
            # Hiển thị kết quả chi tiết
            log_message("✅ OCR xong ảnh!")
            log_message("="*50)
            log_message("KẾT QUẢ OCR:")
            log_message("="*50)
            
            if ocr_result:
                text_box.insert(END, ocr_result)
                log_message(f"\n📝 Số ký tự: {len(ocr_result)}")
                log_message(f"📄 Số dòng: {len(ocr_result.splitlines())}")
            else:
                log_message("❌ Không tìm thấy text trong ảnh!")
                log_message("💡 Thử điều chỉnh chất lượng ảnh hoặc dùng ảnh rõ nét hơn")
            
            progress_bar["value"] = 100

        elif filepath.lower().endswith(".pdf"):
            log_message("📄 Đang chuyển PDF sang ảnh...")
            
            # Convert PDF với xử lý lỗi
            try:
                pages = convert_from_path(filepath, dpi=200)  # Giảm DPI để tăng tốc
                total_pages = len(pages)
                log_message(f"📄 PDF có {total_pages} trang.")
            except Exception as e:
                log_message(f"❌ Lỗi khi đọc PDF: {e}")
                log_message("💡 Cần cài đặt poppler trên macOS: brew install poppler")
                btn_frame.config(state="normal")
                btn_save.config(state="normal")
                return

            progress_bar["value"] = 0
            progress_bar["maximum"] = total_pages

            result_lines = []
            for i, page in enumerate(pages):
                log_message(f"🔎 Đang OCR trang {i+1}/{total_pages}...")
                
                # OCR từng trang
                text = pytesseract.image_to_string(page, config=custom_config, lang="eng")
                page_result = text.strip()
                
                result_lines.append(f"\n{'='*40}")
                result_lines.append(f"TRANG {i+1}/{total_pages}")
                result_lines.append(f"{'='*40}\n")
                result_lines.append(page_result)
                
                progress_bar["value"] = i + 1
                root.update_idletasks()

            ocr_result = "\n".join(result_lines)
            
            # Hiển thị kết quả
            log_message("✅ Hoàn tất OCR PDF!")
            log_message("="*50)
            log_message("KẾT QUẢ OCR PDF:")
            log_message("="*50)
            
            text_box.insert(END, ocr_result)
            
            # Thống kê kết quả
            total_text = "".join(result_lines)
            log_message(f"\n📊 Tổng số trang: {total_pages}")
            log_message(f"📝 Tổng số ký tự: {len(total_text)}")
            log_message(f"📄 Tổng số dòng: {len(total_text.splitlines())}")

        else:
            log_message("❌ Định dạng file không hỗ trợ.")

    except Exception as e:
        log_message(f"❌ Lỗi: {str(e)}")
        log_message("💡 Kiểm tra:")
        log_message("   - File có bị hỏng không?")
        log_message("   - Tesseract đã cài đặt chưa?")
        log_message("   - Ảnh/PDF có text rõ ràng không?")

    finally:
        # Re-enable buttons
        btn_frame.config(state="normal")
        btn_save.config(state="normal")

def save_to_txt():
    """Lưu kết quả OCR ra file .txt"""
    global ocr_result
    if not ocr_result.strip():
        messagebox.showwarning("Cảnh báo", "Chưa có dữ liệu OCR để lưu!")
        return

    save_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")],
        title="Lưu file TXT"
    )
    if save_path:
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(ocr_result)
            messagebox.showinfo("Thành công", f"Đã lưu kết quả vào:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")

def clear_results():
    """Xóa toàn bộ kết quả"""
    global ocr_result
    text_box.delete("1.0", END)
    ocr_result = ""
    progress_bar["value"] = 0
    log_message("🧹 Đã xóa kết quả!")

# GUI setup
root = Tk()
root.title("OCR PDF & Image - Hiển thị kết quả chi tiết")
root.geometry("900x700")

# Frame chứa buttons (SỬA LỖI Ở ĐÂY)
button_frame = Frame(root)  # Đã sửa từ Tk.Frame thành Frame
button_frame.pack(pady=10)

btn_frame = Button(button_frame, text="📁 Chọn file để OCR", command=ocr_file, font=("Arial", 12))
btn_frame.pack(side="left", padx=5)

btn_save = Button(button_frame, text="💾 Lưu kết quả ra TXT", command=save_to_txt, font=("Arial", 12))
btn_save.pack(side="left", padx=5)

btn_clear = Button(button_frame, text="🧹 Xóa kết quả", command=clear_results, font=("Arial", 12))
btn_clear.pack(side="left", padx=5)

progress_bar = Progressbar(root, length=800, mode="determinate")
progress_bar.pack(pady=5)

# Text box với scrollbar (SỬA LỖI Ở ĐÂY)
text_frame = Frame(root)  # Đã sửa từ Tk.Frame thành Frame
text_frame.pack(expand=True, fill="both", padx=10, pady=5)

scrollbar = Scrollbar(text_frame)
scrollbar.pack(side=RIGHT, fill=Y)

text_box = Text(text_frame, wrap="word", font=("Arial", 11), 
                yscrollcommand=scrollbar.set, bg="white", fg="black")
text_box.pack(expand=True, fill="both")
scrollbar.config(command=text_box.yview)

# Hướng dẫn sử dụng
log_message("🟢 Sẵn sàng! Nhấn 'Chọn file để OCR' để bắt đầu")
log_message("💡 Mẹo:")
log_message("   - Chọn file ảnh chất lượng cao, text rõ nét")
log_message("   - PDF nên có độ phân giải tốt")
log_message("   - Kết quả sẽ hiển thị chi tiết ở đây")

root.mainloop()
