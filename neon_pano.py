import customtkinter as ctk
import pyperclip
import threading
import time
from datetime import datetime

class NeonClipboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Ana Ayarlar ---
        self.title("Neon Clipboard Ultra v2.5")
        self.geometry("500x750")
        ctk.set_appearance_mode("dark")
        
        self.history = []
        self.last_item = ""
        self.is_monitoring = True

        self.setup_ui()
        
        # Panoyu izleyen motoru arka planda başlat
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        self.monitor_thread.start()

    def setup_ui(self):
        # --- Üst Başlık & Kontroller ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=20, padx=20, fill="x")

        self.header = ctk.CTkLabel(self.header_frame, text="NEON CLIPBOARD", 
                                   font=("Consolas", 24, "bold"), text_color="#00ffcc")
        self.header.pack(side="left")

        self.clear_btn = ctk.CTkButton(self.header_frame, text="CLEAN LOG", width=100,
                                       fg_color="#c0392b", hover_color="#a93226", 
                                       command=self.clear_history)
        self.clear_btn.pack(side="right")

        # --- Kaydırılabilir Liste Alanı ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=460, height=580, 
                                                fg_color="#121212", border_width=1, border_color="#333333")
        self.scroll_frame.pack(pady=5, padx=15, fill="both", expand=True)

        # --- Alt Durum Çubuğu ---
        self.status_bar = ctk.CTkFrame(self, height=35, fg_color="#1a1a1a")
        self.status_bar.pack(fill="x", side="bottom")

        self.status_lbl = ctk.CTkLabel(self.status_bar, text="🟢 System Active", font=("Arial", 11), text_color="#2ecc71")
        self.status_lbl.pack(side="left", padx=15)

        self.count_lbl = ctk.CTkLabel(self.status_bar, text="Items: 0", font=("Arial", 11))
        self.count_lbl.pack(side="right", padx=15)

    def monitor_clipboard(self):
        """Clipboard motoru - Optimize edilmiş gecikme ile."""
        while self.is_monitoring:
            try:
                current_item = pyperclip.paste()
                if current_item != self.last_item and current_item.strip() != "":
                    self.last_item = current_item
                    self.add_to_history(current_item)
            except Exception:
                pass
            time.sleep(0.7) # CPU dostu kontrol aralığı

    def add_to_history(self, item):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = {"text": item, "time": timestamp}

        if entry["text"] not in [x["text"] for x in self.history]:
            self.history.insert(0, entry)
            if len(self.history) > 50:
                self.history.pop()
            
            self.after(0, self.update_ui_list)

    def update_ui_list(self):
        # Mevcut öğeleri temizle
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        for idx, item in enumerate(self.history):
            self.create_entry_widget(item, idx)
        
        self.count_lbl.configure(text=f"Items: {len(self.history)}")

    def create_entry_widget(self, item, idx):
        # Her pano öğesi için bir satır (frame) oluştur
        row = ctk.CTkFrame(self.scroll_frame, fg_color="#1e1e1e" if idx % 2 == 0 else "#252525")
        row.pack(fill="x", pady=2, padx=5)

        # Zaman Etiketi
        time_lbl = ctk.CTkLabel(row, text=item["time"], font=("Arial", 9), text_color="gray")
        time_lbl.pack(side="left", padx=10)

        # Metin Gösterimi (Kısa özet)
        short_text = (item["text"][:40] + '...') if len(item["text"]) > 40 else item["text"]
        
        btn = ctk.CTkButton(row, text=short_text, anchor="w", fg_color="transparent",
                            hover_color="#333333", height=35,
                            command=lambda t=item["text"]: self.copy_back(t))
        btn.pack(side="left", fill="x", expand=True)

        # Kopyala Butonu (Küçük İkon niyetine)
        copy_small = ctk.CTkButton(row, text="📋", width=30, height=25, fg_color="#2c3e50",
                                   command=lambda t=item["text"]: self.copy_back(t))
        copy_small.pack(side="right", padx=5)

    def copy_back(self, text):
        pyperclip.copy(text)
        self.last_item = text
        self.status_lbl.configure(text="⚡ Copied to clipboard!", text_color="#00ffcc")
        # 2 saniye sonra normale dön
        self.after(2000, lambda: self.status_lbl.configure(text="🟢 System Active", text_color="#2ecc71"))

    def clear_history(self):
        self.history = []
        self.update_ui_list()
        self.status_lbl.configure(text="🗑 History Cleared", text_color="#c0392b")

if __name__ == "__main__":
    app = NeonClipboard()
    app.mainloop()
