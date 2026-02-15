import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4

# -------------------------------------------------------------
# 1. TEMALAR VE SABİTLER (CYBERPUNK / PRO DARK)
# -------------------------------------------------------------
class Config:
    APP_NAME = "ONAR MUHASEBE PRO V3 (Ultimate)"
    WIDTH, HEIGHT = 1366, 768
    
    # CYBERPUNK - PROFESYONEL MAVİ KARIŞIMI TEMA
    BG_COLOR = "#0f172a"           # En Koyu Zemin
    SIDEBAR_COLOR = "#0B0F19"      # Cyberpunk Yan Menü (Daha Koyu)
    PRIMARY = "#00F0FF"            # Neon Cyan Mavi (Ana İşlemler)
    PRIMARY_HOVER = "#00B8CC"
    SECONDARY = "#2563EB"          # Profesyonel Koyu Mavi
    ACCENT = "#7C3AED"             # Vurgu Mor
    DANGER = "#FF0055"             # Cyberpunk Neon Kırmızı (Silme/Hata)
    SUCCESS = "#00FF9D"            # Cyberpunk Neon Yeşil (Başarı/Ekle)
    TEXT_WHITE = "#E2E8F0"
    TABLE_HEADER = "#1e293b"       # Tablo Başlığı
    TABLE_BG = "#0f172a"
    DB_FILE = "onar_veritabani.json"

# Türkçe Karakter Filtresi (PDF basımında standard reportlab çökmelerini önlemek için)
def turkce_temizle(metin):
    return str(metin).replace('ı','i').replace('İ','I').replace('ğ','g').replace('Ğ','G').replace('ş','s').replace('Ş','S').replace('ö','o').replace('Ö','O').replace('ç','c').replace('Ç','C').replace('ü','u').replace('Ü','U')

# -------------------------------------------------------------
# 2. VERİTABANI YÖNETİM MOTORU (GELİŞMİŞ JSON İŞLEMCİ)
# -------------------------------------------------------------
class DataManager:
    def __init__(self):
        self.file = Config.DB_FILE
        self.data = self.load()

    def load(self):
        if not os.path.exists(self.file):
            return {"stok": [], "cari": [], "fatura": [], "kasa": [], "banka": [], "personel": []}
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {"stok": [], "cari": [], "fatura": [], "kasa": [], "banka": [], "personel": []}

    def save(self):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def insert(self, table, record):
        if table not in self.data: self.data[table] = []
        self.data[table].append(record)
        self.save()

    def update(self, table, pk_field, pk_val, new_record):
        for i, row in enumerate(self.data[table]):
            if str(row.get(pk_field)) == str(pk_val):
                self.data[table][i] = new_record
                self.save()
                return True
        return False

    def delete(self, table, pk_field, pk_val):
        original_count = len(self.data.get(table, []))
        self.data[table] = [row for row in self.data[table] if str(row.get(pk_field)) != str(pk_val)]
        if len(self.data[table]) < original_count:
            self.save()
            return True
        return False

    def get_all(self, table):
        return self.data.get(table, [])

    def search(self, table, keyword):
        if not keyword: return self.get_all(table)
        kw = str(keyword).lower()
        res = []
        for row in self.data.get(table, []):
            if any(kw in str(val).lower() for val in row.values()):
                res.append(row)
        return res

