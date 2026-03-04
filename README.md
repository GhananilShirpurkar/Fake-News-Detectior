<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=32&pause=1000&color=E94560&center=true&vCenter=true&width=600&lines=📰+Fake+News+Detection;NLP+%2B+Machine+Learning;Built+with+Python" alt="Typing SVG" />

<br/>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-7B2FBE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-00D9FF?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-2ecc71?style=for-the-badge)

<br/>

*A machine learning system that classifies news articles as **real or fake** using classical NLP techniques — complete with a modern desktop GUI, live keyword highlighting, and model explainability.*

<br/>

[Features](#️-desktop-application) · [Installation](#-installation) · [Usage](#-running-the-application) · [Pipeline](#-machine-learning-pipeline) · [Performance](#-model-performance)

</div>

---

## 🖼️ Screenshots

<div align="center">

<!-- Drop your screenshots into an assets/ folder and update the paths below -->

| Main Interface | Analysis Results |
|:-:|:-:|
| ![Main Interface](assets/screenshot-main.png) | ![Analysis Results](assets/screenshot-results.png) |

</div>

> **How to add your screenshots:**
> 1. Create an `assets/` folder in the project root
> 2. Save your screenshots as `assets/screenshot-main.png` and `assets/screenshot-results.png`
> 3. Delete this tip block — the images will render automatically on GitHub

---

## 📌 Overview

Fake news spreads rapidly across digital platforms and can significantly influence public opinion. This project explores how machine learning can automatically classify news articles based on **textual patterns** — covering the full journey from raw data to a polished desktop app.

<div align="center">

|  | What's inside |
|--|---------------|
| 🧹 | Text preprocessing & feature engineering |
| 🤖 | Model training, comparison & cross-validation |
| 📊 | Calibration curve & error analysis |
| 🖥️ | Desktop GUI with real-time explainability |

</div>

---

## ⚙️ System Architecture

```
┌─────────────────────────────────────┐
│          Raw News Article           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Text Cleaning & Normalization   │
│  (lowercase · URLs · punctuation)   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│    TF-IDF Vectorization (1–2 gram)  │
│   max_features=20 000 · max_df=0.7  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│        Machine Learning Model       │
│  Logistic Regression / Naive Bayes  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Classification Output + Confidence│
│          ✅ Real  /  ⚠️ Fake        │
└─────────────────────────────────────┘
```

---

## 🧠 Machine Learning Pipeline

### 1️⃣ Data Loading

| File | Label |
|------|-------|
| `Fake.csv` | Fake — `1` |
| `True.csv` | Real — `0` |

Both datasets are merged into a single labeled corpus. Title and body text are concatenated to give the model richer context.

### 2️⃣ Text Preprocessing

```
raw text  →  lowercase  →  strip URLs  →  remove punctuation & numbers  →  normalise whitespace
```

### 3️⃣ Feature Engineering

```python
TfidfVectorizer(
    stop_words  = "english",
    max_df      = 0.7,
    max_features= 20_000,
    ngram_range = (1, 2),   # unigrams + bigrams
)
```

Bigrams capture phrase-level signals: `"breaking news"`, `"white house"`, `"prime minister"`.

### 4️⃣ Model Comparison

| Model | Strengths |
|-------|-----------|
| **Logistic Regression** | Strong accuracy · interpretable coefficients · calibrated probabilities |
| **Multinomial Naive Bayes** | Blazing-fast training · solid text-classification baseline |

### 5️⃣ Cross-Validation

5-fold CV ensures the reported accuracy is not a lucky split artefact — results are averaged across all folds before the best model is selected and saved.

---

## 📊 Model Performance

```
Mean CV Accuracy  ──  0.949
Test Accuracy     ──  0.948
```

```
              precision    recall    f1-score    support
─────────────────────────────────────────────────────────
  Real News      0.95       0.95       0.95       4 284
  Fake News      0.95       0.95       0.95       4 696
─────────────────────────────────────────────────────────
   accuracy                            0.95       8 980
```

> Logistic Regression consistently outperforms Naive Bayes on this task and is auto-selected as the production model.

---

## 📈 Model Reliability Analysis

### Calibration Curve
Verifies that predicted probabilities match real-world frequencies. A well-calibrated model sits on the diagonal — meaning a 70% confidence prediction is correct ~70% of the time.

### Confidence Distribution
Plots the histogram of predicted probabilities. A bimodal spike near `0.0` and `1.0` indicates strong class separation.

### Error Analysis
Misclassified samples are surfaced and reviewed. Common failure modes include:
- Ambiguous or neutral headlines
- Satirical content that mimics real reporting style
- Politically framed but factually correct articles

---

## 🖥️ Desktop Application

Built with **CustomTkinter** for a sleek, modern dark-themed interface.

| Feature | Detail |
|---------|--------|
| 🔍 **Article Analysis** | Paste text and classify with one click or `Ctrl+Enter` |
| 🎨 **Live Highlighting** | Clickbait phrases (amber) · positive (cyan) · negative (red) sentiment |
| 📖 **Readability Meter** | Animated Flesch score gauge that updates as you type |
| 🧠 **Explainability Panel** | Top influential words with animated weight bars |
| 🎯 **Confidence Display** | Animated circular progress + dual probability bars |
| 🌐 **Live News Fetch** | Pull real headlines directly from NewsAPI |

---

## 🌐 Live News Integration

Integrates with [NewsAPI](https://newsapi.org/) to fetch live top headlines. Analyse real breaking news without copy-pasting anything.

> Requires a free `NEWS_API_KEY` in your `.env` file — see [Installation](#-installation).

---

## 📂 Project Structure

```
fake-news-detector/
│
├── assets/                    ← screenshots & images for README
│
├── data/
│   ├── Fake.csv
│   └── True.csv
│
├── models/
│   ├── model.pkl
│   └── vectorizer.pkl
│
├── src/
│   ├── app.py                 ← desktop GUI
│   ├── train.py               ← training pipeline
│   ├── explain.py             ← explainability utilities
│   ├── utils.py               ← text preprocessing
│   └── __init__.py
│
├── .env                       ← API keys (not committed)
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

---

## 🚀 Installation

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/fake-news-detector.git
cd fake-news-detector
```

**2. Create & activate a virtual environment**

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Add your API key**

```bash
# create a .env file in the project root
echo "NEWS_API_KEY=your_key_here" > .env
```

---

## 🏋️ Training the Model

```bash
python src/train.py
```

This will:

1. Load and merge `Fake.csv` + `True.csv`
2. Clean and vectorize all text
3. Train Logistic Regression and Naive Bayes
4. Run 5-fold cross-validation
5. Save the best model → `models/model.pkl` + `models/vectorizer.pkl`

---

## 🧪 Running the Application

```bash
python src/app.py
```

Paste any article into the input panel and press **Analyze** or `Ctrl+Enter`.

---

## ⚠️ Limitations

This model detects **writing style patterns** — it cannot verify facts.

| Limitation | Impact |
|------------|--------|
| Dataset source bias | May not generalise to non-English or non-US news |
| No fact-checking | A well-written fake article may pass undetected |
| Static vocabulary | Rare or emerging terms may be out-of-vocabulary |

More capable systems would incorporate knowledge graphs, transformer models (BERT / RoBERTa), and live fact-checking APIs.

---

## 🔮 Future Improvements

- [ ] Fine-tuned BERT / RoBERTa classifier
- [ ] Real-time fact verification via external knowledge bases
- [ ] Browser extension for inline detection while browsing
- [ ] Multilingual support
- [ ] Web deployment (FastAPI + React frontend)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Built with 🤍 as an end-to-end ML project exploring NLP-based misinformation detection.**

*If this was useful, consider leaving a ⭐ on GitHub.*

</div>