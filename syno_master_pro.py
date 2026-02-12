import customtkinter as ctk
import requests
import threading # Uygulamanın donmasını engellemek için

class SynoMasterPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Syno-Master // Academic Intelligence")
        self.geometry("950x650")
        ctk.set_appearance_mode("dark")
        
        self.history_list = []
        self.popup_window = None # Aynı anda birden fazla popup açılmasını engeller
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_frames()
        self.show_frame("search")

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#0a0a0a")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar_frame, text="SYNO\nMASTER", 
                     font=ctk.CTkFont(family="Consolas", size=28, weight="bold"),
                     text_color="#00ffcc").pack(pady=40)

        self.btn_search = ctk.CTkButton(self.sidebar_frame, text="🔍 Thesaurus", 
                                        fg_color="transparent", hover_color="#1a1a1a",
                                        command=lambda: self.show_frame("search"))
        self.btn_search.pack(pady=10, padx=20, fill="x")
        
        self.btn_history = ctk.CTkButton(self.sidebar_frame, text="📜 History", 
                                         fg_color="transparent", hover_color="#1a1a1a",
                                         command=lambda: self.show_frame("history"))
        self.btn_history.pack(pady=10, padx=20, fill="x")

        self.status_box = ctk.CTkFrame(self.sidebar_frame, fg_color="#141414", corner_radius=10)
        self.status_box.pack(side="bottom", fill="x", padx=20, pady=20)
        self.status_lbl = ctk.CTkLabel(self.status_box, text="Ready", font=("Arial", 11), text_color="#2ecc71")
        self.status_lbl.pack(pady=10)

    def setup_main_frames(self):
        # Arama Sayfası
        self.search_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#141414")
        self.search_container = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        self.search_container.pack(pady=35, padx=50, fill="x")

        self.entry = ctk.CTkEntry(self.search_container, width=400, height=50, 
                                   placeholder_text="Scan for academic alternatives...",
                                   font=("Arial", 14), border_color="#333", corner_radius=12)
        self.entry.pack(side="left", padx=(0, 15), fill="x", expand=True)
        self.entry.bind("<Return>", lambda e: self.find_synonyms())

        self.search_btn = ctk.CTkButton(self.search_container, text="ANALYZE", width=140, height=50,
                                        font=("Arial", 14, "bold"), fg_color="#00ffcc", 
                                        text_color="#000", corner_radius=12, command=self.find_synonyms)
        self.search_btn.pack(side="right")

        self.result_frame = ctk.CTkScrollableFrame(self.search_frame, fg_color="transparent")
        self.result_frame.pack(pady=10, padx=40, fill="both", expand=True)

        # Geçmiş Sayfası
        self.history_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#141414")
        ctk.CTkLabel(self.history_frame, text="SEARCH HISTORY", font=("Consolas", 20, "bold"), text_color="#00ffcc").pack(pady=30)
        self.history_scroll = ctk.CTkScrollableFrame(self.history_frame, fg_color="transparent")
        self.history_scroll.pack(pady=10, padx=40, fill="both", expand=True)

    def show_frame(self, frame_name):
        if frame_name == "search":
            self.history_frame.grid_forget()
            self.search_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
            self.btn_search.configure(fg_color="#1a1a1a")
            self.btn_history.configure(fg_color="transparent")
        else:
            self.search_frame.grid_forget()
            self.history_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
            self.btn_history.configure(fg_color="#1a1a1a")
            self.btn_search.configure(fg_color="transparent")
            self.update_history_ui()

    def find_synonyms(self):
        word = self.entry.get().strip().lower()
        if not word: return
        
        if word not in self.history_list:
            self.history_list.insert(0, word)
        
        self.status_lbl.configure(text="Searching...", text_color="#f1c40f")
        threading.Thread(target=self._api_find_synonyms, args=(word,), daemon=True).start()

    def _api_find_synonyms(self, word):
        url = f"https://api.datamuse.com/words?ml={word}&max=12"
        try:
            response = requests.get(url, timeout=5).json()
            # UI güncellemeleri ana thread üzerinde yapılmalı
            self.after(0, lambda: self._update_results_ui(response, word))
        except Exception as e:
            self.after(0, lambda: self.status_lbl.configure(text="Connection Error", text_color="red"))

    def _update_results_ui(self, response, word):
        for widget in self.result_frame.winfo_children(): widget.destroy()
        sorted_data = sorted(response, key=lambda x: x.get('score', 0), reverse=True)
        for item in sorted_data:
            self.create_result_card(self.result_frame, item['word'], item.get('score', 0))
        self.status_lbl.configure(text=f"Ready for '{word}'", text_color="#2ecc71")

    def fetch_details(self, word):
        """Detayları ayrı bir thread içinde getirerek donmayı önler."""
        self.status_lbl.configure(text=f"Loading {word}...", text_color="#00ffcc")
        threading.Thread(target=self._api_fetch_details, args=(word,), daemon=True).start()

    def _api_fetch_details(self, word):
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        try:
            res = requests.get(url, timeout=5).json()
            if isinstance(res, list):
                # Örneği bulana kadar tüm anlamları tara
                definition = "No definition found."
                example = "No academic example found."
                for m in res[0].get('meanings', []):
                    for d in m.get('definitions', []):
                        if definition == "No definition found.":
                            definition = d.get('definition', definition)
                        if d.get('example'):
                            example = d.get('example')
                            break
                    if example != "No academic example found.": break
                self.after(0, lambda: self.show_pro_popup(word, definition, example))
            else:
                self.after(0, lambda: self.show_pro_popup(word, "Definition not found in database.", "N/A"))
        except:
            self.after(0, lambda: self.show_pro_popup(word, "Network error while fetching details.", "N/A"))
        
        self.after(0, lambda: self.status_lbl.configure(text="Ready", text_color="#2ecc71"))

    def show_pro_popup(self, word, definition, example):
        # Eski popup açıksa kapat
        if self.popup_window is not None and self.popup_window.winfo_exists():
            self.popup_window.destroy()

        self.popup_window = ctk.CTkToplevel(self)
        self.popup_window.title(f"Details: {word}")
        self.popup_window.geometry("500x420")
        self.popup_window.attributes("-topmost", True)
        self.popup_window.configure(fg_color="#0a0a0a")
        
        container = ctk.CTkFrame(self.popup_window, fg_color="#141414", corner_radius=20, border_width=1, border_color="#00ffcc")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(container, text=word.upper(), font=("Consolas", 26, "bold"), text_color="#00ffcc").pack(pady=20)
        
        def_box = ctk.CTkTextbox(container, height=90, fg_color="transparent", font=("Arial", 13))
        def_box.insert("0.0", f"DEFINITION:\n{definition}"); def_box.configure(state="disabled"); def_box.pack(fill="x", padx=25)
        
        ex_box = ctk.CTkTextbox(container, height=90, fg_color="#0d0d0d", font=("Arial", 13, "italic"), text_color="#00ffcc")
        ex_box.insert("0.0", f"EXAMPLE USAGE:\n\"{example}\""); ex_box.configure(state="disabled"); ex_box.pack(fill="x", padx=25, pady=20)
        ctk.CTkButton(container, text="CLOSE", fg_color="#333", command=self.popup_window.destroy).pack(side="bottom", pady=20)

    # --- Diğer yardımcı fonksiyonlar (create_result_card, update_history_ui vb. aynı kalıyor) ---
    def create_result_card(self, parent, word, score):
        card = ctk.CTkFrame(parent, fg_color="#1a1a1a", height=60, corner_radius=12)
        card.pack(fill="x", pady=5, padx=10)
        color = "#00ffcc" if score > 75000 else "#3498db" if score > 50000 else "#555"
        btn = ctk.CTkButton(card, text=word, font=("Consolas", 18, "bold"), anchor="w",
                            fg_color="transparent", hover_color="#252525",
                            command=lambda w=word: self.fetch_details(w))
        btn.pack(side="left", padx=20, fill="x", expand=True)
        ctk.CTkLabel(card, text="SCORE: " + str(score//1000), font=("Arial", 9), text_color=color).pack(side="right", padx=15)

    def update_history_ui(self):
        for widget in self.history_scroll.winfo_children(): widget.destroy()
        if not self.history_list:
            ctk.CTkLabel(self.history_scroll, text="No searches yet.", text_color="gray").pack(pady=20)
            return
        for word in self.history_list:
            h_card = ctk.CTkFrame(self.history_scroll, fg_color="#1a1a1a", height=50)
            h_card.pack(fill="x", pady=3, padx=10)
            ctk.CTkLabel(h_card, text=word, font=("Consolas", 16), text_color="white").pack(side="left", padx=20, pady=10)
            re_search = ctk.CTkButton(h_card, text="Search Again", width=100, height=25, fg_color="#333", command=lambda w=word: self.re_search(w))
            re_search.pack(side="right", padx=15)

    def re_search(self, word):
        self.entry.delete(0, 'end'); self.entry.insert(0, word)
        self.show_frame("search"); self.find_synonyms()

if __name__ == "__main__":
    app = SynoMasterPro()
    app.mainloop()