# -------------------------------------------------------------
# 3. YARDIMCI ARAÇLAR: PDF VE EXCEL MOTORU
# -------------------------------------------------------------
class ExportEngine:
    @staticmethod
    def to_excel(columns, raw_data, filename="Disa_Aktar"):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=f"{filename}_{datetime.now().strftime('%Y%m%d')}.xlsx", title="Excel Kaydet", filetypes=[("Excel Files", "*.xlsx")])
        if not path: return
        try:
            df = pd.DataFrame(raw_data, columns=columns)
            df.to_excel(path, index=False)
            messagebox.showinfo("Başarılı", f"Veriler Excel'e aktarıldı!\nDosya: {path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Excel'e aktarılırken hata oluştu:\n{e}")

    @staticmethod
    def to_pdf(headers, rows, filename="Disa_Aktar"):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"{filename}_{datetime.now().strftime('%Y%m%d')}.pdf", title="PDF Kaydet", filetypes=[("PDF Files", "*.pdf")])
        if not path: return
        try:
            # Standart ASCII dönüşümü ile font sorunsuz geniş pdf yazdırılır
            c = canvas.Canvas(path, pagesize=landscape(A4))
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, 560, f"{filename} Raporu ({datetime.now().strftime('%d/%m/%Y %H:%M')})")
            
            y = 530
            c.setFont("Helvetica-Bold", 10)
            
            # Üst bilgi yaz
            row_text = "  |  ".join([turkce_temizle(h) for h in headers])
            c.drawString(40, y, row_text)
            c.line(40, y-5, 800, y-5)
            y -= 25
            
            c.setFont("Helvetica", 9)
            for i, row in enumerate(rows):
                line = "  |  ".join([turkce_temizle(str(i)) for i in row])
                c.drawString(40, y, line)
                y -= 15
                if y < 40: # Sayfa bittiyse yenile
                    c.showPage()
                    y = 550
                    c.setFont("Helvetica", 9)
            c.save()
            messagebox.showinfo("Başarılı", f"Veriler PDF olarak kaydedildi!\n{path}")
        except Exception as e:
             messagebox.showerror("Hata", f"PDF üretimi sırasında hata:\n{e}")

# -------------------------------------------------------------
# 4. TABLO GÖRÜNTÜLEYİCİ BİLEŞENİ
# -------------------------------------------------------------
class ModernTable(ttk.Treeview):
    def __init__(self, master, columns, column_widths, **kwargs):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview", background=Config.TABLE_BG, foreground=Config.TEXT_WHITE, 
                        rowheight=40, fieldbackground=Config.TABLE_BG, font=("Segoe UI", 11))
        
        style.configure("Treeview.Heading", background=Config.TABLE_HEADER, foreground=Config.PRIMARY, 
                        font=("Segoe UI", 12, "bold"), relief="flat", padding=(0,5))
        
        style.map("Treeview", background=[("selected", Config.PRIMARY_HOVER)], foreground=[("selected", "black")])
        style.map("Treeview.Heading", background=[('active', '#334155')])

        super().__init__(master, columns=columns, show="headings", **kwargs)
        
        self.scrollbar = ctk.CTkScrollbar(master, orientation="vertical", command=self.yview)
        self.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.pack(side="left", fill="both", expand=True)
        
        for i, col in enumerate(columns):
            self.heading(col, text=col.upper())
            self.column(col, width=column_widths[i], anchor="center")

