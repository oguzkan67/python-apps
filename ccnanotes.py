import customtkinter as ctk
import sys
import webbrowser
import random

# --- Profesyonel Ayarlar ve Renk Paleti ---
SCROLL_SPEED = 0.7            # Çok daha yavaş ve okunabilir hız
ANIMATION_DELAY_MS = 10       # Daha düşük gecikme = Daha akıcı (FPS artışı)
BG_COLOR = "#1e1e1e"          # Modern Koyu Antrasit (VS Code Dark stili)
TEXT_COLOR = "#e0e0e0"        # Göz yormayan kırık beyaz
ACCENT_COLOR = "#4cc9f0"      # Tıklanabilir öğeler için Soft Cyan
HEADER_COLOR = "#f72585"      # Başlıklar için modern Neon Pembe/Kırmızı
SEPARATOR_COLOR = "#555555"   # Öğeler arası silik gri ayırıcı
FONT_FAMILY = "Segoe UI"      # Daha modern, okunaklı font (Windows default)
FONT_SIZE = 15                # Bir tık daha büyük
ITEM_SPACING = 40             # Öğeler arası ferah boşluk

# --- CCNA Veri Tabanı ---
CCNA_NOTES = [
    "### OSI VE TCP/IP MODELLERİ ###",
    "Katman 7 Uygulama: HTTP, FTP, DNS, SNMP, SSH",
    "Katman 6 Sunum: Şifreleme, Sıkıştırma, JPEG, GIF",
    "Katman 5 Oturum: Oturum başlatma, durdurma, yönetme",
    "Katman 4 Taşıma: TCP, UDP, Port Numaraları",
    "Katman 3 Ağ: IP Adresleme, Yönlendirme, ICMP",
    "Katman 2 Veri İletimi: MAC Adresi, Switchler, VLAN, ARP",
    "Katman 1 Fiziksel: Kablolar, Bit akışı, Hublar",
    "PDU L4: Segment (Bölüm)",
    "PDU L3: Packet (Paket)",
    "PDU L2: Frame (Çerçeve)",
    "PDU L1: Bits (Bitler)",
    "TCP: Bağlantı odaklı, Güvenilir, 3'lü el sıkışma",
    "UDP: Bağlantısız, Hızlı, En iyi çaba (Best-effort)",
    "3'lü El Sıkışma: SYN -> SYN/ACK -> ACK",
    "### IP ADRESLEME VE ALT AĞLARA BÖLME ###",
    "Sınıf A: 1-126 (/8)",
    "Sınıf B: 128-191 (/16)",
    "Sınıf C: 192-223 (/24)",
    "Loopback: 127.0.0.1 (Yerel geri dönüş)",
    "APIPA: 169.254.x.x (DHCP bulunamazsa atanan)",
    "Özel IP A: 10.0.0.0 - 10.255.255.255",
    "Özel IP B: 172.16.0.0 - 172.31.255.255",
    "Özel IP C: 192.168.0.0 - 192.168.255.255",
    "RFC 1918: Özel (Private) IP adres standardı",
    "CIDR: Sınıfsız Alanlar Arası Yönlendirme",
    "Alt Ağ Maskesi: Ağ ve host kısmını belirler",
    "Ağ Kimliği (Network ID): Bir alt ağdaki ilk adres",
    "Yayın Adresi (Broadcast): Bir alt ağdaki son adres",
    "Ağ Geçidi (Gateway): Diğer ağlara çıkış noktası",
    "### CISCO IOS TEMEL KOMUTLAR ###",
    "Kullanıcı Modu: Router>",
    "Ayrıcalıklı Mod: Router# (enable komutu ile)",
    "Yapılandırma Modu: Router(config)# (conf t komutu ile)",
    "Arayüz Modu: Router(config-if)#",
    "Hat Modu: Router(config-line)#",
    "Ayarları Kaydet: copy running-config startup-config",
    "Ayarları Kaydet (Kısa): write (wr)",
    "Ayarları Sil: erase startup-config",
    "Cihazı Yeniden Başlat: reload",
    "Versiyon Bilgisi: show version",
    "Arayüz Özet: show ip interface brief",
    "Çalışan Ayarlar: show running-config",
    "Cihaz Adı: hostname [İsim]",
    "Giriş Mesajı: banner motd # Mesaj #",
    "Konsol Şifresi: line con 0 -> password [şifre] -> login",
    "VTY (Uzak Bağlantı) Şifresi: line vty 0 4 -> login",
    "Şifreleri Gizle: service password-encryption",
    "### SWITCHING (ANAHTARLAMA) KAVRAMLARI ###",
    "Switch: LAN içindeki cihazları bağlar (Katman 2)",
    "MAC Tablosu: CAM Tablosu olarak da bilinir",
    "Öğrenme: Gelen çerçevenin kaynak MAC adresini kaydeder",
    "Yönlendirme: Hedef MAC adresini CAM tablosunda arar",
    "Flooding (Basma): Bilinmeyen hedefi tüm portlara gönderir",
    "Çarpışma Alanı (Collision Domain): Her switch portu ayrıdır",
    "Yayın Alanı (Broadcast Domain): Switch'in tamamıdır",
    "Tam Çift Yönlü (Full Duplex): Aynı anda gönderim ve alım",
    "Yarı Çift Yönlü (Half Duplex): Sırayla gönderim/alım (CSMA/CD)",
    "### VLAN VE TRUNKING ###",
    "VLAN: Sanal LAN, yayın alanlarını mantıksal böler",
    "VLAN Oluştur: vlan [id] -> name [isim]",
    "Porta VLAN Ata: switchport access vlan [id]",
    "Trunking: Tek hat üzerinden çoklu VLAN taşıma",
    "802.1Q: Standart VLAN etiketleme protokolü (Dot1q)",
    "Native VLAN: Trunk hattındaki etiketsiz trafik",
    "Trunk Yapılandırma: switchport mode trunk",
    "VTP: VLAN bilgilerini switchler arasında senkronize eder",
    "DTP: Dinamik Trunk Protokolü (Cisco özel)",
    "Ses VLAN: switchport voice vlan [id]",
    "### SPANNING TREE PROTOCOL (STP) ###",
    "STP Amacı: Katman 2 döngülerini (loop) engellemek",
    "STP Standardı: 802.1D",
    "Root Bridge: En düşük Bridge ID'ye sahip switch",
    "Bridge ID: Öncelik (Priority) + MAC Adresi",
    "Root Port (RP): Root Bridge'e en yakın port",
    "Designated Port (DP): Veri ileten port",
    "Blocking Port: Döngüyü kırmak için kapatılan port",
    "STP Durumları: Blocking, Listening, Learning, Forwarding",
    "PortFast: Uç cihazlar için STP beklemesini atlar",
    "BPDU Guard: Porttan BPDU gelirse portu kapatır",
    "Rapid STP (RSTP): 802.1w (Daha hızlı yakınsama)",
    "### ETHERCHANNEL ###",
    "EtherChannel: Bant genişliği için link birleştirme",
    "PAgP: Cisco'ya özel protokol (Auto, Desirable)",
    "LACP: Endüstri standardı 802.3ad (Active, Passive)",
    "Max Link: En fazla 8 aktif hat birleşebilir",
    "Yapılandırma: channel-group [id] mode active",
    "### YÖNLENDİRME (ROUTING) TEMELLERİ ###",
    "Router: Farklı ağları birbirine bağlar (Katman 3)",
    "Yönlendirme Tablosu: Hedef ağ, Metrik, Sonraki durak",
    "Doğrudan Bağlı (Connected): AD değeri 0",
    "Statik Rota: AD değeri 1",
    "Varsayılan Rota: 0.0.0.0 0.0.0.0 (Bilinmeyen her yer)",
    "Administrative Distance (AD): Rotanın güvenilirliği",
    "Metric: Hedefe ulaşma maliyeti (Mesafe/Hız)",
    "Yakınsama (Convergence): Tüm routerların rotada uzlaşması",
    "### YÖNLENDİRME PROTOKOLLERİ ###",
    "RIP: Mesafe vektör, max 15 hop, AD 120",
    "EIGRP: Gelişmiş mesafe vektör, AD 90",
    "OSPF: Link-state (Bağlantı durumu), AD 110",
    "OSPF Alan (Area): Çoklu alanlarda Area 0 omurgadır",
    "OSPF Hello: Varsayılan 10 saniye",
    "OSPF Router ID: En yüksek IP veya manuel atama",
    "OSPF Joker Maske (Wildcard): Maskenin tersi",
    "OSPF Komut: router ospf [id] -> network [ip] [wildcard]",
    "### IPv6 ###",
    "IPv6: 128-bit, Heksadesimal yazım",
    "Global Unicast: 2000::/3 (İnternet IP'si)",
    "Link-Local: fe80::/10 (Yerel bağlantı adresi)",
    "Unique Local: fc00::/7 (Özel ağ adresi)",
    "Dual Stack: IPv4 ve IPv6'yı aynı anda çalıştırma",
    "SLAAC: Sunucusuz otomatik adres yapılandırma",
    "EUI-64: MAC adresinden IPv6 arayüz kimliği oluşturma",
    "### IP HİZMETLERİ (NAT, DHCP, ACL) ###",
    "Statik NAT: 1'e 1 eşleme",
    "PAT (Overload): Çoklu iç IP'yi tek dış IP'ye portla eşleme",
    "DHCP DORA: Discover, Offer, Request, Acknowledge",
    "DHCP Relay: Farklı VLAN'a DHCP isteği iletme",
    "Standart ACL: 1-99, Sadece kaynak IP'ye bakar",
    "Genişletilmiş ACL: 100-199, Kaynak, Hedef, Port bakar",
    "Implicit Deny: ACL sonundaki gizli 'tümünü reddet' kuralı",
    "### GÜVENLİK VE OTOMASYON ###",
    "SSH: Güvenli uzaktan erişim (Port 22)",
    "Port Security: Porta bağlanacak MAC sayısını kısıtlar",
    "Sticky MAC: Öğrenilen MAC adresini ayarlara kaydeder",
    "WLC: Kablosuz ağları merkezi yöneten denetleyici",
    "SDN: Yazılım tanımlı ağ yönetimi",
    "JSON/XML: Otomasyonda kullanılan veri formatları",
    "Ansible: Ajan gerektirmeyen otomasyon aracı (YAML kullanır)",
    "REST API: HTTP protokolü ile uygulama iletişimi",
    "Ping: Bağlantı kontrolü (ICMP)",
    "Traceroute: Hedefe giden yolu izleme"
]

