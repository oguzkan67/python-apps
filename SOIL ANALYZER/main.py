#!/usr/bin/env python3
"""
PHOENIX SOIL ANALYZER - Professional Soil Analysis Application
Advanced desktop application with PDF export capability and comprehensive reporting.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
from typing import Dict, List, Optional
import os
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# PDF Export
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from recommendation_engine import CropRecommendationEngine


class PhoenixSoilAnalyzer:
    """Professional Soil Analysis Application - PHOENIX"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 PhoenixAnalyze - Profesyonel Toprak Analiz")
        self.root.geometry("1500x950")
        self.root.minsize(1300, 850)
        
        # Set application icon
        try:
            # Try multiple possible locations for the icon
            possible_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'phoenix_icon.png'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '_internal', 'phoenix_icon.png'),
                'phoenix_icon.png'
            ]
            
            icon_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    icon_path = path
                    break
            
            if icon_path:
                self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
        except Exception as e:
            print(f"Could not load icon: {e}")
            pass  # Icon not found, continue without it
        
        # Colors - Professional Blue Theme
        self.colors = {
            'primary': '#0d47a1',      # Deep Blue
            'secondary': '#1976d2',     # Medium Blue  
            'accent': '#42a5f5',       # Light Blue
            'highlight': '#00bcd4',    # Cyan
            'dark': '#0a1929',         # Dark Navy
            'card': '#ffffff',
            'bg': '#f0f4f8',
            'text': '#1a1a2e',
            'light_text': '#ffffff',
            'success': '#2e7d32',
            'warning': '#f57c00',
            'danger': '#c62828',
            'border': '#e0e0e0'
        }
        
        # Load data
        self.climate_data = self.load_climate_data()
        self.engine = CropRecommendationEngine("crop_database.json", "data_core.json")
        
        # Current data
        self.current_results = None
        
        # Build UI
        self.create_styles()
        self.create_header()
        self.create_main_layout()
        
    def load_climate_data(self) -> Dict:
        """Load climate data from JSON file."""
        try:
            with open('climate_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def create_styles(self):
        """Configure professional styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure notebook style
        style.configure('TNotebook', background=self.colors['bg'])
        style.configure('TNotebook.Tab', 
                      background=self.colors['card'],
                      foreground=self.colors['text'],
                      padding=[15, 8],
                      font=('Helvetica', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['primary'])],
                 foreground=[('selected', self.colors['light_text'])])
        
        # Treeview style
        style.configure('Treeview',
                       font=('Helvetica', 9),
                       rowheight=28)
        style.configure('Treeview.Heading',
                      font=('Helvetica', 10, 'bold'),
                      background=self.colors['primary'],
                      foreground=self.colors['light_text'])
    
    def create_header(self):
        """Create professional header with logo."""
        header = tk.Frame(self.root, bg=self.colors['dark'], height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Logo - Phoenix Bird (Text + Symbol)
        logo_frame = tk.Frame(header, bg=self.colors['dark'])
        logo_frame.pack(side=tk.LEFT, padx=30, pady=20)
        
        # Phoenix symbol using canvas
        canvas = tk.Canvas(logo_frame, width=60, height=60, bg=self.colors['dark'], highlightthickness=0)
        canvas.pack(side=tk.LEFT)
        
        # Draw Phoenix
        self.draw_phoenix(canvas)
        
        # Title
        title_frame = tk.Frame(header, bg=self.colors['dark'])
        title_frame.pack(side=tk.LEFT, padx=10)
        
        title = tk.Label(title_frame,
                        text="🔥 PhoenixAnalyze",
                        font=('Helvetica', 22, 'bold'),
                        bg=self.colors['dark'],
                        fg=self.colors['highlight'])
        title.pack(anchor='w')
        
        subtitle = tk.Label(title_frame,
                          text="Profesyonel Toprak Analiz ve Bitki Oneri Sistemi",
                          font=('Helvetica', 11),
                          bg=self.colors['dark'],
                          fg='#90caf9')
        subtitle.pack(anchor='w')
        
        # Right side info
        info_frame = tk.Frame(header, bg=self.colors['dark'])
        info_frame.pack(side=tk.RIGHT, padx=30)
        
        tk.Label(info_frame,
                text=f"📅 {datetime.now().strftime('%d.%m.%Y')}",
                font=('Helvetica', 10),
                bg=self.colors['dark'],
                fg='#90caf9').pack()
        
        tk.Label(info_frame,
                text=f"📊 Veritabani: 88000+ Kayit",
                font=('Helvetica', 9),
                bg=self.colors['dark'],
                fg='#64b5f6').pack()
    
    def draw_phoenix(self, canvas):
        """Draw a blue phoenix bird."""
        # Body
        canvas.create_oval(15, 25, 45, 50, fill=self.colors['highlight'], outline='')
        
        # Head
        canvas.create_oval(25, 10, 40, 22, fill=self.colors['secondary'], outline='')
        
        # Beak
        canvas.create_polygon(38, 15, 48, 16, 40, 20, fill='#ff9800', outline='')
        
        # Wing (flame-like)
        canvas.create_polygon(10, 20, 5, 5, 20, 15, fill=self.colors['primary'], outline='')
        canvas.create_polygon(50, 20, 55, 5, 40, 15, fill=self.colors['primary'], outline='')
        
        # Tail flames
        canvas.create_polygon(20, 50, 15, 58, 25, 55, fill=self.colors['accent'], outline='')
        canvas.create_polygon(30, 52, 30, 60, 35, 55, fill=self.colors['secondary'], outline='')
        canvas.create_polygon(40, 50, 45, 58, 35, 55, fill=self.colors['accent'], outline='')
    
    def create_main_layout(self):
        """Create main layout with sidebar and content."""
        main = tk.Frame(self.root, bg=self.colors['bg'])
        main.pack(fill=tk.BOTH, expand=True)
        
        # Left Sidebar
        self.create_sidebar(main)
        
        # Right Content Area
        self.create_content_area(main)
    
    def create_sidebar(self, parent):
        """Create sidebar with navigation."""
        sidebar = tk.Frame(parent, bg=self.colors['dark'], width=280)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # User info
        user_frame = tk.Frame(sidebar, bg=self.colors['dark'], pady=20)
        user_frame.pack(fill=tk.X)
        
        tk.Label(user_frame,
                text="🌱 Tarim Uzmani",
                font=('Helvetica', 14, 'bold'),
                bg=self.colors['dark'],
                fg=self.colors['highlight']).pack(pady=5)
        
        tk.Label(user_frame,
                text="Phoenix Sistemi",
                font=('Helvetica', 9),
                bg=self.colors['dark'],
                fg='#90caf9').pack()
        
        # Separator
        tk.Frame(sidebar, height=1, bg='#37474f').pack(fill=tk.X, padx=20, pady=15)
        
        # Navigation buttons
        nav_buttons = [
            ("🏠", "Ana Sayfa", self.show_home),
            ("📍", "Konum Secimi", self.show_location),
            ("🌱", "Toprak Analizi", self.show_soil),
            ("🌾", "Bitki Onerileri", self.show_crops),
            ("📊", "Grafikler", self.show_charts),
            ("📋", "Detayli Rapor", self.show_report),
            ("💾", "PDF Indir", self.export_pdf)
        ]
        
        for icon, text, command in nav_buttons:
            btn = tk.Button(sidebar,
                          text=f"  {icon}  {text}",
                          font=('Helvetica', 11),
                          bg='#1a237e',
                          fg=self.colors['light_text'],
                          activebackground=self.colors['primary'],
                          activeforeground=self.colors['light_text'],
                          bd=0,
                          padx=20,
                          pady=12,
                          cursor='hand2',
                          command=command,
                          anchor='w')
            btn.pack(fill=tk.X, padx=10, pady=2)
        
        # Database info
        info_frame = tk.Frame(sidebar, bg=self.colors['dark'], pady=20)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        tk.Label(info_frame,
                text="📊 Veritabani",
                font=('Helvetica', 10, 'bold'),
                bg=self.colors['dark'],
                fg=self.colors['highlight']).pack(pady=(0, 5))
        
        tk.Label(info_frame,
                text="• 88000+ Tarihsel Kayit",
                font=('Helvetica', 8),
                bg=self.colors['dark'],
                fg='#90caf9').pack(anchor='w', padx=20)
        
        tk.Label(info_frame,
                text="• 25+ Bitki Turu",
                font=('Helvetica', 8),
                bg=self.colors['dark'],
                fg='#90caf9').pack(anchor='w', padx=20)
        
        tk.Label(info_frame,
                text="• PDF Rapor Olusturma",
                font=('Helvetica', 8),
                bg=self.colors['dark'],
                fg='#90caf9').pack(anchor='w', padx=20)
    
    def create_content_area(self, parent):
        """Create content area with tabs."""
        content = tk.Frame(parent, bg=self.colors['bg'])
        content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input Section
        input_frame = tk.LabelFrame(content,
                                    text="📝 ANALIZ PARAMETRELERI",
                                    font=('Helvetica', 11, 'bold'),
                                    bg=self.colors['bg'],
                                    fg=self.colors['primary'],
                                    padx=15, pady=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_input_form(input_frame)
        
        # Results Section
        results_frame = tk.LabelFrame(content,
                                     text="📊 ANALIZ SONUCLARI",
                                     font=('Helvetica', 11, 'bold'),
                                     bg=self.colors['bg'],
                                     fg=self.colors['primary'],
                                     padx=10, pady=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tabs
        self.create_tabs()
        
        self.show_placeholder()
    
    def create_input_form(self, parent):
        """Create professional input form."""
        grid_frame = tk.Frame(parent, bg=self.colors['bg'])
        grid_frame.pack(fill=tk.X)
        
        # Row 1: Country & City
        row1 = tk.Frame(grid_frame, bg=self.colors['bg'])
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(row1, text="Ulke:", font=('Helvetica', 10, 'bold'),
                bg=self.colors['bg'], width=15, anchor='e').pack(side=tk.LEFT, padx=5)
        
        self.country_var = tk.StringVar()
        countries = list(self.climate_data.get('countries', {}).keys())
        country_combo = ttk.Combobox(row1, textvariable=self.country_var,
                                    values=countries, state='readonly',
                                    font=('Helvetica', 10), width=20)
        country_combo.pack(side=tk.LEFT, padx=5)
        country_combo.bind('<<ComboboxSelected>>', self.on_country_selected)
        
        tk.Label(row1, text="Sehir:", font=('Helvetica', 10, 'bold'),
                bg=self.colors['bg'], width=10, anchor='e').pack(side=tk.LEFT, padx=5)
        
        self.city_var = tk.StringVar()
        self.city_combo = ttk.Combobox(row1, textvariable=self.city_var,
                                       values=[], state='readonly',
                                       font=('Helvetica', 10), width=20)
        self.city_combo.pack(side=tk.LEFT, padx=5)
        
        # Row 2: pH & Temperature
        row2 = tk.Frame(grid_frame, bg=self.colors['bg'])
        row2.pack(fill=tk.X, pady=5)
        
        tk.Label(row2, text="pH Degeri:", font=('Helvetica', 10, 'bold'),
                bg=self.colors['bg'], width=15, anchor='e').pack(side=tk.LEFT, padx=5)
        
        self.ph_var = tk.DoubleVar(value=6.5)
        ttk.Spinbox(row2, from_=4.0, to=9.0, increment=0.1,
                    textvariable=self.ph_var, width=22,
                    font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Label(row2, text="Sicaklik (°C):", font=('Helvetica', 10, 'bold'),
                bg=self.colors['bg'], width=12, anchor='e').pack(side=tk.LEFT, padx=5)
        
        self.temp_var = tk.IntVar(value=22)
        ttk.Spinbox(row2, from_=0, to=50, increment=1,
                    textvariable=self.temp_var, width=18,
                    font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        
        # Row 3: NPK
        row3 = tk.Frame(grid_frame, bg=self.colors['bg'])
        row3.pack(fill=tk.X, pady=5)
        
        tk.Label(row3, text="Azot (N):", font=('Helvetica', 10, 'bold'),
                bg=self.colors['bg'], width=15, anchor='e').pack(side=tk.LEFT, padx=5)
        
        self.n_var = tk.StringVar(value="Orta")
        ttk.Combobox(row3, textvariable=self.n_var,
                     values=["Cok Dusuk", "Dusuk", "Orta", "Yuksek", "Cok Yuksek"],
                     state='readonly', width=18, font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Label(row3, text="Fosfor (P):", font=('Helvetica', 10, 'bold'),
                bg=self.colors['bg'], width=12, anchor='e').pack(side=tk.LEFT, padx=5)
        
        self.p_var = tk.StringVar(value="Orta")
        ttk.Combobox(row3, textvariable=self.p_var,
                     values=["Cok Dusuk", "Dusuk", "Orta", "Yuksek", "Cok Yuksek"],
                     state='readonly', width=18, font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Label(row3, text="Potasyum (K):", font=('Helvetica', 10, 'bold'),
                bg=self.colors['bg'], width=12, anchor='e').pack(side=tk.LEFT, padx=5)
        
        self.k_var = tk.StringVar(value="Orta")
        ttk.Combobox(row3, textvariable=self.k_var,
                     values=["Cok Dusuk", "Dusuk", "Orta", "Yuksek", "Cok Yuksek"],
                     state='readonly', width=18, font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        
        # Row 4: Soil Type & Moisture
        row4 = tk.Frame(grid_frame, bg=self.colors['bg'])
        row4.pack(fill=tk.X, pady=5)
        
        tk.Label(row4, text="Toprak Tipi:", font=('Helvetica', 10, 'bold'),
                bg=self.colors['bg'], width=15, anchor='e').pack(side=tk.LEFT, padx=5)
        
        self.soil_var = tk.StringVar(value="Tinli")
        ttk.Combobox(row4, textvariable=self.soil_var,
                     values=["Kumlu", "Tinli", "Killi", "Siyah", "Kirmizi", "Laterit"],
                     state='readonly', width=18, font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Label(row4, text="Toprak Nemi:", font=('Helvetica', 10, 'bold'),
                bg=self.colors['bg'], width=12, anchor='e').pack(side=tk.LEFT, padx=5)
        
        self.moisture_var = tk.StringVar(value="Orta")
        ttk.Combobox(row4, textvariable=self.moisture_var,
                     values=["Cok Kuru", "Kuru", "Orta", "Nemli", "Cok Nemli"],
                     state='readonly', width=18, font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        
        # Row 5: Rainfall & Buttons
        row5 = tk.Frame(grid_frame, bg=self.colors['bg'])
        row5.pack(fill=tk.X, pady=10)
        
        tk.Label(row5, text="Yagis (mm):", font=('Helvetica', 10, 'bold'),
                bg=self.colors['bg'], width=15, anchor='e').pack(side=tk.LEFT, padx=5)
        
        self.rain_var = tk.IntVar(value=800)
        ttk.Spinbox(row5, from_=0, to=4000, increment=50,
                    textvariable=self.rain_var, width=20,
                    font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        btn_frame = tk.Frame(row5, bg=self.colors['bg'])
        btn_frame.pack(side=tk.RIGHT, padx=10)
        
        analyze_btn = tk.Button(btn_frame,
                              text="🔥 ANALIZ ET",
                              font=('Helvetica', 11, 'bold'),
                              bg=self.colors['primary'],
                              fg=self.colors['light_text'],
                              padx=25, pady=8,
                              cursor='hand2',
                              command=self.analyze_soil)
        analyze_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(btn_frame,
                            text="🗑️ Temizle",
                            font=('Helvetica', 10),
                            bg='#616161',
                            fg=self.colors['light_text'],
                            padx=15, pady=8,
                            cursor='hand2',
                            command=self.clear_form)
        clear_btn.pack(side=tk.LEFT)
    
    def create_tabs(self):
        """Create result tabs."""
        # Tab 1: Overview
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="📊 Genel")
        self.overview_text = scrolledtext.ScrolledText(self.overview_frame, wrap=tk.WORD, font=('Consolas', 10))
        self.overview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 2: Crops Table
        self.crops_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.crops_frame, text="🌾 Bitkiler")
        
        # Treeview for crops
        cols = ('Sira', 'Bitki', 'Kategori', 'Uygunluk', 'pH', 'Sicaklik', 'Yagis')
        self.crops_tree = ttk.Treeview(self.crops_frame, columns=cols, show='headings', height=15)
        
        for col in cols:
            self.crops_tree.heading(col, text=col)
            self.crops_tree.column(col, width=100)
        
        self.crops_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 3: Data Insights
        self.insights_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.insights_frame, text="📈 Analiz")
        
        self.insights_text = scrolledtext.ScrolledText(self.insights_frame, wrap=tk.WORD, font=('Consolas', 10), height=10)
        self.insights_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 4: Similar Records
        self.records_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.records_frame, text="🔎 Kayitlar")
        
        self.records_text = scrolledtext.ScrolledText(self.records_frame, wrap=tk.WORD, font=('Consolas', 10))
        self.records_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 5: Charts
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="📉 Grafikler")
        
        self.figure = Figure(figsize=(10, 6), dpi=80)
        self.canvas = FigureCanvasTkAgg(self.figure, self.charts_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Tab 6: Detailed Recommendations
        self.recs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recs_frame, text="💡 Detayli Oneriler")
        
        self.recs_text = scrolledtext.ScrolledText(self.recs_frame, wrap=tk.WORD, font=('Consolas', 10))
        self.recs_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def on_country_selected(self, event):
        """Handle country selection."""
        country = self.country_var.get()
        if country and country in self.climate_data.get('countries', {}):
            cities = list(self.climate_data['countries'][country]['cities'].keys())
            self.city_combo['values'] = cities
            self.city_var.set('')
    
    def show_home(self):
        self.notebook.select(0)
    
    def show_location(self):
        self.notebook.select(0)
    
    def show_soil(self):
        self.notebook.select(0)
    
    def show_crops(self):
        self.notebook.select(1)
    
    def show_charts(self):
        self.notebook.select(4)
    
    def show_report(self):
        self.notebook.select(5)
    
    def show_placeholder(self):
        """Show placeholder."""
        placeholder = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           🔥 PHOENIX SOIL ANALYZER                         ║
║           Profesyonel Toprak Analiz Sistemi                   ║
║                                                               ║
║  Lutfen analiz parametrelerini girin ve 'ANALIZ ET'        ║
║  butonuna tikayin.                                         ║
║                                                               ║
║  Ozellikler:                                                ║
║  • 88000+ tarihsel kayit ile karsilastirma               ║
║  • Kapsamli toprak analizi (pH, NPK, nem, vs.)           ║
║  • PDF rapor olusturma ozelligi                           ║
║  • Detayli gubreleme ve sulama oneri                    ║
║  • Risk analizi ve ekim rotasyon planlari                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
        """
        
        for text_widget in [self.overview_text, self.insights_text, 
                          self.records_text, self.recs_text]:
            text_widget.delete(1.0, tk.END)
            text_widget.insert(1.0, placeholder)
    
    def analyze_soil(self):
        """Analyze soil."""
        try:
            soil_data = {
                'ph': self.ph_var.get(),
                'nitrogen': self.convert_turkish(self.n_var.get()),
                'phosphorus': self.convert_turkish(self.p_var.get()),
                'potassium': self.convert_turkish(self.k_var.get()),
                'soil_type': self.convert_soil_type(self.soil_var.get()),
                'moisture': self.convert_moisture(self.moisture_var.get()),
                'temperature': self.temp_var.get(),
                'rainfall': self.rain_var.get(),
                'country': self.country_var.get(),
                'city': self.city_var.get()
            }
            
            climate_info = {}
            country = self.country_var.get()
            city = self.city_var.get()
            if country and city:
                try:
                    climate_info = self.climate_data['countries'][country]['cities'][city]
                except:
                    pass
            
            self.current_results = self.engine.get_recommendations(soil_data)
            self.current_results['country'] = country
            self.current_results['city'] = city
            self.current_results['climate_info'] = climate_info
            
            self.display_results()
            
        except Exception as e:
            messagebox.showerror("Hata", str(e))
    
    def convert_turkish(self, val):
        """Convert Turkish values."""
        mapping = {
            "Cok Dusuk": "very_low", "Dusuk": "low", "Orta": "medium",
            "Yuksek": "high", "Cok Yuksek": "very_high"
        }
        return mapping.get(val, "medium")
    
    def convert_soil_type(self, val):
        """Convert soil type."""
        mapping = {
            "Kumlu": "Sandy", "Tinli": "Loamy", "Killi": "Clayey",
            "Siyah": "Black", "Kirmizi": "Red", "Laterit": "Laterite"
        }
        return mapping.get(val, "Loamy")
    
    def convert_moisture(self, val):
        """Convert moisture."""
        mapping = {
            "Cok Kuru": "very_low", "Kuru": "low", "Orta": "moderate",
            "Nemli": "high", "Cok Nemli": "very_high"
        }
        return mapping.get(val, "moderate")
    
    def display_results(self):
        """Display results with comprehensive details."""
        results = self.current_results
        
        # Overview
        self.overview_text.delete(1.0, tk.END)
        self.overview_text.insert(tk.END, self.format_overview(results))
        
        # Crops Table
        for item in self.crops_tree.get_children():
            self.crops_tree.delete(item)
        
        for i, rec in enumerate(results.get('primary_crops', []), 1):
            crop = rec['crop']
            self.crops_tree.insert('', tk.END, values=(
                i, crop['name'], crop.get('category', '-'),
                f"%{rec['score']:.1f}",
                f"{crop.get('ph_min', '-')}-{crop.get('ph_max', '-')}",
                f"{crop.get('temperature_min', '-')}-{crop.get('temperature_max', '-')}",
                f"{crop.get('rainfall_min', '-')}-{crop.get('rainfall_max', '-')}"
            ))
        
        # Insights - Enhanced with data from data_core
        self.insights_text.delete(1.0, tk.END)
        
        analysis = results.get('analysis', {})
        
        # pH Analysis
        ph_data = analysis.get('ph', {})
        self.insights_text.insert(tk.END, "📊 DETAYLI TOPRAK ANALIZI\n" + "="*50 + "\n\n")
        
        self.insights_text.insert(tk.END, f"🌡️ pH DEGERI: {ph_data.get('value', 'N/A')}\n")
        self.insights_text.insert(tk.END, f"   Durum: {ph_data.get('status', 'N/A')}\n")
        self.insights_text.insert(tk.END, f"   Oneri: {ph_data.get('advice', 'N/A')}\n")
        
        # Nutrients Analysis
        self.insights_text.insert(tk.END, "\n🧪 BESIN ANALIZI\n" + "-"*40 + "\n")
        nutrients = analysis.get('nutrients', {})
        for nutrient, data in nutrients.items():
            self.insights_text.insert(tk.END, f"   {nutrient.upper()}: {data.get('level', 'N/A')} - {data.get('action', 'N/A')}\n")
        
        # Data-driven insights
        self.insights_text.insert(tk.END, "\n📈 VERITABANI ANALIZI\n" + "-"*40 + "\n")
        
        data_insights = results.get('data_insights', {})
        crop_specific = data_insights.get('crop_specific', [])
        
        if crop_specific:
            for insight in crop_specific:
                self.insights_text.insert(tk.END, f"\n🌾 {insight.get('crop', 'N/A')}\n")
                self.insights_text.insert(tk.END, f"   Uygunluk: %{insight.get('score', 0):.1f}\n")
                
                optimal = insight.get('optimal_conditions', {})
                if 'temperature' in optimal:
                    t = optimal['temperature']
                    self.insights_text.insert(tk.END, f"   🌡️ Ideal Sicaklik: {t.get('ideal', 'N/A')}\n")
                if 'humidity' in optimal:
                    h = optimal['humidity']
                    self.insights_text.insert(tk.END, f"   💧 Ideal Nem: {h.get('ideal', 'N/A')}\n")
                if 'soil' in optimal:
                    self.insights_text.insert(tk.END, f"   🌍 Toprak: {optimal.get('soil', 'N/A')}\n")
                if 'fertilizer' in optimal:
                    self.insights_text.insert(tk.END, f"   💊 Onerilen Gubre: {optimal.get('fertilizer', 'N/A')}\n")
        
        # Similar Records
        self.records_text.delete(1.0, tk.END)
        self.records_text.insert(tk.END, "🔍 BENZER KAYITLAR (data_core.json)\n" + "="*50 + "\n\n")
        
        similar = results.get('similar_records', [])
        if similar:
            for i, rec in enumerate(similar[:10], 1):
                self.records_text.insert(tk.END, f"#{i} {rec['crop']}\n")
                self.records_text.insert(tk.END, f"   🌍 Toprak: {rec['soil_type']} | 💊 Gubre: {rec['fertilizer']}\n")
                self.records_text.insert(tk.END, f"   🌡️ Sicaklik: {rec['temperature']}°C | 💧 Nem: {rec['moisture']}%\n")
                self.records_text.insert(tk.END, f"   ⚗️ N: {rec['nitrogen']} | P: {rec['phosphorous']} | K: {rec['potassium']}\n")
                self.records_text.insert(tk.END, f"   Benzerlik Skoru: %{rec['score']:.1f}\n")
                self.records_text.insert(tk.END, "-"*40 + "\n")
        
        # Charts
        self.update_charts(results)
        
        # Detailed Recommendations
        self.recs_text.delete(1.0, tk.END)
        
        # Fertilizer Recommendations
        self.recs_text.insert(tk.END, "💊 DETAYLI GUBRELEME ONERILERI\n" + "="*50 + "\n\n")
        
        fert_recs = results.get('fertilizer_recommendations', {})
        
        immediate = fert_recs.get('immediate', [])
        if immediate:
            self.recs_text.insert(tk.END, "⏰ ANINDA UYGULANMALI\n")
            for rec in immediate:
                self.recs_text.insert(tk.END, f"\n  ▸ {rec.get('type', 'N/A')}\n")
                self.recs_text.insert(tk.END, f"    Urun: {rec.get('product', 'N/A')}\n")
                self.recs_text.insert(tk.END, f"    Doz: {rec.get('dose', 'N/A')}\n")
                self.recs_text.insert(tk.END, f"    Zaman: {rec.get('timing', 'N/A')}\n")
                self.recs_text.insert(tk.END, f"    Yontem: {rec.get('method', 'N/A')}\n")
        
        mineral = fert_recs.get('mineral', [])
        if mineral:
            self.recs_text.insert(tk.END, "\n\n💎 MINERAL GUBRELER\n")
            for m in mineral:
                self.recs_text.insert(tk.END, f"  • {m}\n")
        
        organic = fert_recs.get('organic', [])
        if organic:
            self.recs_text.insert(tk.END, "\n\n🌿 ORGANIK GUBRELER\n")
            for o in organic:
                self.recs_text.insert(tk.END, f"  • {o}\n")
        
        micro = fert_recs.get('micronutrients', [])
        if micro:
            self.recs_text.insert(tk.END, "\n\n🔬 MIKRO BESINLER\n")
            for m in micro:
                self.recs_text.insert(tk.END, f"  ▸ {m.get('element')}: {m.get('deficiency')}\n")
                self.recs_text.insert(tk.END, f"    Urun: {m.get('product')} | Doz: {m.get('dose')}\n")
        
        # Irrigation
        self.recs_text.insert(tk.END, "\n\n" + "="*50)
        self.recs_text.insert(tk.END, "\n💧 DETAYLI SULAMA ONERILERI\n" + "="*50 + "\n\n")
        
        irr = results.get('irrigation_recommendations', {})
        self.recs_text.insert(tk.END, f"🏗️ YONTEM: {irr.get('method', 'N/A')}\n\n")
        self.recs_text.insert(tk.END, f"⚠️ ONCELIK: {irr.get('priority', 'N/A')}\n\n")
        self.recs_text.insert(tk.END, f"📅 SIKLIK: {irr.get('frequency', 'N/A')}\n\n")
        
        if 'water_saving' in irr:
            self.recs_text.insert(tk.END, f"💦 Tasarruf: {irr.get('water_saving')}\n\n")
        
        if 'heat_management' in irr:
            self.recs_text.insert(tk.END, f"☀️ Isi Yonetimi: {irr.get('heat_management')}\n\n")
        
        critical = irr.get('critical_stages', [])
        if critical:
            self.recs_text.insert(tk.END, "🎯 KRITIK DONEMLER:\n")
            for stage in critical:
                self.recs_text.insert(tk.END, f"  • {stage}\n")
        
        # Risk Analysis
        risks = results.get('risk_analysis', {})
        
        self.recs_text.insert(tk.END, "\n\n" + "="*50)
        self.recs_text.insert(tk.END, "\n⚠️ RISK ANALIZI\n" + "="*50 + "\n\n")
        
        env_risks = risks.get('environmental', [])
        if env_risks:
            self.recs_text.insert(tk.END, "🌍 CEVRESEL RISKLER:\n")
            for r in env_risks:
                self.recs_text.insert(tk.END, f"  ▸ {r.get('type')}: {r.get('severity')}\n")
                self.recs_text.insert(tk.END, f"    Cozum: {r.get('mitigation')}\n")
        
        agr_risks = risks.get('agronomic', [])
        if agr_risks:
            self.recs_text.insert(tk.END, "\n🌾 AGRONOMIK RISKLER:\n")
            for r in agr_risks:
                self.recs_text.insert(tk.END, f"  ▸ {r.get('type')}: {r.get('severity')}\n")
                self.recs_text.insert(tk.END, f"    Cozum: {r.get('mitigation')}\n")
        
        # Crop Rotation
        rotation = results.get('crop_rotation_plan', {})
        if rotation and 'current_season' in rotation:
            self.recs_text.insert(tk.END, "\n\n" + "="*50)
            self.recs_text.insert(tk.END, "\n🔄 EKIM ROTASYON PLANI\n" + "="*50 + "\n\n")
            self.recs_text.insert(tk.END, f"📌 Mevcut: {rotation.get('current_season', 'N/A')}\n\n")
            
            next_crops = rotation.get('next_season_crops', [])
            if next_crops:
                self.recs_text.insert(tk.END, "➡️ SONRAKI SEZON:\n")
                for nc in next_crops:
                    self.recs_text.insert(tk.END, f"  • {nc.get('crop')}: {nc.get('reason')}\n")
        
        # Yield Estimates
        yields = results.get('yield_estimates', {})
        if yields:
            self.recs_text.insert(tk.END, "\n\n" + "="*50)
            self.recs_text.insert(tk.END, "\n📈 TAHMINI VERIMLER\n" + "="*50 + "\n\n")
            for crop_name, data in yields.items():
                self.recs_text.insert(tk.END, f"🌾 {crop_name}\n")
                self.recs_text.insert(tk.END, f"   Verim: {data.get('estimated_yield', 'N/A')}\n")
                self.recs_text.insert(tk.END, f"   Uygunluk: {data.get('suitability_score', 'N/A')}\n")
                self.recs_text.insert(tk.END, f"   Guven: {data.get('confidence', 'N/A')}\n\n")
        
        messagebox.showinfo("Basarili", f"Analiz tamamlandi!\n{len(results['primary_crops'])} bitki onERISI bulundu.")
    
    def format_overview(self, results):
        """Format overview text."""
        soil = results['soil_data']
        
        text = f"""
╔═══════════════════════════════════════════════════════════════╗
║                 🔥 ANALIZ SONUCLARI                         ║
╚═══════════════════════════════════════════════════════════════╝

📍 KONUM BİLGİSİ
{'─'*50}
"""
        if results.get('country'):
            climate = results.get('climate_info', {})
            text += f"Ulke: {results['country']}\n"
            text += f"Sehir: {results.get('city', 'N/A')}\n"
            if climate:
                text += f"Bolge: {climate.get('region_type', 'N/A')}\n"
                text += f"Sicaklik: {climate.get('temperature', 'N/A')}°C\n"
                text += f"Nem: {climate.get('humidity', 'N/A')}%\n"
        
        text += f"""
🌱 TOPRAK PARAMETRELERI
{'─'*50}
pH Degeri:      {soil['ph']}
Azot (N):        {soil['nitrogen'].title()}
Fosfor (P):     {soil['phosphorus'].title()}
Potasyum (K):    {soil['potassium'].title()}
Sicaklik:       {soil['temperature']}°C
Yagis:          {soil['rainfall']} mm

🌟 ONERILEN BITKILER
{'─'*50}
"""
        
        for i, rec in enumerate(results.get('primary_crops', [])[:5], 1):
            text += f"{i}. {rec['crop']['name']} - %{rec['score']:.1f}\n"
        
        return text
    
    def update_charts(self, results):
        """Update charts."""
        soil = results['soil_data']
        
        self.figure.clear()
        
        # NPK Chart
        ax1 = self.figure.add_subplot(221)
        npk_values = {
            'N': self.get_npk_val(soil.get('nitrogen', 'medium')),
            'P': self.get_npk_val(soil.get('phosphorus', 'medium')),
            'K': self.get_npk_val(soil.get('potassium', 'medium'))
        }
        colors = ['#2196f3', '#4caf50', '#ff9800']
        bars = ax1.bar(npk_values.keys(), npk_values.values(), color=colors)
        ax1.set_ylim(0, 100)
        ax1.set_title('NPK Dagilimi', fontweight='bold')
        ax1.set_ylabel('Seviye (%)')
        
        # Crop suitability
        ax2 = self.figure.add_subplot(222)
        crops = results.get('primary_crops', [])[:4]
        if crops:
            names = [c['crop']['name'][:8] for c in crops]
            scores = [c['score'] for c in crops]
            ax2.barh(names, scores, color='#0d47a1')
            ax2.set_xlim(0, 100)
            ax2.set_title('Bitki Uygunluk', fontweight='bold')
        
        # pH indicator
        ax3 = self.figure.add_subplot(223)
        ph = soil['ph']
        colors_ph = ['#c62828' if ph < 5.5 else '#f57c00' if ph < 6.0 else '#2e7d32' if ph < 7.5 else '#f57c00' if ph < 8.0 else '#c62828']
        ax3.bar(['pH'], [ph], color=colors_ph)
        ax3.set_ylim(0, 14)
        ax3.axhline(y=7, color='gray', linestyle='--', alpha=0.5)
        ax3.set_title(f'Toprak pH: {ph}', fontweight='bold')
        
        # Temperature vs Rainfall
        ax4 = self.figure.add_subplot(224)
        ax4.scatter([soil['temperature']], [soil['rainfall']/10], s=200, c='#00bcd4', alpha=0.7)
        ax4.set_xlabel('Sicaklik (°C)')
        ax4.set_ylabel('Yagis (mm/10)')
        ax4.set_title('Sicaklik-Yagis', fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def get_npk_val(self, level):
        """Get NPK value."""
        mapping = {'very_low': 20, 'low': 40, 'medium': 60, 'high': 80, 'very_high': 95}
        return mapping.get(level, 50)
    
    def export_pdf(self):
        """Export comprehensive PDF report with Phoenix branding."""
        if not self.current_results:
            messagebox.showwarning("Uyari", "Once analiz yapiniz!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"PHOENIX_Rapor_{datetime.now().strftime('%Y%m%d')}"
        )
        
        if file_path:
            try:
                self.create_pdf_report(file_path)
                messagebox.showinfo("Basarili", f"PDF rapor kaydedildi:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
    
    def create_pdf_report(self, file_path):
        """Create comprehensive PDF report with Phoenix branding."""
        results = self.current_results
        soil = results['soil_data']
        
        # Create PDF - wider margins for better spacing
        doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=12*mm, leftMargin=12*mm, topMargin=12*mm, bottomMargin=12*mm)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#0d47a1'), alignment=TA_CENTER, spaceAfter=12)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#0d47a1'), spaceBefore=10, spaceAfter=6)
        subheading_style = ParagraphStyle('CustomSubheading', parent=styles['Heading3'], fontSize=9, textColor=colors.HexColor('#1976d2'), spaceBefore=6, spaceAfter=3)
        normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=8, spaceAfter=3, wordWrap='CJK')
        small_style = ParagraphStyle('CustomSmall', parent=styles['Normal'], fontSize=7, spaceAfter=2, wordWrap='CJK')
        
        # =============================================
        # TITLE SECTION
        # =============================================
        story.append(Paragraph("🔥 PHOENIX SOIL ANALYZER", title_style))
        story.append(Paragraph("Profesyonel Toprak Analiz ve Bitki Oneri Raporu", ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, textColor=colors.grey, alignment=TA_CENTER)))
        story.append(Spacer(1, 12))
        
        # Date & Location
        location_info = f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        if results.get('country'):
            location_info += f" | Ulke: {results['country']}"
            if results.get('city'):
                location_info += f" - {results['city']}"
        story.append(Paragraph(location_info, normal_style))
        story.append(Spacer(1, 8))
        
        # =============================================
        # SOIL PARAMETERS
        # =============================================
        story.append(Paragraph("🌱 TOPRAK ANALIZ PARAMETRELERI", heading_style))
        
        # Detailed soil data - wider columns
        soil_data = [
            ['Parametre', 'Deger', 'Durum'],
            ['pH Degeri', str(soil['ph']), self.get_ph_status(soil['ph'])],
            ['Azot (N)', soil['nitrogen'].title(), self.get_npk_status(soil['nitrogen'])],
            ['Fosfor (P)', soil['phosphorus'].title(), self.get_npk_status(soil['phosphorus'])],
            ['Potasyum (K)', soil['potassium'].title(), self.get_npk_status(soil['potassium'])],
            ['Sicaklik', f"{soil['temperature']}°C", self.get_temp_status(soil['temperature'])],
            ['Yagis', f"{soil['rainfall']} mm", self.get_rain_status(soil['rainfall'])],
        ]
        
        # Calculate page width minus margins
        page_width = 190  # A4 width in mm minus margins
        col_widths = [page_width * 0.30, page_width * 0.25, page_width * 0.45]
        
        t = Table(soil_data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d47a1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.lightgrey]),
            ('TEXTTOPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t)
        story.append(Spacer(1, 10))
        
        # =============================================
        # pH ANALYSIS
        # =============================================
        analysis = results.get('analysis', {})
        ph_data = analysis.get('ph', {})
        
        story.append(Paragraph("🌡️ pH ANALIZI VE ONERILER", heading_style))
        
        ph_content = [
            ['Analiz', 'Sonuc'],
            ['pH Degeri', str(ph_data.get('value', soil['ph']))],
            ['Durum', ph_data.get('status', 'Normal')],
            ['Oneri', ph_data.get('advice', 'pH dengeli')],
        ]
        
        t_ph = Table(ph_content, colWidths=[page_width * 0.35, page_width * 0.65])
        t_ph.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f57c00')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fff3e0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.orange),
            ('TEXTTOPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t_ph)
        story.append(Spacer(1, 10))
        
        # =============================================
        # NUTRIENT ANALYSIS
        # =============================================
        story.append(Paragraph("🧪 BESIN ANALIZI", heading_style))
        
        nutrients = analysis.get('nutrients', {})
        nutrient_data = [['Besin', 'Seviye', 'Aksiyon']]
        
        for nutrient, data in nutrients.items():
            nutrient_data.append([
                nutrient.upper(),
                data.get('level', '-'),
                data.get('action', '-')
            ])
        
        if len(nutrient_data) > 1:
            t_nut = Table(nutrient_data, colWidths=[page_width * 0.25, page_width * 0.25, page_width * 0.50])
            t_nut.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#388e3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e8f5e9')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('TEXTTOPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(t_nut)
            story.append(Spacer(1, 10))
        
        # =============================================
        # CROP RECOMMENDATIONS
        # =============================================
        story.append(Paragraph("🌾 ONERILEN BITKILER", heading_style))
        
        crop_data = [['Sira', 'Bitki', 'Kategori', 'Uygunluk', 'pH Araligi']]
        for i, rec in enumerate(results.get('primary_crops', [])[:8], 1):
            crop = rec['crop']
            ph_range = f"{crop.get('ph_min', '-')}-{crop.get('ph_max', '-')}"
            crop_data.append([str(i), crop['name'], crop.get('category', '-'), f"%{rec['score']:.1f}", ph_range])
        
        t2 = Table(crop_data, colWidths=[page_width * 0.08, page_width * 0.32, page_width * 0.25, page_width * 0.15, page_width * 0.20])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('TEXTTOPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(t2)
        story.append(Spacer(1, 10))
        
        # =============================================
        # FERTILIZER RECOMMENDATIONS - DETAILED
        # =============================================
        story.append(Paragraph("💊 DETAYLI GUBRELEME ONERILERI", heading_style))
        
        fert_recs = results.get('fertilizer_recommendations', {})
        
        # Immediate actions
        immediate = fert_recs.get('immediate', [])
        if immediate:
            story.append(Paragraph("⏰ ANINDA UYGULANMASI GEREKEN", subheading_style))
            for rec in immediate:
                story.append(Paragraph(f"▸ <b>{rec.get('type', 'N/A')}</b>: {rec.get('product', 'N/A')}", normal_style))
                story.append(Paragraph(f"   Doz: {rec.get('dose', 'N/A')} | Zaman: {rec.get('timing', 'N/A')}", small_style))
                if rec.get('method'):
                    story.append(Paragraph(f"   Yontem: {rec.get('method', 'N/A')}", small_style))
            story.append(Spacer(1, 8))
        
        # Mineral fertilizers
        mineral = fert_recs.get('mineral', [])
        if mineral:
            story.append(Paragraph("💎 MINERAL GUBRELER", subheading_style))
            for m in mineral:
                story.append(Paragraph(f"  • {m}", normal_style))
            story.append(Spacer(1, 6))
        
        # Organic fertilizers
        organic = fert_recs.get('organic', [])
        if organic:
            story.append(Paragraph("🌿 ORGANIK GUBRELER", subheading_style))
            for o in organic:
                story.append(Paragraph(f"  • {o}", normal_style))
            story.append(Spacer(1, 6))
        
        # Micronutrients
        micro = fert_recs.get('micronutrients', [])
        if micro:
            story.append(Paragraph("🔬 MIKRO BESIN ELEMENTLERI", subheading_style))
            for m in micro:
                story.append(Paragraph(f"▸ <b>{m.get('element', 'N/A')}</b> - Eksiklik: {m.get('deficiency', 'N/A')}", normal_style))
                story.append(Paragraph(f"   Urun: {m.get('product', 'N/A')} | Doz: {m.get('dose', 'N/A')}", small_style))
        
        story.append(Spacer(1, 12))
        
        # =============================================
        # IRRIGATION RECOMMENDATIONS - DETAILED
        # =============================================
        story.append(Paragraph("💧 DETAYLI SULAMA ONERILERI", heading_style))
        
        irr = results.get('irrigation_recommendations', {})
        
        irr_data = [
            ['Parametre', 'Deger'],
            ['Sulama Yontemi', irr.get('method', 'N/A')],
            ['Oncelik', irr.get('priority', 'N/A')],
            ['Sulama Sikligi', irr.get('frequency', 'N/A')],
        ]
        
        if 'water_saving' in irr:
            irr_data.append(['Su Tasarrufu', irr.get('water_saving', 'N/A')])
        
        if 'heat_management' in irr:
            irr_data.append(['Isi Yonetimi', irr.get('heat_management', 'N/A')])
        
        t_irr = Table(irr_data, colWidths=[60, 140])
        t_irr.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0288d1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e1f5fe')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightblue),
        ]))
        story.append(t_irr)
        
        # Critical stages
        critical = irr.get('critical_stages', [])
        if critical:
            story.append(Paragraph("🎯 KRITIK SULAMA DONEMLERI:", normal_style))
            critical_text = " | ".join(critical)
            story.append(Paragraph(f"   {critical_text}", small_style))
        
        story.append(Spacer(1, 12))
        
        # =============================================
        # RISK ANALYSIS
        # =============================================
        story.append(Paragraph("⚠️ RISK ANALIZI VE ONERILER", heading_style))
        
        risks = results.get('risk_analysis', {})
        
        # Environmental risks
        env_risks = risks.get('environmental', [])
        if env_risks:
            story.append(Paragraph("🌍 CEVRESEL RISKLER:", subheading_style))
            for r in env_risks:
                story.append(Paragraph(f"▸ <b>{r.get('type', 'N/A')}</b> - Siddet: {r.get('severity', 'N/A')}", normal_style))
                story.append(Paragraph(f"   📌 Cozum: {r.get('mitigation', 'N/A')}", small_style))
        
        # Agronomic risks
        agr_risks = risks.get('agronomic', [])
        if agr_risks:
            story.append(Paragraph("🌾 AGRONOMIK RISKLER:", subheading_style))
            for r in agr_risks:
                story.append(Paragraph(f"▸ <b>{r.get('type', 'N/A')}</b> - Siddet: {r.get('severity', 'N/A')}", normal_style))
                if r.get('mitigation'):
                    story.append(Paragraph(f"   📌 Cozum: {r.get('mitigation', 'N/A')}", small_style))
        
        story.append(Spacer(1, 12))
        
        # =============================================
        # CROP ROTATION PLAN
        # =============================================
        rotation = results.get('crop_rotation_plan', {})
        if rotation and 'current_season' in rotation:
            story.append(Paragraph("🔄 EKIM ROTASYON PLANI", heading_style))
            
            rot_data = [
                ['Donem', 'Bilgi'],
                ['Mevcut Sezon', rotation.get('current_season', 'N/A')],
            ]
            
            if 'next_season_crops' in rotation:
                next_crops = rotation.get('next_season_crops', [])
                if next_crops:
                    rot_data.append(['Sonraki Sezon Icin Oneriler', ''])
                    for nc in next_crops:
                        rot_data.append([f"  • {nc.get('crop', 'N/A')}", nc.get('reason', 'N/A')])
            
            t_rot = Table(rot_data, colWidths=[60, 140])
            t_rot.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7b1fa2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3e5f5')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.purple),
            ]))
            story.append(t_rot)
            story.append(Spacer(1, 12))
        
        # =============================================
        # YIELD ESTIMATES
        # =============================================
        yields = results.get('yield_estimates', {})
        if yields:
            story.append(Paragraph("📈 TAHMINI VERIMLER", heading_style))
            
            yield_data = [['Bitki', 'Verim', 'Uygunluk', 'Guven']]
            for crop_name, data in yields.items():
                yield_data.append([
                    crop_name,
                    data.get('estimated_yield', 'N/A'),
                    data.get('suitability_score', 'N/A'),
                    data.get('confidence', 'N/A')
                ])
            
            t_yield = Table(yield_data, colWidths=[60, 60, 50, 40])
            t_yield.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f57c00')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fff3e0')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.orange),
            ]))
            story.append(t_yield)
            story.append(Spacer(1, 12))
        
        # =============================================
        # SIMILAR RECORDS
        # =============================================
        similar = results.get('similar_records', [])
        if similar:
            story.append(Paragraph("🔍 BENZER KAYITLAR (Veritabani Eslesmeleri)", heading_style))
            
            for i, rec in enumerate(similar[:5], 1):
                story.append(Paragraph(f"<b>#{i} {rec['crop']}</b>", normal_style))
                story.append(Paragraph(f"   Toprak: {rec.get('soil_type', 'N/A')} | Gubre: {rec.get('fertilizer', 'N/A')}", small_style))
                story.append(Paragraph(f"   Sicaklik: {rec.get('temperature', 'N/A')}°C | Nem: {rec.get('moisture', 'N/A')}%", small_style))
                story.append(Paragraph(f"   Benzerlik: %{rec.get('score', 0):.1f}", small_style))
                story.append(Spacer(1, 4))
        
        # =============================================
        # FOOTER
        # =============================================
        story.append(Spacer(1, 20))
        story.append(Paragraph("─" * 60, ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, textColor=colors.grey)))
        story.append(Paragraph("🔥 PHOENIX SOIL ANALYZER - Profesyonel Tarim Çözümleri", ParagraphStyle('Footer2', parent=styles['Normal'], alignment=TA_CENTER, textColor=colors.grey, fontSize=9)))
        story.append(Paragraph("Bu rapor otomatik olarak olusturulmustur. | Tüm veriler referans amaçlıdır.", ParagraphStyle('Footer3', parent=styles['Normal'], alignment=TA_CENTER, textColor=colors.lightgrey, fontSize=7)))
        
        # Build PDF
        doc.build(story)
    
    def get_ph_status(self, ph):
        """Get pH status text."""
        if ph < 5.5:
            return "Asidik"
        elif ph < 6.0:
            return "Hafif Asidik"
        elif ph < 7.5:
            return "Ideal"
        elif ph < 8.0:
            return "Hafif Alkalin"
        else:
            return "Alkalin"
    
    def get_npk_status(self, level):
        """Get NPK status text."""
        status_map = {
            'very_low': 'Cok Dusuk',
            'low': 'Dusuk',
            'medium': 'Orta',
            'high': 'Yuksek',
            'very_high': 'Cok Yuksek'
        }
        return status_map.get(level, '-')
    
    def get_temp_status(self, temp):
        """Get temperature status."""
        if temp < 10:
            return "Cok Dusuk"
        elif temp < 15:
            return "Dusuk"
        elif temp < 25:
            return "Ideal"
        elif temp < 35:
            return "Yuksek"
        else:
            return "Cok Yuksek"
    
    def get_rain_status(self, rain):
        """Get rainfall status."""
        if rain < 300:
            return "Cok Kuru"
        elif rain < 600:
            return "Kuru"
        elif rain < 1200:
            return "Ideal"
        else:
            return "Yogun"
    
    def export_report(self):
        """Export text report (legacy)."""
        self.export_pdf()
    
    def clear_form(self):
        """Clear form."""
        self.country_var.set('')
        self.city_var.set('')
        self.city_combo['values'] = []
        self.ph_var.set(6.5)
        self.n_var.set("Orta")
        self.p_var.set("Orta")
        self.k_var.set("Orta")
        self.soil_var.set("Tinli")
        self.moisture_var.set("Orta")
        self.temp_var.set(22)
        self.rain_var.set(800)
        
        self.show_placeholder()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = PhoenixSoilAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()

