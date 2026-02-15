import customtkinter as ctk
import requests
from bs4 import BeautifulSoup
import threading
import time
import sys
import webbrowser

# --- Ayarlar ve Sabitler ---
NEWS_URL = "https://www.bbc.com/news"
BASE_URL = "https://www.bbc.com"
UPDATE_INTERVAL_SECONDS = 600 # 10 dakika
SCROLL_SPEED = 1.5            # Kayma hızı
ANIMATION_DELAY_MS = 15       # Yenileme hızı
BG_COLOR = "#1a1a1a"
TEXT_COLOR = "#e0e0e0"
HOVER_COLOR = "#bb1919"       # Üzerine gelince renk
FONT_FAMILY = "Arial"
FONT_SIZE = 14
ITEM_SPACING = 50             # Haberler arası boşluk

class BBCNewsTicker(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Pencere Ayarları ---
        self.title("BBC News Ticker")
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0.95)
        
        # Ekran boyutunu al
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        bar_height = 40
        
        # Taskbar üstüne yerleştir (Linux/Windows fark edebilir, biraz pay bırakıyoruz)
        y_pos = screen_height - bar_height - 5 
        
        self.geometry(f"{screen_width}x{bar_height}+0+{y_pos}")
        self.configure(fg_color=BG_COLOR)

        # --- Değişkenler ---
        self.news_data = []      
        self.news_widgets = []   
        self.is_running = True
        self.drag_data = {"x": 0, "y": 0}
        self.first_load_done = False 

        # --- Yükleniyor Mesajı ---
        self.loading_label = ctk.CTkLabel(
            self, text="Connecting to BBC...", 
            font=(FONT_FAMILY, FONT_SIZE, "bold"), text_color=HOVER_COLOR
        )
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")

        # --- Etkileşimler ---
        self.bind("<Button-3>", self.close_app)     # Sağ tık kapatır
        self.bind("<ButtonPress-1>", self.start_drag) # Sürükleme başlar
        self.bind("<B1-Motion>", self.do_drag)        # Sürüklenir

        # --- Başlatma ---
        self.start_background_thread() # Eksik olan fonksiyon çağrısı buradaydı
        self.animate_ticker()

    # --- EKSİK OLAN FONKSİYON EKLENDİ ---
    def start_background_thread(self):
        """Haber çekme işlemini ayrı thread'de başlatır."""
        thread = threading.Thread(target=self.fetch_news, daemon=True)
        thread.start()

    def fetch_news(self):
        """Web scraping işlemini yapan fonksiyon."""
        while self.is_running:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                response = requests.get(NEWS_URL, headers=headers, timeout=10)
                
                new_data = []
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    tags = soup.find_all(['h2', 'h4'])
                    
                    seen_titles = set()
                    
                    for tag in tags:
                        title = tag.get_text().strip()
                        if not title or title in seen_titles:
                            continue
                        
                        # Linki bul
                        link_tag = tag.find_parent('a')
                        if not link_tag:
                            link_tag = tag.find('a')
                        
                        if link_tag and link_tag.get('href'):
                            href = link_tag.get('href')
                            full_link = href if href.startswith('http') else BASE_URL + href
                            
                            new_data.append({"title": title, "link": full_link})
                            seen_titles.add(title)
                    
                    if not new_data:
                        new_data = [{"title": "No headlines found.", "link": NEWS_URL}]
                else:
                    new_data = [{"title": f"Connection Error: {response.status_code}", "link": NEWS_URL}]

                self.news_data = new_data
                
                # Arayüzü güncelle (Main thread'de çalışması için after kullanılır)
                self.after(0, self.setup_news_widgets)

            except Exception as e:
                print(f"Hata: {e}")
            
            time.sleep(UPDATE_INTERVAL_SECONDS)

    def open_link(self, url):
        """Tarayıcıda linki açar."""
        if url:
            webbrowser.open(url)

    def setup_news_widgets(self):
        """Widget'ları oluşturur ve ekrana dizer."""
        # Eski widget'ları temizle
        for item in self.news_widgets:
            item['label'].destroy()
        self.news_widgets.clear()
        
        if self.loading_label:
            self.loading_label.destroy()
            self.loading_label = None

        current_x = self.winfo_screenwidth() 

        for item in self.news_data:
            title = item['title']
            link = item['link']

            lbl = ctk.CTkLabel(
                self, 
                text=title, 
                font=(FONT_FAMILY, FONT_SIZE),
                text_color=TEXT_COLOR,
                cursor="hand2"
            )
            
            # Tıklama olayı
            lbl.bind("<Button-1>", lambda event, url=link: self.open_link(url))
            
            # Renk değişimi (Hover)
            lbl.bind("<Enter>", lambda event, l=lbl: l.configure(text_color=HOVER_COLOR))
            lbl.bind("<Leave>", lambda event, l=lbl: l.configure(text_color=TEXT_COLOR))

            # Genişliği hesaplamak için çizimi zorla (Linux'ta bazen gereklidir)
            lbl.update_idletasks() 
            w = lbl.winfo_reqwidth()
            
            self.news_widgets.append({
                "label": lbl,
                "x": current_x,
                "width": w,
                "url": link
            })
            
            current_x += w + ITEM_SPACING

        self.first_load_done = True

    def animate_ticker(self):
        """Kayan yazı animasyonu."""
        if not self.is_running:
            return

        if not self.first_load_done or not self.news_widgets:
             self.after(100, self.animate_ticker)
             return

        # Listenin en sağındaki elemanın bittiği yer
        right_most_edge = -99999
        if self.news_widgets:
            # En sağdaki widget'ı bul (x değeri en büyük olan)
            last_item = max(self.news_widgets, key=lambda i: i['x'])
            right_most_edge = last_item['x'] + last_item['width']

        for item in self.news_widgets:
            # Sola kaydır
            item['x'] -= SCROLL_SPEED
            
            # Ekranın solundan çıktıysa en sağa ekle
            if item['x'] + item['width'] < 0:
                item['x'] = right_most_edge + ITEM_SPACING
                right_most_edge = item['x'] + item['width']

            # Konumu güncelle
            item['label'].place(x=item['x'], y=8)

        self.after(ANIMATION_DELAY_MS, self.animate_ticker)

    # --- Sürükleme ve Kapatma ---
    def start_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def do_drag(self, event):
        x = self.winfo_x() - self.drag_data["x"] + event.x
        y = self.winfo_y() - self.drag_data["y"] + event.y
        self.geometry(f"+{x}+{y}")

    def close_app(self, event=None):
        self.is_running = False
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = BBCNewsTicker()
    app.mainloop()