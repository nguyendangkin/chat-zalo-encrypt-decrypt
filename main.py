import tkinter as tk
from tkinter import scrolledtext, messagebox
import pyautogui
import pyperclip
import time
import threading
from cryptography.fernet import Fernet

class ZaloEncryptDecryptApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ứng dụng Mã hóa/Giải mã Tự động Hai Chiều cho Zalo")
        self.geometry("700x600")

        self.create_widgets()
        self.is_monitoring = False

    def create_widgets(self):
        # Ô nhập key
        tk.Label(self, text="Nhập key (để trống để tạo key mới):").pack(pady=5)
        self.key_entry = tk.Entry(self, width=70)
        self.key_entry.pack(pady=5)
        tk.Button(self, text="Tạo key mới", command=self.generate_new_key).pack(pady=5)

        # Khu vực nhập văn bản gửi đi
        tk.Label(self, text="Văn bản gửi đi:").pack(pady=5)
        self.send_text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=70, height=5)
        self.send_text_area.pack(padx=10, pady=5, expand=True, fill=tk.BOTH)

        # Khu vực hiển thị văn bản nhận được
        tk.Label(self, text="Văn bản nhận được (đã giải mã):").pack(pady=5)
        self.receive_text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=70, height=5)
        self.receive_text_area.pack(padx=10, pady=5, expand=True, fill=tk.BOTH)

        self.status_label = tk.Label(self, text="Trạng thái: Đang chờ")
        self.status_label.pack(pady=5)

        self.mode_var = tk.StringVar(value="encrypt")
        tk.Radiobutton(self, text="Mã hóa", variable=self.mode_var, value="encrypt").pack()
        tk.Radiobutton(self, text="Giải mã", variable=self.mode_var, value="decrypt").pack()

        tk.Button(self, text="Xử lý và Gửi", command=self.process_and_send).pack(pady=5)
        tk.Button(self, text="Định vị ô nhập tin nhắn", command=self.locate_input_box).pack(pady=5)
        
        self.monitor_button = tk.Button(self, text="Bắt đầu theo dõi tin nhắn đến", command=self.toggle_monitoring)
        self.monitor_button.pack(pady=5)

        self.input_box_coords = None

    def generate_new_key(self):
        key = Fernet.generate_key()
        self.key_entry.delete(0, tk.END)
        self.key_entry.insert(0, key.decode())
        messagebox.showinfo("Thông báo", "Đã tạo key mới. Hãy lưu lại key này!")

    def locate_input_box(self):
        messagebox.showinfo("Hướng dẫn", "Di chuyển chuột đến ô nhập tin nhắn trong Zalo và giữ nguyên trong 2 giây.")
        time.sleep(3)  # Đợi người dùng di chuyển chuột
        self.input_box_coords = pyautogui.position()
        self.status_label.config(text=f"Đã định vị ô nhập tin nhắn: {self.input_box_coords}")

    def process_and_send(self):
        if not self.input_box_coords:
            messagebox.showerror("Lỗi", "Vui lòng định vị ô nhập tin nhắn trước.")
            return

        key = self.key_entry.get().strip()
        if not key:
            messagebox.showerror("Lỗi", "Vui lòng nhập hoặc tạo key trước khi xử lý.")
            return

        try:
            key = key.encode()
            fernet = Fernet(key)
            original_text = self.send_text_area.get("1.0", tk.END).strip()
            mode = self.mode_var.get()

            if mode == "encrypt":
                processed_text = fernet.encrypt(original_text.encode()).decode()
            else:  # decrypt
                processed_text = fernet.decrypt(original_text.encode()).decode()

            # Tự động hóa quá trình copy/paste và gửi trong Zalo
            pyperclip.copy(processed_text)
            time.sleep(0.5)  # Đợi để đảm bảo clipboard đã được cập nhật

            # Click vào ô nhập tin nhắn
            pyautogui.click(self.input_box_coords)
            time.sleep(0.2)

            # Paste nội dung
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.2)

            # Gửi tin nhắn
            pyautogui.press('enter')

            self.status_label.config(text=f"Trạng thái: Đã {mode} và gửi thành công")
        except Exception as e:
            self.status_label.config(text=f"Lỗi: {str(e)}")

    def toggle_monitoring(self):
        if self.is_monitoring:
            self.is_monitoring = False
            self.monitor_button.config(text="Bắt đầu theo dõi tin nhắn đến")
            self.status_label.config(text="Trạng thái: Đã dừng theo dõi")
        else:
            self.is_monitoring = True
            self.monitor_button.config(text="Dừng theo dõi tin nhắn đến")
            self.status_label.config(text="Trạng thái: Đang theo dõi tin nhắn đến")
            threading.Thread(target=self.monitor_clipboard, daemon=True).start()

    def monitor_clipboard(self):
        last_clipboard = ""
        while self.is_monitoring:
            current_clipboard = pyperclip.paste()
            if current_clipboard != last_clipboard:
                last_clipboard = current_clipboard
                self.decrypt_incoming_message(current_clipboard)
            time.sleep(0.5)

    def decrypt_incoming_message(self, message):
        key = self.key_entry.get().strip()
        if not key:
            self.status_label.config(text="Lỗi: Không có key để giải mã")
            return

        try:
            fernet = Fernet(key.encode())
            decrypted_message = fernet.decrypt(message.encode()).decode()
            self.receive_text_area.delete(1.0, tk.END)
            self.receive_text_area.insert(tk.END, decrypted_message)
            self.status_label.config(text="Trạng thái: Đã nhận và giải mã tin nhắn mới")
        except Exception as e:
            self.status_label.config(text=f"Lỗi khi giải mã: {str(e)}")

if __name__ == "__main__":
    app = ZaloEncryptDecryptApp()
    app.mainloop()