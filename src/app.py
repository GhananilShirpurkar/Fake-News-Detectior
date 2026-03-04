import os
import re
import time
import math
import random
import joblib
import requests
import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from dotenv import load_dotenv
from utils import clean_text


# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────

CLICKBAIT_PATTERNS = [
    r"\byou won't believe\b", r"\bshocking\b", r"\bbreaking\b", r"\bOMG\b",
    r"\bmiracle\b", r"\bsecret\b", r"\bexposed\b", r"\bscandal\b",
    r"\bconspiracy\b", r"\bhoax\b", r"\bfake\b", r"\blies\b", r"\bcover.?up\b",
    r"\bwake up\b", r"\bthey don't want you to know\b", r"\bshare before deleted\b",
    r"\bgoing viral\b", r"\bmust see\b", r"\bunbelievable\b", r"\bblast\b",
    r"\bslam\b", r"\bdestroy\b", r"\bcrushed\b", r"\bannihilate\b",
    r"\b100%\b", r"\bproven\b", r"\bguaranteed\b", r"\bno doubt\b",
]

SENTIMENT_WORDS = {
    "positive": ["great", "excellent", "wonderful", "amazing", "good", "best",
                 "success", "win", "victory", "improve", "benefit", "safe"],
    "negative": ["terrible", "horrible", "awful", "bad", "worst", "fail",
                 "crisis", "danger", "threat", "attack", "destroy", "collapse"],
}


# ─────────────────────────────────────────────
#  ANIMATED CANVAS WIDGETS
# ─────────────────────────────────────────────

