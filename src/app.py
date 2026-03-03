import os
import joblib
import requests
import customtkinter as ctk
from tkinter import messagebox
from dotenv import load_dotenv
from utils import clean_text


class FakeNewsDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fake News Detection System")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)

        # Appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv("NEWS_API_KEY")

        # Paths
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_PATH = os.path.join(BASE_DIR, "../models/model.pkl")
        VECTORIZER_PATH = os.path.join(BASE_DIR, "../models/vectorizer.pkl")

        # Load Model
        try:
            self.model = joblib.load(MODEL_PATH)
            self.vectorizer = joblib.load(VECTORIZER_PATH)
            self.model_loaded = True
        except Exception as e:
            self.model_loaded = False
            messagebox.showerror("Model Load Error", f"Failed to load model:\n{str(e)}")
            self.root.destroy()
            return

        self.is_analyzing = False

        # Enhanced color palette
        self.colors = {
            "bg_primary": "#0f0f1a",       # Deeper background
            "bg_secondary": "#1a1a2e",     # Card background
            "bg_card": "#16213e",          # Lighter card
            "accent_primary": "#e94560",   # Coral accent
            "accent_secondary": "#00d9ff", # Cyan accent
            "accent_success": "#00d9ff",   # Success cyan
            "accent_danger": "#e94560",    # Danger red
            "accent_warning": "#f39c12",   # Warning orange
            "text_primary": "#ffffff",
            "text_secondary": "#a0a0a0",
            "text_muted": "#6c757d",
            "border": "#2d3748"
        }

        self.root.configure(fg_color=self.colors["bg_primary"])
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Animation variables
        self.animation_speed = 0.02
        
        self._create_header()
        self._create_main_content()
        self._create_status_bar()

    # ==========================
    # UI CREATION
    # ==========================

    def _create_header(self):
        """Create modern header with gradient effect"""
        header = ctk.CTkFrame(
            self.root, 
            fg_color=self.colors["bg_secondary"], 
            height=90,
            corner_radius=0
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        # Logo/Icon area
        icon_frame = ctk.CTkFrame(
            header, 
            fg_color=self.colors["accent_primary"], 
            width=50, 
            height=50,
            corner_radius=12
        )
        icon_frame.place(x=30, rely=0.5, anchor="w")
        icon_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            icon_frame,
            text="🔍",
            font=ctk.CTkFont(size=24),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Title group
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.place(x=100, rely=0.5, anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Fake News Detection",
            font=ctk.CTkFont(family="SF Pro Display", size=26, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Advanced NLP Classification System",
            font=ctk.CTkFont(family="SF Pro Display", size=12),
            text_color=self.colors["accent_primary"]
        ).pack(anchor="w")

        # Stats badge
        self.stats_badge = ctk.CTkFrame(
            header,
            fg_color=self.colors["bg_card"],
            corner_radius=20,
            height=35
        )
        self.stats_badge.place(relx=0.98, rely=0.5, anchor="e")
        
        self.accuracy_label = ctk.CTkLabel(
            self.stats_badge,
            text="🎯 94.2% Accuracy",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors["accent_secondary"]
        )
        self.accuracy_label.pack(padx=15, pady=5)

    def _create_main_content(self):
        """Create responsive main content area"""
        main = ctk.CTkFrame(
            self.root, 
            fg_color=self.colors["bg_primary"]
        )
        main.grid(row=1, column=0, sticky="nsew", padx=25, pady=20)

        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=2)  # Input area
        main.grid_columnconfigure(1, weight=1)  # Results area

        self._create_left_panel(main)
        self._create_right_panel(main)

    def _create_left_panel(self, parent):
        """Create enhanced input panel"""
        left = ctk.CTkFrame(
            parent, 
            fg_color=self.colors["bg_secondary"], 
            corner_radius=20,
            border_width=1,
            border_color=self.colors["border"]
        )
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        # Header with character count
        header_frame = ctk.CTkFrame(left, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="📄 Article Input",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, sticky="w")

        self.char_count_label = ctk.CTkLabel(
            header_frame,
            text="0 chars",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_muted"]
        )
        self.char_count_label.grid(row=0, column=1, sticky="e")

        # Text input with enhanced styling
        self.text_input = ctk.CTkTextbox(
            left,
            fg_color=self.colors["bg_primary"],
            text_color=self.colors["text_primary"],
            font=ctk.CTkFont(family="SF Mono", size=13),
            corner_radius=12,
            border_width=2,
            border_color=self.colors["border"],
            scrollbar_button_color=self.colors["accent_primary"],
            scrollbar_button_hover_color=self.colors["accent_secondary"]
        )
        self.text_input.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        
        # Bind character counter
        self.text_input.bind('<KeyRelease>', self._update_char_count)

        # Quick actions toolbar
        toolbar = ctk.CTkFrame(left, fg_color="transparent")
        toolbar.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))

        ctk.CTkButton(
            toolbar,
            text="🗑️ Clear",
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color=self.colors["bg_card"],
            text_color=self.colors["text_secondary"],
            width=80,
            height=32,
            command=self._clear_input
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            toolbar,
            text="📋 Paste",
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color=self.colors["bg_card"],
            text_color=self.colors["text_secondary"],
            width=80,
            height=32,
            command=self._paste_from_clipboard
        ).pack(side="left")

    def _create_right_panel(self, parent):
        """Create enhanced results panel"""
        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        right.grid_rowconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=0)

        # Results card with glassmorphism effect
        self.result_card = ctk.CTkFrame(
            right,
            fg_color=self.colors["bg_card"],
            corner_radius=20,
            border_width=1,
            border_color=self.colors["border"]
        )
        self.result_card.grid(row=0, column=0, sticky="new", pady=(0, 20))
        self.result_card.grid_columnconfigure(0, weight=1)

        # Result header
        ctk.CTkLabel(
            self.result_card,
            text="Analysis Results",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 15))

        # Prediction display with icon
        self.prediction_frame = ctk.CTkFrame(
            self.result_card,
            fg_color=self.colors["bg_secondary"],
            corner_radius=15,
            height=120
        )
        self.prediction_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        self.prediction_frame.grid_propagate(False)

        self.prediction_icon = ctk.CTkLabel(
            self.prediction_frame,
            text="⏳",
            font=ctk.CTkFont(size=40)
        )
        self.prediction_icon.place(relx=0.5, rely=0.35, anchor="center")

        self.prediction_label = ctk.CTkLabel(
            self.prediction_frame,
            text="Ready",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_secondary"]
        )
        self.prediction_label.place(relx=0.5, rely=0.75, anchor="center")

        # Confidence section
        confidence_frame = ctk.CTkFrame(self.result_card, fg_color="transparent")
        confidence_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            confidence_frame,
            text="Confidence Score",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_muted"]
        ).pack(side="left")

        self.confidence_value = ctk.CTkLabel(
            confidence_frame,
            text="--%",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        self.confidence_value.pack(side="right")

        # Progress bar with gradient effect
        self.confidence_bar = ctk.CTkProgressBar(
            self.result_card,
            height=8,
            corner_radius=4,
            fg_color=self.colors["bg_secondary"],
            progress_color=self.colors["accent_primary"]
        )
        self.confidence_bar.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.confidence_bar.set(0)

        # Action buttons with enhanced styling
        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="sew")

        self.analyze_btn = ctk.CTkButton(
            btn_frame,
            text="🔍 Analyze Article",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors["accent_primary"],
            hover_color="#ff6b6b",
            text_color="white",
            corner_radius=12,
            height=50,
            command=self.analyze_news
        )
        self.analyze_btn.pack(fill="x", pady=(0, 12))

        self.fetch_btn = ctk.CTkButton(
            btn_frame,
            text="🌐 Fetch Live News",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors["bg_card"],
            hover_color=self.colors["bg_secondary"],
            text_color=self.colors["text_primary"],
            border_width=2,
            border_color=self.colors["border"],
            corner_radius=12,
            height=50,
            command=self.fetch_live_news
        )
        self.fetch_btn.pack(fill="x")

    def _create_status_bar(self):
        """Create professional status bar"""
        status = ctk.CTkFrame(
            self.root, 
            fg_color=self.colors["bg_secondary"], 
            height=40,
            corner_radius=0
        )
        status.grid(row=2, column=0, sticky="ew")
        status.grid_propagate(False)

        # Left side - Status
        self.status_icon = ctk.CTkLabel(
            status,
            text="●",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["accent_success"]
        )
        self.status_icon.place(x=20, rely=0.5, anchor="w")

        self.status_label = ctk.CTkLabel(
            status,
            text="System Ready",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_secondary"]
        )
        self.status_label.place(x=35, rely=0.5, anchor="w")

        # Right side - Model info
        model_info = ctk.CTkLabel(
            status,
            text="Model: PassiveAggressiveClassifier | v2.1.0",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["text_muted"]
        )
        model_info.place(relx=0.98, rely=0.5, anchor="e")

    # ==========================
    # HELPER METHODS
    # ==========================

    def _update_char_count(self, event=None):
        """Update character counter"""
        count = len(self.text_input.get("1.0", "end-1c"))
        self.char_count_label.configure(text=f"{count} chars")

    def _clear_input(self):
        """Clear text input"""
        self.text_input.delete("1.0", "end")
        self._update_char_count()
        self.status_label.configure(text="Input cleared")

    def _paste_from_clipboard(self):
        """Paste from clipboard"""
        try:
            clipboard = self.root.clipboard_get()
            self.text_input.delete("1.0", "end")
            self.text_input.insert("1.0", clipboard)
            self._update_char_count()
            self.status_label.configure(text="Content pasted")
        except:
            self.status_label.configure(text="Clipboard empty")

    def _animate_result(self, target_value, duration=500):
        """Animate progress bar"""
        steps = int(duration / 20)
        increment = target_value / steps
        current = 0
        
        def animate():
            nonlocal current
            current += increment
            if current < target_value:
                self.confidence_bar.set(current)
                self.root.after(20, animate)
            else:
                self.confidence_bar.set(target_value)
        
        animate()

    # ==========================
    # CORE FUNCTIONALITY
    # ==========================

    def analyze_news(self):
        """Enhanced analysis with animations"""
        text_content = self.text_input.get("1.0", "end-1c").strip()

        if not text_content:
            messagebox.showwarning("Input Required", "Please enter a news article to analyze.")
            return

        if len(text_content) < 50:
            messagebox.showwarning("Input Too Short", "Please enter at least 50 characters for accurate analysis.")
            return

        self.is_analyzing = True
        self.status_label.configure(text="Processing...")
        self.status_icon.configure(text_color=self.colors["accent_warning"])
        self.analyze_btn.configure(state="disabled", text="⏳ Analyzing...")
        
        # Reset display
        self.prediction_icon.configure(text="🤔")
        self.prediction_label.configure(text="Analyzing...", text_color=self.colors["text_secondary"])
        self.confidence_value.configure(text="--%")
        self.confidence_bar.set(0)

        # Process after short delay for UI update
        self.root.after(100, self._process_analysis, text_content)

    def _process_analysis(self, text_content):
        """Process the actual analysis"""
        try:
            cleaned = clean_text(text_content)
            vector = self.vectorizer.transform([cleaned])

            prediction = self.model.predict(vector)[0]
            probabilities = self.model.predict_proba(vector)[0]
            confidence = probabilities.max()

            # Determine result styling
            if prediction == 1:
                label = "FAKE NEWS"
                color = self.colors["accent_danger"]
                icon = "⚠️"
                bg_color = "#3d1f1f"
            else:
                label = "REAL NEWS"
                color = self.colors["accent_success"]
                icon = "✅"
                bg_color = "#1f3d3d"

            # Update UI with animation
            self.prediction_frame.configure(fg_color=bg_color)
            self.prediction_icon.configure(text=icon)
            self.prediction_label.configure(text=label, text_color=color)
            self.confidence_value.configure(text=f"{confidence*100:.1f}%", text_color=color)
            self.confidence_bar.configure(progress_color=color)
            
            self._animate_result(confidence)
            
            self.status_label.configure(text="Analysis complete")
            self.status_icon.configure(text_color=self.colors["accent_success"])

        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze:\n{str(e)}")
            self.status_label.configure(text="Error occurred")
            self.status_icon.configure(text_color=self.colors["accent_danger"])
            self.prediction_icon.configure(text="❌")
            self.prediction_label.configure(text="Error", text_color=self.colors["accent_danger"])

        self.is_analyzing = False
        self.analyze_btn.configure(state="normal", text="🔍 Analyze Article")

    def fetch_live_news(self):
        """Enhanced news fetching"""
        if not self.api_key:
            messagebox.showerror("Configuration Error", "NEWS_API_KEY not found in .env file.")
            return

        self.status_label.configure(text="Fetching news...")
        self.status_icon.configure(text_color=self.colors["accent_warning"])
        self.fetch_btn.configure(state="disabled", text="⏳ Fetching...")

        self.root.after(100, self._fetch_news_api)

    def _fetch_news_api(self):
        """Actual API call"""
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "country": "us",
                "category": "general",
                "pageSize": 1,
                "apiKey": self.api_key
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get("status") != "ok":
                raise Exception(data.get("message", "API request failed"))

            articles = data.get("articles", [])
            if not articles:
                raise Exception("No articles found")

            article = articles[0]
            title = article.get("title", "")
            description = article.get("description", "")
            content = article.get("content", "")
            
            full_text = f"{title}\n\n{description}\n\n{content}" if content else f"{title}\n\n{description}"

            self.text_input.delete("1.0", "end")
            self.text_input.insert("1.0", full_text)
            self._update_char_count()

            self.status_label.configure(text=f"Fetched: {title[:50]}...")
            self.status_icon.configure(text_color=self.colors["accent_success"])

        except Exception as e:
            messagebox.showerror("API Error", f"Failed to fetch news:\n{str(e)}")
            self.status_label.configure(text="Fetch failed")
            self.status_icon.configure(text_color=self.colors["accent_danger"])

        self.fetch_btn.configure(state="normal", text="🌐 Fetch Live News")


if __name__ == "__main__":
    root = ctk.CTk()
    app = FakeNewsDetectionApp(root)
    root.mainloop()