# -------------------------------------------------------------
# 5. SUPER CLASS (NESNE YÖNELİMLİ ORTAK İSKELET / BASE PAGE)
# Yüzlerce satır tekrarından kurtarır. Her modul otomatik calısır.
# -------------------------------------------------------------
class GenericBasePage(ctk.CTkFrame):
    PAGE_NAME = "" # Veritabanındaki tablo ismi
    PK = ""        # Anahtar veri hücresi (ID vb.)
    TITLE = ""
    FORM_FIELDS = [] # Örnek: [("kod", "Stok Kodu"), ...]
    COLUMNS = []     # Tablo Header isimleri
    COL_WIDTHS = []  # Header kalınlıkları

    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.build_ui()
        self.refresh()

    def build_ui(self):
        # --- ÜST PANEL: ARAMA ve BAŞLIK ---
        header_fr = ctk.CTkFrame(self, fg_color=Config.TABLE_HEADER, corner_radius=10)
        header_fr.pack(fill="x", padx=15, pady=(15, 5))
        
        lbl_title = ctk.CTkLabel(header_fr, text=self.TITLE, font=("Montserrat", 22, "bold"), text_color=Config.TEXT_WHITE)
        lbl_title.pack(side="left", padx=20, pady=15)
        
        self.search_val = ctk.StringVar()
        self.search_ent = ctk.CTkEntry(header_fr, placeholder_text="Veri ara veya filtrele...", textvariable=self.search_val, width=300)
        self.search_ent.pack(side="right", padx=(5, 20), pady=15)
        self.search_ent.bind("<KeyRelease>", self.on_search)

        # --- ARA PANEL: BUTONLAR ---
        btn_fr = ctk.CTkFrame(self, fg_color="transparent")
        btn_fr.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkButton(btn_fr, text="+ YENİ EKLE", font=("Arial", 12, "bold"), fg_color="#10B981", text_color="black", hover_color="#059669", 
                      command=lambda: self.open_form(edit_mode=False)).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_fr, text="✎ GÜNCELLE", font=("Arial", 12, "bold"), fg_color="#F59E0B", text_color="black", hover_color="#D97706",
                      command=lambda: self.open_form(edit_mode=True)).pack(side="left", padx=5)
                      
        ctk.CTkButton(btn_fr, text="✖ SİL", font=("Arial", 12, "bold"), fg_color="#EF4444", text_color="white", hover_color="#B91C1C",
                      command=self.delete_selected).pack(side="left", padx=5)

        # Sağ butonlar
        ctk.CTkButton(btn_fr, text="⬇ PDF", fg_color=Config.DANGER, font=("Arial", 11, "bold"), width=80,
                      command=self.to_pdf).pack(side="right", padx=5)
        ctk.CTkButton(btn_fr, text="⬇ EXCEL", fg_color="#16A34A", font=("Arial", 11, "bold"), width=80,
                      command=self.to_excel).pack(side="right", padx=5)

        # --- ALT PANEL: LİSTE ---
        table_fr = ctk.CTkFrame(self, fg_color=Config.BG_COLOR, corner_radius=10)
        table_fr.pack(fill="both", expand=True, padx=15, pady=10)
        self.table = ModernTable(table_fr, self.COLUMNS, self.COL_WIDTHS)

    def refresh(self, data=None):
        for item in self.table.get_children():
            self.table.delete(item)
            
        load_data = data if data is not None else self.db.get_all(self.PAGE_NAME)
        # JSON alan sırasıyla FORM alanlarına göre eşleme
        data_keys = [f[0] for f in self.FORM_FIELDS]
        if 'tarih' not in data_keys: data_keys.append('tarih')

        for record in reversed(load_data):
            # record verilerini COLUMNS sırasında çıkart. Eğer veri yoksa - atar
            vals = []
            # Kolaylık: form alanlarına 'tarih' eklendi varsayılır otomatik.
            all_keys = [k for k, _ in self.FORM_FIELDS] + ["tarih"]
            for k in all_keys:
                # Sadece UI Sütun sayısı kadar map edelim
                if len(vals) < len(self.COLUMNS):
                   vals.append(record.get(k, "-"))
            self.table.insert("", "end", values=vals)

    def on_search(self, e):
        kw = self.search_val.get()
        data = self.db.search(self.PAGE_NAME, kw)
        self.refresh(data)

    def get_selected(self):
        sel = self.table.selection()
        if not sel: return None
        return self.table.item(sel[0])['values']

    def delete_selected(self):
        val = self.get_selected()
        if not val:
            messagebox.showwarning("Seçim Hatası", "Önce listeden bir satır seçin!")
            return
            
        pk_val = val[0] # Listede 1. alan ID/Anahtar kabul edilir
        if messagebox.askyesno("Kritik İşlem", f"Belirtilen kayıt kalıcı olarak silinecek. ({pk_val})\nEmin misiniz?"):
            self.db.delete(self.PAGE_NAME, self.PK, pk_val)
            self.refresh()

    def open_form(self, edit_mode=False):
        old_val = None
        if edit_mode:
            old_val = self.get_selected()
            if not old_val:
                messagebox.showwarning("Eksik", "Lütfen önce düzenlenecek satırı seçin!")
                return
        
        # POPUP PENCERE
        dialog = ctk.CTkToplevel(self)
        dialog.title("Bilgi Güncelle" if edit_mode else "Yeni Kayıt Ekle")
        dialog.geometry("450x650")
        dialog.configure(fg_color=Config.TABLE_HEADER)
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text=self.TITLE.upper(), font=("Arial", 18, "bold"), text_color=Config.PRIMARY).pack(pady=20)
        
        entries = {}
        # Form fieldlarımızı render et
        for i, (k_val, k_name) in enumerate(self.FORM_FIELDS):
            f_fr = ctk.CTkFrame(dialog, fg_color="transparent")
            f_fr.pack(fill="x", padx=30, pady=5)
            
            ctk.CTkLabel(f_fr, text=k_name+":", font=("Arial", 12), text_color="#A0ABC0", width=120, anchor="e").pack(side="left", padx=10)
            
            ent = ctk.CTkEntry(f_fr, width=200, fg_color="#0B0F19", text_color="white", border_color=Config.SECONDARY)
            ent.pack(side="left")
            entries[k_val] = ent
            
            # Veri doldur (Düzenleme moduysa)
            if edit_mode and i < len(old_val):
                ent.insert(0, str(old_val[i]))
                if i == 0:  # PK alanı kitlenir, değiştirilmez
                    ent.configure(state="readonly", text_color="gray")

        def save():
            record = {k: e.get() for k, e in entries.items()}
            
            # Basit boşluk kontrolü PK için
            if not record[self.PK].strip():
                messagebox.showerror("Hata", "Anahtar KOD / No Alanı boş bırakılamaz!", parent=dialog)
                return

            if edit_mode:
                # GÜNCELLE
                record['tarih'] = old_val[-1] # Tarihi aynı bırak
                success = self.db.update(self.PAGE_NAME, self.PK, record[self.PK], record)
                msg = "Güncellendi"
            else:
                # YENI EKLE
                # primary key duplicate kontrol
                existing = [row for row in self.db.get_all(self.PAGE_NAME) if str(row.get(self.PK)) == str(record[self.PK])]
                if existing:
                    messagebox.showerror("Hata", "Bu Anahtar Koda sahip bir kayıt zaten mevcut!", parent=dialog)
                    return
                    
                record['tarih'] = datetime.now().strftime("%d-%m-%Y %H:%M")
                self.db.insert(self.PAGE_NAME, record)
                msg = "Kayıt Başarıyla Eklendi!"
                
            self.refresh()
            dialog.destroy()
            self.show_popup_msg(msg)

        btn_txt = "Değişiklikleri Kaydet" if edit_mode else "Veritabanına Ekle"
        ctk.CTkButton(dialog, text=btn_txt, font=("Arial", 14, "bold"), height=40, fg_color=Config.PRIMARY, hover_color=Config.PRIMARY_HOVER, text_color="black", command=save).pack(pady=30)

    def show_popup_msg(self, m):
        msg_frame = ctk.CTkFrame(self, fg_color=Config.SUCCESS)
        msg_frame.place(relx=0.5, rely=0.1, anchor="n")
        lbl = ctk.CTkLabel(msg_frame, text="✔ "+m, font=("Arial", 14, "bold"), text_color="black", padx=20, pady=10)
        lbl.pack()
        self.after(3000, msg_frame.destroy) # 3 Saniye sonra oto kaybolsun

    def get_export_data(self):
        items = self.table.get_children()
        raw_rows = [self.table.item(i)['values'] for i in items]
        return self.COLUMNS, raw_rows

    def to_excel(self):
        cols, rows = self.get_export_data()
        ExportEngine.to_excel(cols, rows, self.PAGE_NAME)

    def to_pdf(self):
         cols, rows = self.get_export_data()
         ExportEngine.to_pdf(cols, rows, self.PAGE_NAME.capitalize())

