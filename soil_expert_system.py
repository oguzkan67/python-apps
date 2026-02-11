import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox

# Global Styles
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SoilExpertSystem(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Agri-Science Decision Support System v5.0")
        self.geometry("850x950")
        
        # --- Header ---
        self.header = ctk.CTkLabel(self, text="SOIL ANALYSIS & AGRONOMIC REPORTING", 
                                   font=("Georgia", 26, "bold"), text_color="#5dade2")
        self.header.pack(pady=25)

        # Main Scrollable Area
        self.main_container = ctk.CTkScrollableFrame(self, width=800, height=800)
        self.main_container.pack(padx=20, pady=10, fill="both", expand=True)

        # --- SECTION 1: PHYSICAL PROPERTIES ---
        self.create_section_title("I. Edaphic & Historical Factors")
        
        self.soil_type = self.create_dropdown("Soil Texture Profile:", 
                                              ["Sandy (Coarse)", "Loamy (Optimal)", "Clay (Heavy/Fine)"])
        
        self.crop_history = self.create_dropdown("Previous Crop Cycle:", 
                                                 ["Legumes (Nitrogen Fixing)", "Cereals", "Root Crops", "Fallow"])

        # --- SECTION 2: CHEMICAL PARAMETERS ---
        self.create_section_title("II. Chemical & Nutrient Composition")
        
        # Inputs organized in a grid for a cleaner look
        self.grid_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.grid_frame.pack(pady=10)

        self.ph_val = self.create_grid_input("Soil pH Level:", "6.5", 0, 0)
        self.om_val = self.create_grid_input("Organic Matter (%):", "3.0", 0, 1)
        self.n_val = self.create_grid_input("Nitrogen (N) ppm:", "40", 1, 0)
        self.p_val = self.create_grid_input("Phosphorus (P) ppm:", "15", 1, 1)
        self.k_val = self.create_grid_input("Potassium (K) ppm:", "200", 2, 0)

        # --- SECTION 3: ENVIRONMENTAL CONDITIONS ---
        self.create_section_title("III. Hydrological Factors")
        self.drainage_var = ctk.BooleanVar(value=False)
        self.drain_check = ctk.CTkCheckBox(self.main_container, text="Evidence of Waterlogging/Poor Drainage", 
                                           variable=self.drainage_var, font=("Arial", 13))
        self.drain_check.pack(pady=10)

        # --- ACTION BUTTONS ---
        self.btn_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.btn_container.pack(pady=30)

        self.run_btn = ctk.CTkButton(self.btn_container, text="GENERATE ACADEMIC REPORT", 
                                     command=self.perform_analysis, fg_color="#27ae60", 
                                     hover_color="#1e8449", width=300, height=45, font=("Arial", 14, "bold"))
        self.run_btn.grid(row=0, column=0, padx=10)

        # --- OUTPUT CONSOLE ---
        self.report_output = ctk.CTkTextbox(self.main_container, width=700, height=450, 
                                            font=("Times New Roman", 15), border_width=2)
        self.report_output.pack(pady=20, padx=10)

    # --- HELPER UI METHODS ---
    def create_section_title(self, text):
        lbl = ctk.CTkLabel(self.main_container, text=text, font=("Arial", 16, "italic"), text_color="#f39c12")
        lbl.pack(pady=(25, 10), anchor="w", padx=40)

    def create_dropdown(self, label, options):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.pack(pady=5, fill="x", padx=60)
        ctk.CTkLabel(frame, text=label, width=200, anchor="w").pack(side="left")
        var = ctk.StringVar(value=options[1])
        menu = ctk.CTkOptionMenu(frame, values=options, variable=var, width=200)
        menu.pack(side="right")
        return var

    def create_grid_input(self, label, placeholder, r, c):
        lbl = ctk.CTkLabel(self.grid_frame, text=label)
        lbl.grid(row=r*2, column=c, padx=20, pady=(10, 0), sticky="w")
        entry = ctk.CTkEntry(self.grid_frame, placeholder_text=placeholder, width=140)
        entry.grid(row=r*2+1, column=c, padx=20, pady=(0, 10))
        return entry

    # --- CORE LOGIC ---
    def perform_analysis(self):
        try:
            # Parsing inputs
            data = {
                "ph": float(self.ph_val.get()),
                "om": float(self.om_val.get()),
                "n": float(self.n_val.get()),
                "p": float(self.p_val.get()),
                "k": float(self.k_val.get()),
                "texture": self.soil_type.get(),
                "history": self.crop_history.get()
            }

            report = f"EDAPHIC EVALUATION REPORT\n"
            report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            report += "="*45 + "\n\n"

            # 1. Physicochemical Diagnosis
            report += "[1. Physicochemical Profile]\n"
            if data['ph'] < 5.5:
                report += "- Critical Acidity: High risk of Aluminum toxicity. Liming is mandatory.\n"
            elif 6.0 <= data['ph'] <= 7.2:
                report += "- Optimal pH: Nutrient bioavailability is at peak efficiency.\n"
            else:
                report += "- Alkaline Profile: Potential micronutrient lock-out (Fe, Zn).\n"

            # 2. Nutrient Inventory
            report += "\n[2. Nutrient Status & Bioavailability]\n"
            if data['history'] == "Legumes (Nitrogen Fixing)":
                report += "- Note: Pre-existing Nitrogen nodules detected via crop history.\n"
            
            if data['om'] < 2.5:
                report += "- Warning: Soil Organic Matter (SOM) is deficient. Microbial activity is low.\n"
            
            # 3. Structural Analysis
            report += "\n[3. Soil Structure & Hydrology]\n"
            if "Sandy" in data['texture']:
                report += "- High Leaching Risk: Frequent, low-volume irrigation advised.\n"
            elif "Clay" in data['texture']:
                report += "- Compaction Warning: Poor aeration potential. Avoid heavy machinery when wet.\n"

            if self.drainage_var.get():
                report += "- ALERT: Anaerobic conditions likely due to poor drainage.\n"

            # Final Summary
            report += "\n" + "="*45 + "\n"
            report += "AGRONOMIC RECOMMENDATION:\n"
            report += "Integrate organic amendments to stabilize structure. Monitor CEC levels."

            self.report_output.delete("0.0", "end")
            self.report_output.insert("0.0", report)

        except ValueError:
            messagebox.showerror("Data Error", "Please ensure all chemical parameters are numeric.")

if __name__ == "__main__":
    app = SoilExpertSystem()
    app.mainloop()

#made by oguzkan berkay yakici