class CircularProgressBar(ctk.CTkFrame):
    """Animated circular progress bar."""

    def __init__(self, parent, size=150, progress=0,
                 fg_color="#2d3748", progress_color="#00d9ff",
                 text_color="white", **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.size = size
        self.progress = progress
        self.fg_color = fg_color
        self.progress_color = progress_color
        self.text_color = text_color

        self.canvas = tk.Canvas(
            self, width=size, height=size,
            bg="#16213e", highlightthickness=0
        )
        self.canvas.pack()

        self.center_x = size // 2
        self.center_y = size // 2
        self.radius = (size - 20) // 2
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        # Subtle shadow ring
        self.canvas.create_oval(
            self.center_x - self.radius + 2, self.center_y - self.radius + 2,
            self.center_x + self.radius + 2, self.center_y + self.radius + 2,
            outline="#0a0a14", width=10, fill=""
        )
        # Background track
        self.canvas.create_oval(
            self.center_x - self.radius, self.center_y - self.radius,
            self.center_x + self.radius, self.center_y + self.radius,
            outline=self.fg_color, width=8, fill=""
        )
        # Progress arc
        if self.progress > 0:
            angle = self.progress * 360
            self.canvas.create_arc(
                self.center_x - self.radius, self.center_y - self.radius,
                self.center_x + self.radius, self.center_y + self.radius,
                start=90, extent=-angle,
                outline=self.progress_color, width=8, style="arc"
            )
            # Glow tip dot
            tip_rad = math.radians(90 - angle)
            tip_x = self.center_x + self.radius * math.cos(tip_rad)
            tip_y = self.center_y - self.radius * math.sin(tip_rad)
            r = 6
            self.canvas.create_oval(
                tip_x - r, tip_y - r, tip_x + r, tip_y + r,
                fill=self.progress_color, outline=""
            )
        # Percentage text
        self.canvas.create_text(
            self.center_x, self.center_y,
            text=f"{int(self.progress * 100)}%",
            font=("Courier", 22, "bold"),
            fill=self.text_color
        )

    def set_progress(self, value):
        self.progress = max(0.0, min(1.0, value))
        self.draw()

    def set_color(self, color):
        self.progress_color = color
        self.draw()


class ReadabilityMeter(ctk.CTkFrame):
    """Animated horizontal gauge for readability / complexity score."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._score = 0.0
        self._label_var = tk.StringVar(value="—")

        lbl = ctk.CTkLabel(self, text="Readability", font=ctk.CTkFont(size=11),
                           text_color="#6c757d")
        lbl.pack(anchor="w")

        self.canvas = tk.Canvas(self, width=260, height=28,
                                bg="#1a1a2e", highlightthickness=0)
        self.canvas.pack(fill="x", pady=(3, 0))

        self.score_lbl = ctk.CTkLabel(self, textvariable=self._label_var,
                                      font=ctk.CTkFont(size=11, weight="bold"),
                                      text_color="#ffffff")
        self.score_lbl.pack(anchor="e")
        self._render(0)

    def _render(self, fraction):
        w = self.canvas.winfo_reqwidth()
        h = 28
        self.canvas.delete("all")
        # Track
        self._rrect(2, 8, w - 2, h - 8, radius=6, fill="#2d3748", outline="")
        # Fill
        fill_w = max(0, int((w - 4) * fraction))
        if fill_w > 0:
            color = self._score_color(fraction)
            self._rrect(2, 8, 2 + fill_w, h - 8, radius=6, fill=color, outline="")
        # Tick marks
        for i in range(1, 5):
            x = int(w * i / 5)
            self.canvas.create_line(x, 10, x, h - 10, fill="#0f0f1a", width=1)

    def _rrect(self, x1, y1, x2, y2, radius=8, **kw):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, **kw)

    @staticmethod
    def _score_color(f):
        if f < 0.4:
            return "#e94560"   # hard to read → red
        elif f < 0.7:
            return "#f39c12"   # moderate → amber
        else:
            return "#00d9ff"   # easy → cyan

    def animate_to(self, score_0_to_100, label_text, root):
        self._score = score_0_to_100 / 100
        target = self._score
        current = [0.0]
        steps = 40

        def step():
            current[0] += target / steps
            frac = min(current[0], target)
            self._render(frac)
            if current[0] < target:
                root.after(20, step)
            else:
                self._render(target)

        self._label_var.set(label_text)
        step()


# ─────────────────────────────────────────────
#  EXPLAINABILITY PANEL
# ─────────────────────────────────────────────

class ExplainabilityPanel(ctk.CTkFrame):
    """Shows top influential words as animated horizontal bar rows."""

    BAR_W = 200

    def __init__(self, parent, colors, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.colors = colors
        self._rows = []

        ctk.CTkLabel(self, text="🧠 Top Influential Words",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=colors["text_secondary"]).pack(anchor="w", pady=(0, 8))

        self.rows_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.rows_frame.pack(fill="x")

    def update_words(self, word_scores: list[tuple[str, float, str]], root):
        """
        word_scores: [(word, weight_0_to_1, 'fake'|'real'), ...]
        """
        # Clear old rows
        for w in self.rows_frame.winfo_children():
            w.destroy()
        self._rows.clear()

        for i, (word, weight, side) in enumerate(word_scores[:8]):
            color = self.colors["accent_danger"] if side == "fake" else self.colors["accent_success"]
            row = ctk.CTkFrame(self.rows_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            word_lbl = ctk.CTkLabel(row, text=word,
                                    font=ctk.CTkFont(family="Courier", size=11, weight="bold"),
                                    text_color=self.colors["text_primary"],
                                    width=110, anchor="w")
            word_lbl.pack(side="left")

            canvas = tk.Canvas(row, width=self.BAR_W, height=16,
                               bg="#1a1a2e", highlightthickness=0)
            canvas.pack(side="left", padx=(4, 8))

            pct_lbl = ctk.CTkLabel(row, text="",
                                   font=ctk.CTkFont(size=10),
                                   text_color=color, width=40)
            pct_lbl.pack(side="left")

            tag_lbl = ctk.CTkLabel(row,
                                   text="FAKE" if side == "fake" else "REAL",
                                   font=ctk.CTkFont(size=9, weight="bold"),
                                   text_color=color,
                                   fg_color=color + "22",
                                   corner_radius=4, width=36)
            tag_lbl.pack(side="left", padx=4)

            self._rows.append((canvas, pct_lbl, weight, color))
            # Stagger animation
            root.after(i * 60, lambda c=canvas, p=pct_lbl, wt=weight, col=color:
                       self._animate_bar(c, p, wt, col, root))

    def _animate_bar(self, canvas, pct_lbl, target, color, root):
        current = [0.0]
        steps = 30

        def step():
            current[0] += target / steps
            frac = min(current[0], target)
            fill_w = int(self.BAR_W * frac)
            canvas.delete("all")
            canvas.create_rectangle(0, 4, self.BAR_W, 12,
                                    fill="#2d3748", outline="")
            if fill_w > 0:
                canvas.create_rectangle(0, 4, fill_w, 12,
                                        fill=color, outline="")
            if current[0] < target:
                root.after(16, step)
            else:
                pct_lbl.configure(text=f"{int(target * 100)}%")

        step()


# ─────────────────────────────────────────────
#  KEYWORD HIGHLIGHTER
# ─────────────────────────────────────────────

class KeywordHighlighter:
    """Applies colour tags to a CTkTextbox canvas for suspicious phrases."""

    CLICKBAIT_TAG = "clickbait"
    SENTIMENT_POS_TAG = "sentiment_pos"
    SENTIMENT_NEG_TAG = "sentiment_neg"

    def __init__(self, textbox: ctk.CTkTextbox):
        self.tb = textbox
        self._setup_tags()

    def _setup_tags(self):
        self.tb.tag_config(self.CLICKBAIT_TAG,
                           foreground="#f39c12",
                           background="#2d2010")
        self.tb.tag_config(self.SENTIMENT_POS_TAG,
                           foreground="#00d9ff",
                           background="#0d2a2a")
        self.tb.tag_config(self.SENTIMENT_NEG_TAG,
                           foreground="#e94560",
                           background="#2d0d14")

    def highlight(self):
        """Re-scan and re-apply all tags."""
        text = self.tb.get("1.0", "end-1c")
        # Remove old tags
        for tag in (self.CLICKBAIT_TAG, self.SENTIMENT_POS_TAG, self.SENTIMENT_NEG_TAG):
            self.tb.tag_remove(tag, "1.0", "end")

        self._apply_patterns(text, CLICKBAIT_PATTERNS, self.CLICKBAIT_TAG)
        for w in SENTIMENT_WORDS["positive"]:
            self._apply_word(text, w, self.SENTIMENT_POS_TAG)
        for w in SENTIMENT_WORDS["negative"]:
            self._apply_word(text, w, self.SENTIMENT_NEG_TAG)

    def _apply_patterns(self, text, patterns, tag):
        for pat in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                start = f"1.0 + {m.start()} chars"
                end = f"1.0 + {m.end()} chars"
                self.tb.tag_add(tag, start, end)

    def _apply_word(self, text, word, tag):
        pat = r"\b" + re.escape(word) + r"\b"
        for m in re.finditer(pat, text, re.IGNORECASE):
            start = f"1.0 + {m.start()} chars"
            end = f"1.0 + {m.end()} chars"
            self.tb.tag_add(tag, start, end)

    def count_flags(self, text):
        flagged = sum(
            1 for p in CLICKBAIT_PATTERNS
            if re.search(p, text, re.IGNORECASE)
        )
        return flagged


# ─────────────────────────────────────────────
#  READABILITY HELPERS
# ─────────────────────────────────────────────

def flesch_score(text: str) -> float:
    """Approximate Flesch Reading Ease (0–100, higher = easier)."""
    sentences = max(1, len(re.split(r'[.!?]+', text)))
    words = text.split()
    if not words:
        return 50.0
    syllables = sum(_count_syllables(w) for w in words)
    score = 206.835 - 1.015 * (len(words) / sentences) - 84.6 * (syllables / len(words))
    return max(0.0, min(100.0, score))


def _count_syllables(word: str) -> int:
    word = word.lower().strip(".,!?;:'\"")
    if not word:
        return 1
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in word:
        is_v = ch in vowels
        if is_v and not prev_vowel:
            count += 1
        prev_vowel = is_v
    if word.endswith("e"):
        count = max(1, count - 1)
    return max(1, count)


def readability_label(score: float) -> str:
    if score >= 70:
        return "Easy to Read"
    elif score >= 50:
        return "Moderate"
    elif score >= 30:
        return "Complex"
    else:
        return "Very Dense"


# ─────────────────────────────────────────────
#  EXPLAINABILITY HELPERS
# ─────────────────────────────────────────────

def get_top_words(model, vectorizer, text: str, n=8):
    """
    Extract top-n influential words using the model's coef_ or feature importances.
    Returns list of (word, normalised_weight, 'fake'|'real').
    """
    try:
        cleaned = clean_text(text)
        vec = vectorizer.transform([cleaned])
        feature_names = vectorizer.get_feature_names_out()

        # For PassiveAggressiveClassifier / LinearSVC / LogisticRegression
        if hasattr(model, "coef_"):
            coef = model.coef_[0]
        elif hasattr(model, "feature_importances_"):
            coef = model.feature_importances_
        else:
            return []

        # Only look at words that actually appear in the document
        nonzero_indices = vec.nonzero()[1]
        if len(nonzero_indices) == 0:
            return []

        word_weights = []
        for idx in nonzero_indices:
            word = feature_names[idx]
            weight = coef[idx]
            word_weights.append((word, weight))

        # Sort by absolute weight
        word_weights.sort(key=lambda x: abs(x[1]), reverse=True)
        top = word_weights[:n]

        if not top:
            return []

        max_abs = max(abs(w) for _, w in top) or 1.0
        result = []
        for word, w in top:
            norm = abs(w) / max_abs
            side = "fake" if w > 0 else "real"
            result.append((word, norm, side))
        return result
    except Exception:
        return []


# ─────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────

class FakeNewsDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fake News Detection System")
        self.root.geometry("1280x860")
        self.root.minsize(1150, 750)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        load_dotenv()
        self.api_key = os.getenv("NEWS_API_KEY")

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_PATH = os.path.join(BASE_DIR, "../models/model.pkl")
        VECTORIZER_PATH = os.path.join(BASE_DIR, "../models/vectorizer.pkl")

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
        self._highlight_job = None   # debounce timer id

        self.colors = {
            "bg_primary":      "#0f0f1a",
            "bg_secondary":    "#1a1a2e",
            "bg_card":         "#16213e",
            "bg_light":        "#1e2a4a",
            "accent_primary":  "#e94560",
            "accent_secondary":"#00d9ff",
            "accent_success":  "#00d9ff",
            "accent_danger":   "#e94560",
            "accent_warning":  "#f39c12",
            "text_primary":    "#ffffff",
            "text_secondary":  "#a0a0a0",
            "text_muted":      "#6c757d",
            "border":          "#2d3748",
        }

        self.root.configure(fg_color=self.colors["bg_primary"])
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Keyboard shortcut
        self.root.bind("<Control-Return>", lambda e: self.analyze_news())

        self._create_header()
        self._create_main_content()
        self._create_status_bar()

        # Fade-in the whole window
        self.root.attributes("-alpha", 0.0)
        self._fade_in(0)

    # ──────────────────────────────────────
    #  FADE-IN ANIMATION
    # ──────────────────────────────────────

    def _fade_in(self, step):
        alpha = step / 20
        if alpha <= 1.0:
            self.root.attributes("-alpha", alpha)
            self.root.after(18, lambda: self._fade_in(step + 1))

    # ──────────────────────────────────────
    #  UI CREATION
    # ──────────────────────────────────────

    def _create_header(self):
        header = ctk.CTkFrame(self.root, fg_color=self.colors["bg_secondary"],
                              height=90, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        icon_frame = ctk.CTkFrame(header, fg_color=self.colors["accent_primary"],
                                  width=50, height=50, corner_radius=12)
        icon_frame.place(x=30, rely=0.5, anchor="w")
        icon_frame.grid_propagate(False)
        ctk.CTkLabel(icon_frame, text="🔍", font=ctk.CTkFont(size=24),
                     text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.place(x=100, rely=0.5, anchor="w")
        ctk.CTkLabel(title_frame, text="Fake News Detection",
                     font=ctk.CTkFont(family="Courier", size=26, weight="bold"),
                     text_color=self.colors["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Advanced NLP Classification System",
                     font=ctk.CTkFont(size=12),
                     text_color=self.colors["accent_primary"]).pack(anchor="w")

        # Keyboard hint
        ctk.CTkLabel(header, text="⌨  Ctrl+Enter to Analyze",
                     font=ctk.CTkFont(size=10),
                     text_color=self.colors["text_muted"]).place(relx=0.5, rely=0.5, anchor="center")

        badge = ctk.CTkFrame(header, fg_color=self.colors["bg_card"],
                             corner_radius=20, height=35)
        badge.place(relx=0.98, rely=0.5, anchor="e")
        ctk.CTkLabel(badge, text="🎯 94.2% Accuracy",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=self.colors["accent_secondary"]).pack(padx=15, pady=5)

    def _create_main_content(self):
        main = ctk.CTkFrame(self.root, fg_color=self.colors["bg_primary"])
        main.grid(row=1, column=0, sticky="nsew", padx=25, pady=20)
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=2)
        main.grid_columnconfigure(1, weight=3)   # wider results column now

        self._create_left_panel(main)
        self._create_right_panel(main)

    # ── LEFT PANEL ──────────────────────────

    def _create_left_panel(self, parent):
        left = ctk.CTkFrame(parent, fg_color=self.colors["bg_secondary"],
                            corner_radius=20, border_width=1,
                            border_color=self.colors["border"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        # Header
        hdr = ctk.CTkFrame(left, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        hdr.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(hdr, text="📄 Article Input",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=self.colors["text_primary"]).grid(row=0, column=0, sticky="w")

        self.char_count_label = ctk.CTkLabel(hdr, text="0 chars",
                                             font=ctk.CTkFont(size=11),
                                             text_color=self.colors["text_muted"])
        self.char_count_label.grid(row=0, column=1, sticky="e")

        # Highlight legend
        legend = ctk.CTkFrame(left, fg_color="transparent")
        legend.grid(row=0, column=0, sticky="e", padx=20)
        self._legend_dot(legend, "#f39c12", "Clickbait").pack(side="left", padx=4)
        self._legend_dot(legend, "#00d9ff", "+ Sentiment").pack(side="left", padx=4)
        self._legend_dot(legend, "#e94560", "− Sentiment").pack(side="left", padx=4)

        # Text input
        self.text_input = ctk.CTkTextbox(
            left,
            fg_color=self.colors["bg_primary"],
            text_color=self.colors["text_primary"],
            font=ctk.CTkFont(family="Courier", size=13),
            corner_radius=12, border_width=2,
            border_color=self.colors["border"],
            scrollbar_button_color=self.colors["accent_primary"],
            scrollbar_button_hover_color=self.colors["accent_secondary"]
        )
        self.text_input.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.text_input.bind("<KeyRelease>", self._on_key_release)

        # Keyword highlighter
        self.highlighter = KeywordHighlighter(self.text_input)

        # Readability meter
        self.readability_meter = ReadabilityMeter(left)
        self.readability_meter.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 8))

        # Toolbar
        toolbar = ctk.CTkFrame(left, fg_color="transparent")
        toolbar.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))

        for label, cmd in [("🗑️ Clear", self._clear_input),
                            ("📋 Paste", self._paste_from_clipboard)]:
            ctk.CTkButton(toolbar, text=label, font=ctk.CTkFont(size=11),
                          fg_color="transparent",
                          hover_color=self.colors["bg_card"],
                          text_color=self.colors["text_secondary"],
                          width=85, height=32, command=cmd).pack(side="left", padx=(0, 8))

        self.flag_badge = ctk.CTkLabel(toolbar, text="",
                                       font=ctk.CTkFont(size=10, weight="bold"),
                                       text_color=self.colors["accent_warning"],
                                       fg_color="#2d2010", corner_radius=8)
        self.flag_badge.pack(side="right")

    def _legend_dot(self, parent, color, label):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(f, text="●", font=ctk.CTkFont(size=9),
                     text_color=color).pack(side="left")
        ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=9),
                     text_color=self.colors["text_muted"]).pack(side="left")
        return f

    # ── RIGHT PANEL ──────────────────────────

    def _create_right_panel(self, parent):
        right = ctk.CTkScrollableFrame(
            parent, fg_color="transparent",
            scrollbar_button_color=self.colors["bg_card"]
        )
        right.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        right.grid_columnconfigure(0, weight=1)

        # ── Results card ──
        self.result_card = ctk.CTkFrame(right, fg_color=self.colors["bg_card"],
                                        corner_radius=20, border_width=1,
                                        border_color=self.colors["border"])
        self.result_card.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        self.result_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.result_card, text="Analysis Results",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=self.colors["text_primary"]
                     ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 15))

        # Circular progress
        pred_frame = ctk.CTkFrame(self.result_card,
                                  fg_color=self.colors["bg_secondary"],
                                  corner_radius=15)
        pred_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        pred_frame.grid_columnconfigure(0, weight=1)

        self.circular_progress = CircularProgressBar(
            pred_frame, size=150, progress=0,
            fg_color=self.colors["border"],
            progress_color=self.colors["accent_secondary"]
        )
        self.circular_progress.grid(row=0, column=0, pady=(20, 10))

        self.prediction_label = ctk.CTkLabel(
            pred_frame, text="Ready to Analyze",
            font=ctk.CTkFont(family="Courier", size=18, weight="bold"),
            text_color=self.colors["text_secondary"])
        self.prediction_label.grid(row=1, column=0, pady=(0, 5))

        self.prediction_confidence = ctk.CTkLabel(
            pred_frame, text="Enter text to begin analysis",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_muted"])
        self.prediction_confidence.grid(row=2, column=0, pady=(0, 20))

        # Probability bars
        prob_frame = ctk.CTkFrame(self.result_card, fg_color="transparent")
        prob_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 15))

        self.real_prob_value, self.real_prob_bar = self._prob_row(
            prob_frame, "✅ Real News", self.colors["accent_success"])
        self.fake_prob_value, self.fake_prob_bar = self._prob_row(
            prob_frame, "⚠️ Fake News", self.colors["accent_danger"])

        # Analysis details
        info_frame = ctk.CTkFrame(self.result_card, fg_color="transparent")
        info_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 15))

        ctk.CTkLabel(info_frame, text="📊 Analysis Details",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=self.colors["text_secondary"]
                     ).pack(anchor="w", pady=(0, 8))

        info_grid = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_grid.pack(fill="x")

        self.info_word_count     = self._info_item(info_grid, "Word Count:",    "--",                 0, 0)
        self.info_char_count     = self._info_item(info_grid, "Characters:",    "--",                 0, 1)
        self.info_model_used     = self._info_item(info_grid, "Model:",         "PassiveAggressive",  1, 0)
        self.info_processing_time= self._info_item(info_grid, "Processing:",    "--ms",               1, 1)
        self.info_flags          = self._info_item(info_grid, "Clickbait flags:","--",                2, 0)
        self.info_readability    = self._info_item(info_grid, "Readability:",   "--",                 2, 1)

        # Verdict
        self.verdict_frame = ctk.CTkFrame(self.result_card,
                                          fg_color=self.colors["bg_secondary"],
                                          corner_radius=10)
        self.verdict_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))

        self.verdict_label = ctk.CTkLabel(
            self.verdict_frame, text="🤖 Waiting for input...",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_muted"],
            wraplength=340)
        self.verdict_label.pack(padx=15, pady=12)

        # ── Explainability card ──
        self.explain_card = ctk.CTkFrame(right, fg_color=self.colors["bg_card"],
                                         corner_radius=20, border_width=1,
                                         border_color=self.colors["border"])
        self.explain_card.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        self.explain_card.grid_columnconfigure(0, weight=1)

        self.explain_panel = ExplainabilityPanel(self.explain_card, self.colors)
        self.explain_panel.grid(row=0, column=0, sticky="ew", padx=20, pady=20)

        # Placeholder message
        self.explain_placeholder = ctk.CTkLabel(
            self.explain_card,
            text="Run analysis to see which words drove the prediction.",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_muted"])
        self.explain_placeholder.grid(row=1, column=0, padx=20, pady=(0, 20))

        # ── Action buttons ──
        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew")

        self.analyze_btn = ctk.CTkButton(
            btn_frame, text="🔍 Analyze Article  (Ctrl+Enter)",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors["accent_primary"],
            hover_color="#ff6b6b", text_color="white",
            corner_radius=12, height=50,
            command=self.analyze_news)
        self.analyze_btn.pack(fill="x", pady=(0, 12))

        self.fetch_btn = ctk.CTkButton(
            btn_frame, text="🌐 Fetch Live News",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors["bg_card"],
            hover_color=self.colors["bg_secondary"],
            text_color=self.colors["text_primary"],
            border_width=2, border_color=self.colors["border"],
            corner_radius=12, height=50,
            command=self.fetch_live_news)
        self.fetch_btn.pack(fill="x")

    def _prob_row(self, parent, label_text, color):
        card = ctk.CTkFrame(parent, fg_color=self.colors["bg_secondary"],
                            corner_radius=12, height=70)
        card.pack(fill="x", pady=(0, 10))
        card.pack_propagate(False)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(hdr, text=label_text,
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=color).pack(side="left")

        val_lbl = ctk.CTkLabel(hdr, text="--%",
                               font=ctk.CTkFont(size=13, weight="bold"),
                               text_color=self.colors["text_primary"])
        val_lbl.pack(side="right")

        bar = ctk.CTkProgressBar(card, height=6, corner_radius=3,
                                 fg_color=self.colors["bg_card"],
                                 progress_color=color)
        bar.pack(fill="x", padx=15, pady=(0, 10))
        bar.set(0)
        return val_lbl, bar

    def _info_item(self, parent, label, value, row, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, sticky="ew", padx=5, pady=3)
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11),
                     text_color=self.colors["text_muted"]).pack(side="left")
        val = ctk.CTkLabel(frame, text=value,
                           font=ctk.CTkFont(size=11, weight="bold"),
                           text_color=self.colors["text_primary"])
        val.pack(side="right")
        return val

    def _create_status_bar(self):
        status = ctk.CTkFrame(self.root, fg_color=self.colors["bg_secondary"],
                              height=40, corner_radius=0)
        status.grid(row=2, column=0, sticky="ew")
        status.grid_propagate(False)

        self.status_icon = ctk.CTkLabel(status, text="●", font=ctk.CTkFont(size=10),
                                        text_color=self.colors["accent_success"])
        self.status_icon.place(x=20, rely=0.5, anchor="w")

        self.status_label = ctk.CTkLabel(status, text="System Ready",
                                         font=ctk.CTkFont(size=11),
                                         text_color=self.colors["text_secondary"])
        self.status_label.place(x=35, rely=0.5, anchor="w")

        ctk.CTkLabel(status,
                     text="Model: PassiveAggressiveClassifier | v2.1.0",
                     font=ctk.CTkFont(size=10),
                     text_color=self.colors["text_muted"]
                     ).place(relx=0.98, rely=0.5, anchor="e")

    # ──────────────────────────────────────
    #  HELPER METHODS
    # ──────────────────────────────────────

    def _on_key_release(self, event=None):
        self._update_char_count()
        # Debounce: highlight + readability only 400 ms after last keystroke
        if self._highlight_job:
            self.root.after_cancel(self._highlight_job)
        self._highlight_job = self.root.after(400, self._live_update)

    def _live_update(self):
        """Highlight keywords + update readability meter in real time."""
        text = self.text_input.get("1.0", "end-1c")
        self.highlighter.highlight()
        # Readability
        score = flesch_score(text)
        self.readability_meter.animate_to(score, readability_label(score), self.root)
        # Clickbait flag count
        flags = self.highlighter.count_flags(text)
        if flags > 0:
            self.flag_badge.configure(text=f"⚠ {flags} flag{'s' if flags != 1 else ''}")
        else:
            self.flag_badge.configure(text="")

    def _update_char_count(self, event=None):
        count = len(self.text_input.get("1.0", "end-1c"))
        self.char_count_label.configure(text=f"{count} chars")

    def _clear_input(self):
        self.text_input.delete("1.0", "end")
        self._update_char_count()
        self.flag_badge.configure(text="")
        self._set_status("Input cleared")
        self._reset_results()

    def _paste_from_clipboard(self):
        try:
            clipboard = self.root.clipboard_get()
            self.text_input.delete("1.0", "end")
            self.text_input.insert("1.0", clipboard)
            self._on_key_release()
            self._set_status("Content pasted")
        except Exception:
            self._set_status("Clipboard empty")

    def _reset_results(self):
        self.circular_progress.set_progress(0)
        self.circular_progress.set_color(self.colors["accent_secondary"])
        self.prediction_label.configure(text="Ready to Analyze",
                                        text_color=self.colors["text_secondary"])
        self.prediction_confidence.configure(text="Enter text to begin analysis",
                                             text_color=self.colors["text_muted"])
        self.real_prob_value.configure(text="--%", text_color=self.colors["text_primary"])
        self.real_prob_bar.set(0)
        self.fake_prob_value.configure(text="--%", text_color=self.colors["text_primary"])
        self.fake_prob_bar.set(0)
        self.info_word_count.configure(text="--")
        self.info_char_count.configure(text="--")
        self.info_processing_time.configure(text="--ms")
        self.info_flags.configure(text="--")
        self.info_readability.configure(text="--")
        self.verdict_label.configure(text="🤖 Waiting for input...",
                                     text_color=self.colors["text_muted"])
        self.verdict_frame.configure(fg_color=self.colors["bg_secondary"])
        self.explain_placeholder.configure(
            text="Run analysis to see which words drove the prediction.")

    def _animate_circular_progress(self, target_value, color, duration=800):
        steps = int(duration / 20)
        increment = target_value / max(steps, 1)
        current = [0.0]
        self.circular_progress.set_color(color)

        def animate():
            nonlocal current
            current[0] += increment
            frac = min(current[0], target_value)
            self.circular_progress.set_progress(frac)
            if current[0] < target_value:
                self.root.after(20, animate)

        animate()

    def _animate_prob_bar(self, bar, target, delay=0):
        """Animate a CTkProgressBar from 0 to target."""
        steps = 35
        inc = target / steps
        current = [0.0]

        def step():
            current[0] += inc
            bar.set(min(current[0], target))
            if current[0] < target:
                self.root.after(16, step)

        self.root.after(delay, step)

    def _set_status(self, text, color=None):
        self.status_label.configure(text=text)
        if color:
            self.status_icon.configure(text_color=color)

    def _reveal_verdict(self, full_text, color, delay_per_char=18):
        """Animate verdict text character-by-character."""
        self.verdict_label.configure(text="", text_color=color)
        total = len(full_text)

        def reveal(i):
            if i <= total:
                self.verdict_label.configure(text=full_text[:i])
                self.root.after(delay_per_char, lambda: reveal(i + 1))

        reveal(0)

    # ──────────────────────────────────────
    #  CORE FUNCTIONALITY
    # ──────────────────────────────────────

    def analyze_news(self):
        text_content = self.text_input.get("1.0", "end-1c").strip()

        if not text_content:
            messagebox.showwarning("Input Required", "Please enter a news article to analyze.")
            return
        if len(text_content) < 50:
            messagebox.showwarning("Input Too Short",
                                   "Please enter at least 50 characters for accurate analysis.")
            return

        self.is_analyzing = True
        self._set_status("Processing...", self.colors["accent_warning"])
        self.analyze_btn.configure(state="disabled", text="⏳ Analyzing...")

        self._reset_results()
        self.prediction_label.configure(text="Analyzing...",
                                        text_color=self.colors["text_secondary"])

        word_count = len(text_content.split())
        char_count = len(text_content)
        self.info_word_count.configure(text=str(word_count))
        self.info_char_count.configure(text=str(char_count))

        start_time = time.time()
        self.root.after(100, lambda: self._process_analysis(text_content, start_time))

    def _process_analysis(self, text_content, start_time):
        try:
            cleaned = clean_text(text_content)
            vector = self.vectorizer.transform([cleaned])

            prediction = self.model.predict(vector)[0]
            probabilities = self.model.predict_proba(vector)[0]

            real_prob = probabilities[0] if len(probabilities) > 1 else 1 - probabilities[0]
            fake_prob = probabilities[1] if len(probabilities) > 1 else probabilities[0]

            processing_time = int((time.time() - start_time) * 1000)

            # Readability
            r_score = flesch_score(text_content)
            flags   = self.highlighter.count_flags(text_content)

            if prediction == 1:
                label        = "FAKE NEWS DETECTED"
                main_color   = self.colors["accent_danger"]
                verdict_bg   = "#3d1f1f"
                conf_text    = f"Confidence: {fake_prob * 100:.1f}%"
                main_progress= fake_prob
                verdict_text = (
                    f"⚠️ This article shows characteristics of fake news with "
                    f"{fake_prob * 100:.1f}% confidence. Verify sources before sharing."
                )
            else:
                label        = "REAL NEWS VERIFIED"
                main_color   = self.colors["accent_success"]
                verdict_bg   = "#1f3d3d"
                conf_text    = f"Confidence: {real_prob * 100:.1f}%"
                main_progress= real_prob
                verdict_text = (
                    f"✅ This article appears legitimate with "
                    f"{real_prob * 100:.1f}% confidence. Always cross-check important information."
                )

            # ── Animate results ──
            self._animate_circular_progress(main_progress, main_color)
            self.prediction_label.configure(text=label, text_color=main_color)
            self.prediction_confidence.configure(text=conf_text, text_color=main_color)

            self.real_prob_value.configure(text=f"{real_prob * 100:.1f}%",
                                           text_color=self.colors["accent_success"])
            self._animate_prob_bar(self.real_prob_bar, real_prob, delay=200)

            self.fake_prob_value.configure(text=f"{fake_prob * 100:.1f}%",
                                           text_color=self.colors["accent_danger"])
            self._animate_prob_bar(self.fake_prob_bar, fake_prob, delay=350)

            self.info_processing_time.configure(text=f"{processing_time}ms")
            self.info_flags.configure(text=str(flags) if flags else "0")
            self.info_readability.configure(text=readability_label(r_score))

            # Animated verdict text
            self.verdict_frame.configure(fg_color=verdict_bg)
            self.root.after(600, lambda: self._reveal_verdict(verdict_text, main_color))

            # ── Explainability panel ──
            top_words = get_top_words(self.model, self.vectorizer, text_content)
            if top_words:
                self.explain_placeholder.configure(text="")
                self.root.after(400, lambda: self.explain_panel.update_words(top_words, self.root))
            else:
                self.explain_placeholder.configure(
                    text="Explainability not available for this model type.")

            self._set_status("Analysis complete ✓", self.colors["accent_success"])

        except Exception as e:
            messagebox.showerror("Analysis Error", f"An error occurred:\n{str(e)}")
            self._set_status("Analysis failed", self.colors["accent_danger"])
            self._reset_results()
        finally:
            self.is_analyzing = False
            self.analyze_btn.configure(state="normal", text="🔍 Analyze Article  (Ctrl+Enter)")

    # ──────────────────────────────────────
    #  LIVE NEWS FETCH
    # ──────────────────────────────────────

    def fetch_live_news(self):
        if not self.api_key:
            messagebox.showerror("API Key Missing",
                                 "No NEWS_API_KEY found in your .env file.\n"
                                 "Please add your NewsAPI key to use this feature.")
            return
        self.fetch_btn.configure(state="disabled", text="⏳ Fetching...")
        self._set_status("Fetching live news...", self.colors["accent_warning"])
        self.root.after(50, self._do_fetch_live_news)

    def _do_fetch_live_news(self):
        try:
            response = requests.get(
                "https://newsapi.org/v2/top-headlines",
                params={"apiKey": self.api_key, "language": "en",
                        "pageSize": 1, "page": random.randint(1, 5)},
                timeout=10
            )
            response.raise_for_status()
            articles = response.json().get("articles", [])
            if not articles:
                messagebox.showinfo("No Articles", "No articles returned.")
                return

            art = articles[0]
            parts = [p for p in [
                art.get("title", ""),
                art.get("description", ""),
                (art.get("content") or "").split("[+")[0].strip()
            ] if p]
            full_text = "\n\n".join(parts)

            if not full_text.strip():
                messagebox.showinfo("Empty Article", "The fetched article had no readable content.")
                return

            self.text_input.delete("1.0", "end")
            self.text_input.insert("1.0", full_text)
            self._on_key_release()
            self._reset_results()
            source = art.get("source", {}).get("name", "Unknown Source")
            self._set_status(f"Fetched from: {source}", self.colors["accent_success"])

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Network Error", "Could not connect. Check your internet connection.")
            self._set_status("Fetch failed — no connection", self.colors["accent_danger"])
        except requests.exceptions.Timeout:
            messagebox.showerror("Timeout", "Request timed out. Try again.")
            self._set_status("Fetch timed out", self.colors["accent_danger"])
        except requests.exceptions.HTTPError as e:
            messagebox.showerror("API Error", f"NewsAPI returned an error:\n{str(e)}")
            self._set_status("API error", self.colors["accent_danger"])
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error:\n{str(e)}")
            self._set_status("Fetch failed", self.colors["accent_danger"])
        finally:
            self.fetch_btn.configure(state="normal", text="🌐 Fetch Live News")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = ctk.CTk()
    app = FakeNewsDetectionApp(root)
    root.mainloop()