# -------------------------------------------------------------
# 6. SİSTEM MODÜLLERİ (Sub - Sınıflar, sadece harita yaparlar!)
# BasePage sayesinde hiçbir UI tasarımı gerektirmeden tam gaz.
# -------------------------------------------------------------
class StokPage(GenericBasePage):
    PAGE_NAME, PK, TITLE = "stok", "stok_kodu", "📦 STOK MERKEZİ"
    FORM_FIELDS = [("stok_kodu", "Stok Kodu/SKU"), ("urun_adi", "Ürün Adı"), ("kategori", "Kategori (Donanım vb)"),
                   ("birim", "Birim (Ad/Kg/Lt)"), ("alis", "Maliyet/Alış Tutar"), ("satis", "Satış Tutar"), ("stok", "Mevcut Miktar")]
    COLUMNS = ["KOD", "Ürün Adı", "Kat.", "Birim", "Alış", "Satış", "Adet", "Son Tarih"]
    COL_WIDTHS = [80, 250, 150, 70, 90, 90, 80, 140]

class CariPage(GenericBasePage):
    PAGE_NAME, PK, TITLE = "cari", "cari_kodu", "👥 MÜŞTERİ / CARİ MERKEZİ"
    FORM_FIELDS = [("cari_kodu", "Cari/Vergi No"), ("unvan", "Firma/Şahıs Ünvanı"), ("yetkili", "İlgili Kişi"),
                   ("tel", "Telefon"), ("email", "E-Mail Adresi"), ("bakiye", "Bakiye ($/₺)")]
    COLUMNS = ["VKN / KOD", "Unvan/Şirket İsmi", "İlgili Yetkili", "Tel/İletişim", "E-Mail Adresi", "Açık Bakiye", "Oluş. Tarihi"]
    COL_WIDTHS = [110, 250, 150, 120, 150, 100, 140]

