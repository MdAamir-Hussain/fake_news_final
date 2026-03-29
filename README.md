# TruthLens — Fake News & Spam Detector

> AI-powered text classification system built with FastAPI + React + Tailwind CSS + scikit-learn.

---

## Overview

TruthLens is a full-stack ML application that classifies text (news articles, SMS messages, emails, social posts) as **SPAM/FAKE** or **HAM/REAL** using a trained machine learning pipeline. It features a modern, responsive UI with dark mode, prediction history, confidence visualization, and live API status.

---

## Tech Stack

| Layer       | Technology                                               |
|-------------|----------------------------------------------------------|
| Backend     | Python 3.11, FastAPI, uvicorn, Pydantic v2               |
| ML          | scikit-learn (LR · NB · RF), TF-IDF, NLTK               |
| Frontend    | React 18, Vite, Tailwind CSS v3, Axios, Lucide React     |
| Deployment  | Docker, Docker Compose, Nginx                            |

---

## Features

- **3-model comparison** — Logistic Regression, Naive Bayes, Random Forest
- **TF-IDF** feature extraction with bi-grams
- **Full NLP pipeline** — cleaning → tokenization → stopword removal → lemmatization
- **Confidence score** with animated progress bar
- **Per-class probability** breakdown
- **Prediction history** sidebar with spam/legit ratio chart
- **Dark / Light mode** toggle
- **Live API status** indicator in header
- **Example texts** for quick testing
- **Debug panel** — shows preprocessed text + raw JSON
- **Fully responsive** — works on mobile and desktop
- **Docker ready** — one command to run everything

---

## Project Structure

```
fake_news/
├── backend/
│   ├── main.py             # FastAPI app + /predict endpoint
│   ├── model_trainer.py    # ML training pipeline
│   ├── preprocessor.py     # Text preprocessing (clean/tokenize/lemmatize)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js          # Axios API client
│   │   ├── index.css       # Tailwind + custom animations
│   │   └── components/
│   │       ├── Header.jsx
│   │       ├── TextAnalyzer.jsx
│   │       ├── ResultCard.jsx
│   │       ├── ConfidenceBar.jsx
│   │       ├── HistoryPanel.jsx
│   │       └── LoadingSpinner.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── models/                 # Saved model files (auto-generated)
├── data/                   # Dataset files
├── docker-compose.yml
└── README.md
```

---

## Quick Start

### Prerequisites
- Python 3.10+ with pip
- Node.js 18+
- (Optional) Docker & Docker Compose

---

### 1. Backend Setup

```bash
# From project root
cd fake_news

# Create & activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r backend/requirements.txt

# Train the ML model (downloads SMS Spam Collection automatically)
python backend/model_trainer.py

# Start the API server (run from backend/ directory)
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs → http://localhost:8000/docs

---

### 2. Frontend Setup

```bash
# New terminal — from project root
cd frontend

# Install Node dependencies
npm install

# Copy env file
cp .env.example .env

# Start dev server
npm run dev
```

Open → http://localhost:5173

---

### 3. Docker (full stack)

```bash
# From project root — train model first
python backend/model_trainer.py

# Start everything
docker-compose up --build
```

- Frontend → http://localhost:5173
- Backend  → http://localhost:8000

---

## API Reference

### `POST /predict`

Classify a piece of text.

**Request:**
```json
{ "text": "WINNER!! You have been selected for a £1000 prize. Call now!" }
```

**Response:**
```json
{
  "prediction": "SPAM",
  "label": 1,
  "confidence": 0.9847,
  "probabilities": {
    "ham": 0.0153,
    "spam": 0.9847
  },
  "processed_text": "winner select pound prize call"
}
```

### `GET /health`

```json
{
  "status": "ready",
  "model_name": "Logistic Regression",
  "accuracy": 0.9821,
  "classes": ["ham", "spam"]
}
```

### `GET /model-info`

Returns full model metadata including all model comparison results.

---

## Training Your Own Dataset

Place a CSV file at `data/dataset.csv` with columns `label` and `text`:

```csv
label,text
spam,"Win £1000 now! Call 09..."
ham,"Meeting at 3pm tomorrow"
```

Supported label formats:
- `spam` / `ham`
- `FAKE` / `REAL`
- `1` / `0`

Then run:
```bash
python backend/model_trainer.py
```

The trainer will:
1. Preprocess all text
2. Train Logistic Regression, Naive Bayes, and Random Forest
3. Print a full metrics comparison table
4. Save confusion matrix plots to `models/`
5. Save the best model (by F1-score) to `models/best_model.joblib`

---

## Model Performance (SMS Spam Collection)

| Model               | Accuracy | Precision | Recall | F1-Score |
|---------------------|----------|-----------|--------|----------|
| Logistic Regression | 98.2%    | 98.1%     | 98.2%  | 98.1%    |
| Naive Bayes         | 97.4%    | 97.6%     | 97.4%  | 97.3%    |
| Random Forest       | 97.8%    | 97.9%     | 97.8%  | 97.8%    |

*Results vary depending on dataset size and train/test split.*

---

## Production Build

```bash
# Frontend build
cd frontend
npm run build        # output → dist/

# Backend production
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Deploy

| Service  | Platform         |
|----------|-----------------|
| Backend  | Render / Railway |
| Frontend | Vercel / Netlify |

Set environment variables:
- Backend: `ALLOWED_ORIGINS=https://your-frontend.vercel.app`
- Frontend: `VITE_API_URL=https://your-backend.onrender.com`

---

## Resume Description

> **TruthLens — Fake News & Spam Detection System** | Python · FastAPI · React · scikit-learn · Tailwind CSS
>
> Built a production-ready full-stack ML application that classifies text as spam/fake or legitimate using a TF-IDF + NLP pipeline. Trained and benchmarked Logistic Regression, Naïve Bayes, and Random Forest classifiers on 5,500+ labeled SMS samples, achieving 98.2% accuracy. Designed a responsive React UI with dark mode, animated confidence visualization, and real-time prediction history. Deployed via Docker with FastAPI backend and Nginx-served frontend.