class CCNAProTicker(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Pencere Ayarları ---
        self.title("CCNA Professional Ticker")
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0.95) # Çok hafif şeffaflık, netlik için yüksek tuttum
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        bar_height = 45 # Biraz daha yüksek, ferah görünüm için
        
        # Görev çubuğunun hemen üzerine yerleştir
        y_pos = screen_height - bar_height - 5 
        
        self.geometry(f"{screen_width}x{bar_height}+0+{y_pos}")
        self.configure(fg_color=BG_COLOR)

        # --- Değişkenler ---
        self.news_widgets = []   
        self.is_running = True
        self.drag_data = {"x": 0, "y": 0}
        
        # Listeyi karıştır (Dilerseniz kapatabilirsiniz)
        # random.shuffle(CCNA_NOTES)

        # --- Etkileşimler ---
        self.bind("<Button-3>", self.close_app)     
        self.bind("<ButtonPress-1>", self.start_drag) 
        self.bind("<B1-Motion>", self.do_drag)        

        # --- Başlatma ---
        self.setup_ticker_content()
        self.animate_ticker()

    def google_search(self, query):
        """Google araması yapar."""
        clean_query = query.replace("###", "").strip()
        base_url = "https://www.google.com/search?q=Cisco+CCNA+"
        final_url = base_url + clean_query.replace(" ", "+")
        webbrowser.open(final_url)

    def setup_ticker_content(self):
        """Notları oluşturur ve aralarına ayırıcı ekler."""
        current_x = self.winfo_screenwidth() 

        for i, note in enumerate(CCNA_NOTES):
            
            is_header = note.startswith("###")
            
            # --- Stil Ayarları ---
            # Başlıklar için farklı, normal notlar için farklı stil
            if is_header:
                clean_text = note.replace("###", "").strip()
                item_color = HEADER_COLOR
                item_font = (FONT_FAMILY, FONT_SIZE, "bold")
            else:
                clean_text = note
                item_color = TEXT_COLOR
                item_font = (FONT_FAMILY, FONT_SIZE)

            # --- 1. Not Etiketi ---
            lbl = ctk.CTkLabel(
                self, 
                text=clean_text,
                font=item_font,
                text_color=item_color,
                cursor="hand2"
            )
            
            # Tıklama ve Hover Efektleri
            lbl.bind("<Button-1>", lambda event, text=note: self.google_search(text))
            
            if not is_header:
                # Normal yazılar üzerine gelince parlasın
                lbl.bind("<Enter>", lambda event, l=lbl: l.configure(text_color=ACCENT_COLOR))
                lbl.bind("<Leave>", lambda event, l=lbl: l.configure(text_color=TEXT_COLOR))
            
            # Genişlik hesapla
            lbl.update_idletasks() 
            w = lbl.winfo_reqwidth()
            
            self.news_widgets.append({
                "label": lbl,
                "x": current_x,
                "width": w,
                "type": "note"
            })
            
            current_x += w 

            # --- 2. Ayırıcı (Separator) ---
            # Son eleman değilse araya nokta koy
            if i < len(CCNA_NOTES) - 1:
                sep_lbl = ctk.CTkLabel(
                    self,
                    text=" • ",
                    font=(FONT_FAMILY, FONT_SIZE + 4), # Nokta biraz büyük olsun
                    text_color=SEPARATOR_COLOR
                )
                
                sep_lbl.update_idletasks()
                sep_w = sep_lbl.winfo_reqwidth()
                
                # Ayıraçlar için biraz extra padding (boşluk) ekleyelim
                padding = 20
                
                self.news_widgets.append({
                    "label": sep_lbl,
                    "x": current_x + padding, # Biraz sağa ötele
                    "width": sep_w,
                    "type": "separator"
                })
                
                current_x += sep_w + (padding * 2) # Toplam boşluğu güncelle

    def animate_ticker(self):
        """Yumuşak kayan yazı animasyonu."""
        if not self.is_running:
            return

        # En sağdaki widget'ın bittiği yer
        right_most_edge = -99999
        if self.news_widgets:
            last_item = max(self.news_widgets, key=lambda i: i['x'])
            right_most_edge = last_item['x'] + last_item['width']

        for item in self.news_widgets:
            # Sola kaydır
            item['x'] -= SCROLL_SPEED
            
            # Ekranın solundan tamamen çıktı mı?
            if item['x'] + item['width'] < 0:
                # Kuyruğun en sonuna ekle + biraz boşluk bırak
                # Separator mantığından dolayı spacing'i dinamik ayarladık yukarıda,
                # burada sabit bir güvenlik boşluğu (ITEM_SPACING) ekliyoruz.
                item['x'] = right_most_edge + ITEM_SPACING
                right_most_edge = item['x'] + item['width']

            # Ekrana yerleştir (Dikey ortalama: bar_height 45 ise y=10-12 iyidir)
            item['label'].place(x=item['x'], y=10)

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
    app = CCNAProTicker()
    app.mainloop()