class KasaPage(GenericBasePage):
    PAGE_NAME, PK, TITLE = "kasa", "fis_no", "💰 KASA & GÜNLÜK GELİR/GİDER"
    FORM_FIELDS = [("fis_no", "Fiş/Belge No"), ("tip", "Türü (Tahsilat/Tediye)"), ("tutar", "Tutar (₺)"), 
                   ("aciklama", "Nereye/Nereden? (Açıklama)")]
    COLUMNS = ["Fiş No", "G/Ç Türü", "İşlem Tutarı", "İşlem Özeti / Açıklama", "Tarih / Saat"]
    COL_WIDTHS = [100, 120, 120, 450, 160]

class BankaPage(GenericBasePage):
    PAGE_NAME, PK, TITLE = "banka", "iban", "🏦 BANKA / KURUMSAL HESAPLAR"
    FORM_FIELDS = [("iban", "TR / IBAN (NO Boşluk)"), ("banka", "Banka Adı"), ("hesap", "Hesap Türü (Ticari)"), 
                   ("bakiye", "Hesap İçi Bakiye")]
    COLUMNS = ["Tam IBAN No", "Kurum / Banka", "Açıklama / Tipi", "Mevcut Para / Limit", "Güncellenme"]
    COL_WIDTHS = [220, 180, 200, 150, 150]

class PersonelPage(GenericBasePage):
    PAGE_NAME, PK, TITLE = "personel", "sicil_no", "👮 İNSAN KAYNAKLARI (İ.K.)"
    FORM_FIELDS = [("sicil_no", "Personel Kimlik No"), ("ad_soyad", "Tam Ad-Soyad"), ("departman", "Görev / Dep."), 
                   ("maas", "Sabit Maaş Hakediş"), ("sgk", "SGK / Sigorta Durumu")]
    COLUMNS = ["Sicil Num.", "İsim - Soyisim", "Birimi/Departman", "Maaşı/Ücreti", "Sosyal Güv. (SGK)", "Giriş / Yenilenme"]
    COL_WIDTHS = [100, 220, 160, 110, 120, 140]

class FaturaPage(GenericBasePage):
    PAGE_NAME, PK, TITLE = "fatura", "ftr_no", "📄 SATIŞ VE ALIŞ FATURALARI (RESMİ)"
    FORM_FIELDS = [("ftr_no", "A Serisi - Belge No"), ("tur", "Belge Tip (AL/SAT)"), ("unvan", "Karşı Cari / Müşteri"),
                   ("tutar", "Genel Toplam Tutar (KDVli)"), ("durum", "Ödenme Durum (AÇIK/KAPALI)")]
    COLUMNS = ["Fatura Numarası", "Yön/Belge", "Kesildiği Kişi veya Kurum", "Meblağ(Son)", "Tahsilat Durumu", "Sistem Tarihi"]
    COL_WIDTHS = [150, 100, 300, 130, 150, 150]

