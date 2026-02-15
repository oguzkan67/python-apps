import customtkinter as ctk
import requests
from bs4 import BeautifulSoup
import re
import threading
from urllib.parse import urljoin, urlparse

# --- Uygulama Ayarları ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PrivacyAuditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Yapılandırması
        self.title("Privacy Auditor Pro - Gizlilik Analiz Uzmanı")
        self.geometry("1100x800")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Veri Seti (Regex Kuralları - TR/EN) ---
        self.risk_patterns = [
            (r"sell.*data", -35, "⚠️ Veri Satışı"),
            (r"share.*third.*part", -20, "⚠️ 3. Taraflarla Paylaşım"),
            (r"advertis.*partner", -15, "⚠️ Reklam Ortaklığı"),
            (r"track.*location", -25, "⚠️ Konum Takibi"),
            (r"voice.*record", -25, "⚠️ Ses Kaydı"),
            (r"collect.*contact", -15, "⚠️ Rehber Erişimi"),
            (r"verilerinizi sat", -35, "⚠️ Veri Satışı (TR)"),
            (r"üçüncü taraf.*paylaş", -20, "⚠️ 3. Taraf Paylaşımı (TR)"),
            (r"reklam.*amaçlı", -15, "⚠️ Reklam Kullanımı (TR)"),
            (r"konum.*işle", -25, "⚠️ Konum İşleme (TR)"),
        ]

        self.trust_patterns = [
            (r"do not sell", 20, "✅ Satış Yapmama Garantisi"),
            (r"won't sell", 20, "✅ Satış Yapmama Garantisi"),
            (r"encrypted", 10, "✅ Şifreleme (Encryption)"),
            (r"ssl", 5, "✅ SSL Güvenliği"),
            (r"gdpr", 15, "✅ GDPR Uyumu"),
            (r"kvkk", 15, "✅ KVKK Uyumu"),
            (r"delete.*account", 10, "✅ Hesap Silme Hakkı"),
            (r"satmıyoruz", 20, "✅ Satış Yapmama (TR)"),
            (r"paylaşmıyoruz", 15, "✅ Paylaşmama (TR)"),
        ]

        self.create_ui()

    def create_ui(self):
        # 1. Başlık Alanı
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, height=60, fg_color="#1a1a1a")
        self.header_frame.grid(row=0, column=0, sticky="ew")
        
        title_lbl = ctk.CTkLabel(self.header_frame, text="🛡️ PRIVACY AUDITOR PRO", font=("Roboto", 24, "bold"), text_color="#4F9FE0")
        title_lbl.pack(pady=15)

        # 2. Ana İçerik (Tab View)
        self.tab_view = ctk.CTkTabview(self, width=1000, height=600)
        self.tab_view.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        self.tab_url = self.tab_view.add("🌐 URL Tarama Modu")
        self.tab_text = self.tab_view.add("📝 Manuel Metin Modu")

        self.setup_url_tab()
        self.setup_text_tab()

        # 3. Sonuç Paneli
        self.results_frame = ctk.CTkFrame(self, height=200)
        self.results_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.results_frame.grid_rowconfigure(1, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)

        # Skor Göstergesi
        self.score_header = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        self.score_header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.lbl_score = ctk.CTkLabel(self.score_header, text="GÜVEN SKORU: --", font=("Roboto", 30, "bold"), text_color="gray")
        self.lbl_score.pack(side="left", padx=20)

        self.lbl_status = ctk.CTkLabel(self.score_header, text="Durum: Bekleniyor", font=("Roboto", 16))
        self.lbl_status.pack(side="right", padx=20)

        # Rapor Metin Kutusu
        self.report_box = ctk.CTkTextbox(self.results_frame, font=("Consolas", 13), wrap="word")
        self.report_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # --- DÜZELTİLEN KISIM ---
        # CustomTkinter tag_config içinde 'font' parametresini desteklemez.
        # Sadece renkleri ayarlıyoruz.
        self.report_box.tag_config("risk", foreground="#FF5555", background="#330000") 
        self.report_box.tag_config("safe", foreground="#00FF7F", background="#003300")
        self.report_box.tag_config("info", foreground="#DDDDDD")
        self.report_box.tag_config("url_highlight", foreground="#4F9FE0") 
        # ------------------------

    def setup_url_tab(self):
        container = ctk.CTkFrame(self.tab_url, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(container, text="Web Sitesi Adresi (Örn: tiktok.com):", font=("Roboto", 14)).pack(pady=5)
        
        self.entry_url = ctk.CTkEntry(container, width=500, placeholder_text="https://...")
        self.entry_url.pack(pady=10)
        
        self.btn_scan_url = ctk.CTkButton(container, text="🔍 Sözleşmeyi Bul ve Analiz Et", 
                                        command=self.start_url_scan, 
                                        fg_color="#1F6AA5", font=("Roboto", 14, "bold"), height=40)
        self.btn_scan_url.pack(pady=10)
        
        self.lbl_url_status = ctk.CTkLabel(container, text="Hazır", text_color="#AAAAAA")
        self.lbl_url_status.pack(pady=5)

    def setup_text_tab(self):
        container = ctk.CTkFrame(self.tab_text, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(container, text="Gizlilik Sözleşmesi Metnini Buraya Yapıştırın:", font=("Roboto", 14)).pack(pady=5)
        
        self.txt_input_manual = ctk.CTkTextbox(container, width=800, height=200)
        self.txt_input_manual.pack(pady=10, fill="both", expand=True)
        
        self.btn_scan_text = ctk.CTkButton(container, text="⚡ Metni Analiz Et", 
                                         command=self.start_text_scan,
                                         fg_color="#2A8C55", font=("Roboto", 14, "bold"), height=40)
        self.btn_scan_text.pack(pady=10)

    # --- İŞLEM FONKSİYONLARI ---

    def start_url_scan(self):
        url = self.entry_url.get().strip()
        if not url: return
        
        self.btn_scan_url.configure(state="disabled")
        self.report_box.configure(state="normal")
        self.report_box.delete("0.0", "end")
        self.report_box.configure(state="disabled")
        
        threading.Thread(target=self.process_url_thread, args=(url,), daemon=True).start()

    def start_text_scan(self):
        text = self.txt_input_manual.get("0.0", "end").strip()
        if len(text) < 50:
            self.log_to_report("⚠️ Lütfen analiz için yeterli uzunlukta metin girin.", "info")
            return
            
        self.btn_scan_text.configure(state="disabled")
        self.log_to_report("⚡ Manuel metin analizi başlatılıyor...\n", "info")
        
        threading.Thread(target=self.process_text_thread, args=(text,), daemon=True).start()

    def log_to_report(self, message, tag="info"):
        self.report_box.configure(state="normal")
        self.report_box.insert("end", f"{message}\n", tag)
        self.report_box.see("end")
        self.report_box.configure(state="disabled")

    # --- URL BULMA VE ÇEKME ---

    def get_headers(self):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8',
        }

    def process_url_thread(self, url):
        self.lbl_url_status.configure(text="Siteye bağlanılıyor...")
        
        if not url.startswith("http"):
            url = "https://" + url

        try:
            domain = urlparse(url).netloc
            base_url = f"https://{domain}"

            self.log_to_report(f"🌐 Hedef Site: {base_url}", "url_highlight")
            self.log_to_report("⏳ Gizlilik Sözleşmesi (Privacy Policy) aranıyor...", "info")

            found_url, content = self.find_policy_link(base_url)

            if not found_url:
                self.log_to_report("⚠️ Ana sayfada link bulunamadı. Derin tarama başlatılıyor...", "info")
                found_url, content = self.brute_force_policy(base_url)

            if found_url and content:
                self.log_to_report(f"\n✅ BAŞARILI! Sözleşme Bulundu.", "safe")
                self.log_to_report(f"🔗 Link: {found_url}\n", "url_highlight")
                self.lbl_url_status.configure(text="Sözleşme bulundu, analiz ediliyor...")
                self.analyze_text(content)
            else:
                self.log_to_report("\n❌ HATA: Gizlilik sözleşmesi otomatik olarak bulunamadı.", "risk")
                self.log_to_report("🔍 Olası Sebepler:\n1. Site ağır bot koruması (Cloudflare vb.) kullanıyor.\n2. Site içeriği tamamen JavaScript ile yükleniyor.\n\n💡 Çözüm: Sözleşme metnini manuel kopyalayıp 'Manuel Metin Modu' sekmesini kullanın.", "info")
                self.update_score(0, "Veri Alınamadı", "#FF5555")

        except Exception as e:
            self.log_to_report(f"Hata oluştu: {str(e)}", "risk")
        finally:
            self.btn_scan_url.configure(state="normal")
            self.lbl_url_status.configure(text="İşlem Tamamlandı")

    def find_policy_link(self, base_url):
        try:
            resp = requests.get(base_url, headers=self.get_headers(), timeout=5)
            if resp.status_code != 200: return None, None
            
            soup = BeautifulSoup(resp.content, 'html.parser')
            keywords = ["privacy", "policy", "gizlilik", "kvkk", "legal", "terms"]
            
            for a in soup.find_all('a', href=True):
                link_text = a.text.lower()
                link_href = a['href'].lower()
                
                if any(k in link_text for k in keywords) or any(k in link_href for k in keywords):
                    if "login" in link_href or "signup" in link_href: continue
                    full_url = urljoin(base_url, a['href'])
                    
                    try:
                        p_resp = requests.get(full_url, headers=self.get_headers(), timeout=5)
                        p_soup = BeautifulSoup(p_resp.content, 'html.parser')
                        text = self.clean_html(p_soup)
                        if len(text) > 1000:
                            return full_url, text
                    except:
                        continue
            return None, None
        except:
            return None, None

    def brute_force_policy(self, base_url):
        common_paths = [
            "/privacy", "/privacy-policy", "/legal/privacy-policy", 
            "/gizlilik", "/gizlilik-politikasi", "/yasal/gizlilik",
            "/legal", "/kvkk", "/policy", "/about/privacy"
        ]
        
        for path in common_paths:
            target_url = urljoin(base_url, path)
            try:
                self.log_to_report(f"Deneniyor: {path}...", "info")
                resp = requests.get(target_url, headers=self.get_headers(), timeout=3)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, 'html.parser')
                    text = self.clean_html(soup)
                    
                    if len(text) > 500 and ("privacy" in text.lower() or "gizlilik" in text.lower()):
                        return target_url, text
            except:
                continue
        return None, None

    def clean_html(self, soup):
        for script in soup(["script", "style", "header", "footer", "nav", "aside", "form"]):
            script.decompose()
        return " ".join(soup.get_text().split())

    def process_text_thread(self, text):
        self.report_box.configure(state="normal")
        self.report_box.delete("0.0", "end")
        self.report_box.configure(state="disabled")
        self.analyze_text(text)
        self.btn_scan_text.configure(state="normal")

    def analyze_text(self, text):
        self.log_to_report("\n📊 Analiz Başlatılıyor...\n" + "="*40, "info")
        
        score = 100
        sentences = [s.strip() for s in re.split(r'[.!?]\s+', text) if len(s) > 20]
        findings = []

        if not sentences:
            self.log_to_report("⚠️ Analiz edilecek anlamlı cümle bulunamadı.", "info")
            return

        for sentence in sentences:
            s_lower = sentence.lower()
            
            for pattern, penalty, msg in self.risk_patterns:
                if re.search(pattern, s_lower):
                    score += penalty
                    display_text = (sentence[:100] + '...') if len(sentence) > 100 else sentence
                    findings.append(("risk", f"[-] {msg} ({penalty} Puan)\n    \"{display_text}\""))

            for pattern, bonus, msg in self.trust_patterns:
                if re.search(pattern, s_lower):
                    score += bonus
                    display_text = (sentence[:100] + '...') if len(sentence) > 100 else sentence
                    findings.append(("safe", f"[+] {msg} (+{bonus} Puan)\n    \"{display_text}\""))

        score = max(0, min(100, score))
        self.after(0, lambda: self.finalize_report(score, findings))

    def finalize_report(self, score, findings):
        if score >= 80:
            color = "#2CC985"
            verdict = "GÜVENLİ"
        elif score >= 50:
            color = "#FFAA00"
            verdict = "DİKKAT EDİLMELİ"
        else:
            color = "#FF4646"
            verdict = "YÜKSEK RİSK"

        self.update_score(score, verdict, color)

        if not findings:
            self.log_to_report("\nHerhangi bir risk veya güven ifadesi tespit edilemedi. Standart metin olabilir.", "info")
        else:
            for tag, text in findings:
                self.log_to_report(text + "\n", tag)
            
        self.log_to_report("\n" + "="*40 + "\nAnaliz Tamamlandı.", "info")

    def update_score(self, score, verdict, color):
        self.lbl_score.configure(text=f"GÜVEN SKORU: {score}/100", text_color=color)
        self.lbl_status.configure(text=f"Durum: {verdict}", text_color=color)

if __name__ == "__main__":
    app = PrivacyAuditorApp()
    app.mainloop()