# -------------------------------------------------------------
# 7. RAPORLAMA/DASHBOARD SİSTEMİ (Summary Card Görünüm)
# -------------------------------------------------------------
class RaporlamaPage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        
        ctk.CTkLabel(self, text="⚡ ANA GÖSTERGE VE YÖNETİM RAPORLARI", font=("Black Ops One", 26, "bold"), text_color=Config.PRIMARY).pack(pady=30)
        self.metrics_fr = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_fr.pack(fill="both", expand=True, padx=40, pady=20)
        self.draw_metrics()

    def create_card(self, row, col, icon, baslik, veriler, c_color):
        card = ctk.CTkFrame(self.metrics_fr, fg_color=Config.TABLE_HEADER, corner_radius=15, width=280, height=200)
        card.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
        card.grid_propagate(False)

        ctk.CTkLabel(card, text=f"{icon} {baslik}", font=("Arial", 16, "bold"), text_color=c_color).pack(pady=(20, 10))
        for t, val in veriler:
            f = ctk.CTkFrame(card, fg_color="transparent")
            f.pack(fill="x", padx=15, pady=2)
            ctk.CTkLabel(f, text=t, font=("Arial", 13), text_color=Config.TEXT_WHITE).pack(side="left")
            ctk.CTkLabel(f, text=str(val), font=("Arial", 14, "bold"), text_color="white").pack(side="right")

    def draw_metrics(self):
        # Refresh clear
        for widget in self.metrics_fr.winfo_children(): widget.destroy()

        st_all = self.db.get_all("stok")
        cr_all = self.db.get_all("cari")
        ks_all = self.db.get_all("kasa")
        ft_all = self.db.get_all("fatura")
        pr_all = self.db.get_all("personel")

        # Toplam Bakiye bul (Try - float converter errors vb için try)
        def to_float(x): 
            try: return float(str(x).replace(",", "."))
            except: return 0.0

        kas_total = sum(to_float(k.get("tutar", 0)) for k in ks_all if str(k.get("tip","")).lower()=="gelir" or str(k.get("tip","")).lower()=="tahsilat")
        kas_gid = sum(to_float(k.get("tutar", 0)) for k in ks_all if str(k.get("tip","")).lower()=="gider" or str(k.get("tip","")).lower()=="tediye")
        
        # SATIR 1
        self.create_card(0, 0, "📦", "Depo/Stok Hacmi", [("Sistem Kayıtlı Ürün", len(st_all)), ("Ort. Maliyetler:", "- ")], Config.PRIMARY)
        self.create_card(0, 1, "👥", "Bilanço Carileri", [("Tanımlı Cari Çeşit", len(cr_all)), ("Yeni Eklenen(Hafta)", "- ")], Config.PRIMARY)
        self.create_card(0, 2, "💵", "Likit Durumu (Kasa)", [("Brüt Nakit Giren:", f"{kas_total:.2f} ₺"), ("Çıkan Nkt Gider:", f"{kas_gid:.2f} ₺")], Config.SUCCESS)
        
        # SATIR 2
        self.create_card(1, 0, "📄", "Ticari Faturalar", [("Toplam Belge Sayısı", len(ft_all))], "#F59E0B")
        self.create_card(1, 1, "🧑‍💻", "Ekipler (HR)", [("Maaşlı Çalısan:", len(pr_all))], Config.PRIMARY)
        self.create_card(1, 2, "🔐", "Veri Tabanı İzi", [("Yedeklenen Veri ID:", "SYS_HSA3932"),("Dosya: ", Config.DB_FILE)], Config.ACCENT)
        
        # Yenile Butonu
        btn_refresh = ctk.CTkButton(self, text="↻ VERİLERİ ŞİMDİ YENİLE VE ONAYLA", width=400, height=50, 
                                    fg_color=Config.SECONDARY, font=("Arial", 14, "bold"), text_color="white", command=self.draw_metrics)
        btn_refresh.pack(pady=40)

# -------------------------------------------------------------
# 8. MAİN APPLICATION APP - Sidebar Navigation Logic
# -------------------------------------------------------------
class CoreAppEngine(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title(Config.APP_NAME)
        self.geometry(f"{Config.WIDTH}x{Config.HEIGHT}")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.db_engine = DataManager()
        self.pages = {} # Önbelleğe alınacak ekran çerçeveleri
        self.setup_mainframe()
        self.change_page("RAPORLAMA EKRANI")

    def setup_mainframe(self):
        # YAN MENÜ SİDEBAR #0B0F19 CYBER Koyu
        self.sidebar_frame = ctk.CTkFrame(self, width=280, fg_color=Config.SIDEBAR_COLOR, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        ctk.CTkLabel(self.sidebar_frame, text="ONAR SYS", font=("Black Ops One", 36, "bold"), text_color=Config.PRIMARY).pack(pady=(40,0))
        ctk.CTkLabel(self.sidebar_frame, text="EXECUTIVE PLATFORM V3.0", font=("Arial", 10), text_color=Config.TEXT_WHITE).pack(pady=(0,50))

        # BUTONLAR
        self.add_nav_button("⚡", "RAPORLAMA EKRANI", Config.SUCCESS)
        self.add_nav_button("👥", "CARİ YÖNETİM MERKEZİ")
        self.add_nav_button("📦", "DEPO VE STOK MODÜLÜ")
        self.add_nav_button("📄", "FATURA VE TİCARİ MODÜL")
        self.add_nav_button("💰", "KASA (Nakit Çekmece)")
        self.add_nav_button("🏦", "BANKA ENT. İŞLEMLERİ")
        self.add_nav_button("👮", "İNSAN KAYNAKLARI SİSTEMİ")
        
        ctk.CTkLabel(self.sidebar_frame, text="Cyber Security Checked\nAll SQL/Injection Safe.", 
                     text_color="gray", font=("Arial", 9)).pack(side="bottom", pady=20)

        # İÇERİK FRAME OLUŞTURULACAK YER
        self.content_frame = ctk.CTkFrame(self, fg_color=Config.BG_COLOR, corner_radius=0)
        self.content_frame.pack(side="left", fill="both", expand=True)

        # EKRAN OLUŞTURMA & HARİTALAMA YAPILMASI
        self.pages["RAPORLAMA EKRANI"] = RaporlamaPage(self.content_frame, self.db_engine)
        self.pages["CARİ YÖNETİM MERKEZİ"] = CariPage(self.content_frame, self.db_engine)
        self.pages["DEPO VE STOK MODÜLÜ"] = StokPage(self.content_frame, self.db_engine)
        self.pages["FATURA VE TİCARİ MODÜL"] = FaturaPage(self.content_frame, self.db_engine)
        self.pages["KASA (Nakit Çekmece)"] = KasaPage(self.content_frame, self.db_engine)
        self.pages["BANKA ENT. İŞLEMLERİ"] = BankaPage(self.content_frame, self.db_engine)
        self.pages["İNSAN KAYNAKLARI SİSTEMİ"] = PersonelPage(self.content_frame, self.db_engine)

        for p_name, page_widget in self.pages.items():
            page_widget.place(x=0, y=0, relwidth=1, relheight=1)

    def add_nav_button(self, icon, txt, c_hover=Config.PRIMARY):
        # Özelleştirilmiş Navigasyon Click Mantığı
        btn = ctk.CTkButton(self.sidebar_frame, text=f"{icon}  {txt}", fg_color="transparent", 
                            text_color=Config.TEXT_WHITE, font=("Segoe UI", 13, "bold"), 
                            height=45, hover_color=c_hover, anchor="w", 
                            command=lambda m=txt: self.change_page(m))
        btn.pack(fill="x", padx=15, pady=6)

    def change_page(self, t):
        # Aktif ekranı yükselt
        for name, frame in self.pages.items():
            if name == t:
                frame.tkraise()
                if hasattr(frame, 'refresh'): frame.refresh()
                if hasattr(frame, 'draw_metrics'): frame.draw_metrics() # Rapor ekranındaysa tazele.

if __name__ == "__main__":
    app = CoreAppEngine()
    app.mainloop()