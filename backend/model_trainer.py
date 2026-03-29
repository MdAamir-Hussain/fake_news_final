"""
ML Training Pipeline — Improved
Fixes: class imbalance, adds LinearSVC, GridSearchCV, SMOTE
"""

import os
import io
import json
import zipfile
import warnings
import requests
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report,
)

from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE

from preprocessor import TextPreprocessor

warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

SMS_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip"

SAMPLE_DATA = [
    ("spam", "WINNER!! You have been selected for a prize of 1000 pounds. Call 09061701461 to claim. T&C apply."),
    ("spam", "Free entry in 2 a weekly competition. Text WIN to 80085 now! 18+ TsCs apply."),
    ("spam", "Congratulations! You've won a FREE iPhone. Click here to claim: http://fake-prize.com"),
    ("spam", "URGENT: Your account has been suspended. Verify now: http://phish-site.net"),
    ("spam", "You are a WINNER of our monthly draw. Reply YES to claim your 5000 pound prize."),
    ("spam", "SIX chances to win CASH! From 100 to 20,000 pounds txt CSH11 and send to 87575."),
    ("spam", "Had your mobile 11 months or more? You are entitled to update to the latest colour mobiles."),
    ("spam", "IMPORTANT - You could be entitled up to 3160 pounds in compensation from mis-sold PPI."),
    ("spam", "Congratulations ur awarded 500 of CD vouchers or 125gift guaranteed and Free entry 2 100 wkly draw."),
    ("spam", "FREE MESSAGE: We are trying to contact U. Our records indicate your mobile number maybe awarded."),
    ("spam", "Call me back ASAP! Win a 1000 pound cash prize by texting CASH to 84484. Cost 50p per msg."),
    ("spam", "This is the 2nd time we have tried to contact u. U have won the 750 Pound prize."),
    ("spam", "Todays Voda numbers ending 7634 are selected to receive a 350 award. Text CLAIM to 81010."),
    ("spam", "Buy cheap Viagra online. No prescription needed. 80% off retail price. Order now!"),
    ("spam", "Make 500 to 1000 per day working from home! No experience needed. Limited spots available!"),
    ("spam", "Your PayPal account has been limited. Verify: http://paypal-secure-login.fake.com"),
    ("spam", "BANK ALERT: Unusual activity detected. Login immediately: http://bank-verify.scam.com"),
    ("spam", "Get a personal loan of up to 25000 pounds with no credit checks! Apply now."),
    ("spam", "FINAL NOTICE: You owe 500 in back taxes. Call 1-800-TAX-SCAM immediately."),
    ("spam", "Lose 30 lbs in 30 days with our miracle diet pill! 100% guaranteed or money back!"),
    ("spam", "You have been pre-approved for a 50000 loan. No credit check required. Act now!"),
    ("spam", "Your subscription is expiring. Renew now to avoid service interruption. Click here!"),
    ("spam", "Claim your free gift now! Just pay shipping. Limited time offer. Reply STOP to opt out."),
    ("spam", "Hot singles in your area want to meet you tonight! Click here to see their profiles."),
    ("spam", "Earn money fast! Join our network marketing program and earn passive income from day one!"),
    ("ham", "Hey, are you free for lunch tomorrow? I was thinking we could try that new Italian place."),
    ("ham", "Don't forget about the meeting at 3pm today. We'll be in conference room B."),
    ("ham", "I'll be home late tonight, traffic is terrible on the highway. Don't wait up."),
    ("ham", "Can you pick up some milk and eggs on your way home? We're out of both."),
    ("ham", "The project deadline has been moved to Friday. Please update your schedules accordingly."),
    ("ham", "Happy birthday! Hope you have a wonderful day. Looking forward to celebrating with you!"),
    ("ham", "Just finished the report you asked for. I've sent it to your email. Let me know if you need changes."),
    ("ham", "The kids are already in bed. Give me a call when you get a chance."),
    ("ham", "I'm at the grocery store, do you need anything? I'm grabbing dinner ingredients."),
    ("ham", "Meeting was cancelled today. We'll reschedule for next week. Check your calendar."),
    ("ham", "Thanks for helping me move last weekend. I really appreciate it! Dinner is on me."),
    ("ham", "Just checking in. How are you feeling? I heard you weren't well yesterday."),
    ("ham", "The train is delayed by 20 minutes. I'll be a bit late to the station."),
    ("ham", "Mom called and wants us to come for Sunday dinner. Are you available this weekend?"),
    ("ham", "I found a great recipe for the dish you were asking about. I'll share it with you later."),
    ("ham", "The quarterly results are in. We exceeded our targets by 15%. Great work team!"),
    ("ham", "Can you review the attached document and give me your feedback by end of day?"),
    ("ham", "Hi, this is a reminder about your dentist appointment tomorrow at 2pm."),
    ("ham", "The package you ordered has been delivered. Please check your front door."),
    ("ham", "Great game last night! Can't believe the overtime finish. We should watch the next one together."),
    ("ham", "I've attached the invoice for your review. Payment is due within 30 days."),
    ("ham", "The conference was fantastic. I learned so much and met some amazing people."),
    ("ham", "Sorry I missed your call. I was in a meeting. I'll call you back after 5pm."),
    ("ham", "Looking forward to the team outing on Friday! Should be a great time."),
    ("ham", "Your flight is confirmed for next Tuesday. Check-in opens 24 hours before departure."),
]


# ── Dataset ──────────────────────────────────────────────────────────────────

def download_sms_dataset():
    local_file = DATA_DIR / "SMSSpamCollection"
    if local_file.exists():
        print("  Found existing SMS dataset.")
        return pd.read_csv(local_file, sep='\t', header=None, names=['label', 'text'])
    print("  Downloading SMS Spam Collection from UCI...")
    try:
        resp = requests.get(SMS_URL, timeout=30)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            with zf.open('SMSSpamCollection') as f:
                content = f.read().decode('utf-8')
        local_file.write_text(content, encoding='utf-8')
        df = pd.read_csv(io.StringIO(content), sep='\t', header=None, names=['label', 'text'])
        print(f"  Downloaded {len(df)} samples.")
        return df
    except Exception as e:
        print(f"  Download failed: {e}")
        return None


def load_dataset():
    df = download_sms_dataset()
    if df is not None and len(df) > 100:
        return df
    for fname in ['dataset.csv', 'spam.csv', 'fake_news.csv']:
        fpath = DATA_DIR / fname
        if fpath.exists():
            df = pd.read_csv(fpath)
            if 'label' in df.columns and 'text' in df.columns:
                return df
    print("  Using built-in sample dataset.")
    return pd.DataFrame([{"label": l, "text": t} for l, t in SAMPLE_DATA])


# ── Model definitions ─────────────────────────────────────────────────────────

def build_pipelines():
    """
    5 pipelines:
      1. Logistic Regression      — class_weight='balanced'
      2. Naive Bayes              — baseline (no class_weight support)
      3. Random Forest            — class_weight='balanced'
      4. LinearSVC                — class_weight='balanced', calibrated for proba
      5. LR + SMOTE               — oversampling minority class
    """
    tfidf_base = dict(max_features=10_000, ngram_range=(1, 2), sublinear_tf=True, min_df=2)

    return {
        "Logistic Regression": Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf_base)),
            ("clf",   LogisticRegression(class_weight='balanced', max_iter=1000, C=1.0, random_state=42)),
        ]),
        "Naive Bayes": Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf_base)),
            ("clf",   MultinomialNB(alpha=0.1)),
        ]),
        "Random Forest": Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf_base)),
            ("clf",   RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42, n_jobs=-1)),
        ]),
        "LinearSVC": Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf_base)),
            ("clf",   CalibratedClassifierCV(
                LinearSVC(class_weight='balanced', max_iter=2000, C=1.0, random_state=42)
            )),
        ]),
        "LR + SMOTE": ImbPipeline([
            ("tfidf", TfidfVectorizer(**tfidf_base)),
            ("smote", SMOTE(random_state=42)),
            ("clf",   LogisticRegression(max_iter=1000, C=1.0, random_state=42)),
        ]),
    }


# ── GridSearchCV on best model ────────────────────────────────────────────────

def tune_best_model(name: str, pipeline, X_train, y_train) -> tuple:
    """Run GridSearchCV over TF-IDF + classifier hyperparameters."""
    print(f"\n  Running GridSearchCV on: {name}")

    if "Logistic Regression" in name:
        param_grid = {
            "tfidf__max_features": [8_000, 12_000],
            "tfidf__ngram_range":  [(1, 1), (1, 2)],
            "clf__C":              [0.1, 1.0, 10.0],
        }
    elif "Naive Bayes" in name:
        param_grid = {
            "tfidf__max_features": [8_000, 12_000],
            "tfidf__ngram_range":  [(1, 1), (1, 2)],
            "clf__alpha":          [0.01, 0.1, 0.5],
        }
    elif "LinearSVC" in name:
        param_grid = {
            "tfidf__max_features": [8_000, 12_000],
            "tfidf__ngram_range":  [(1, 1), (1, 2)],
            "clf__estimator__C":   [0.1, 1.0, 10.0],
        }
    elif "Random Forest" in name:
        param_grid = {
            "tfidf__max_features": [8_000, 12_000],
            "clf__n_estimators":   [100, 200],
            "clf__max_depth":      [None, 30],
        }
    else:  # SMOTE pipeline
        param_grid = {
            "tfidf__max_features": [8_000, 12_000],
            "tfidf__ngram_range":  [(1, 1), (1, 2)],
            "clf__C":              [0.1, 1.0, 10.0],
        }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    gs = GridSearchCV(pipeline, param_grid, cv=cv, scoring='f1_weighted', n_jobs=-1, verbose=0)
    gs.fit(X_train, y_train)

    print(f"  Best params : {gs.best_params_}")
    print(f"  Best CV F1  : {gs.best_score_:.4f}")
    return gs.best_estimator_, gs.best_params_


# ── Evaluation ────────────────────────────────────────────────────────────────

def evaluate_model(name, pipeline, X_test, y_test, classes):
    y_pred = pipeline.predict(X_test)
    proba  = pipeline.predict_proba(X_test)

    metrics = {
        "model_name": name,
        "accuracy":   round(accuracy_score(y_test, y_pred), 4),
        "precision":  round(precision_score(y_test, y_pred, average='weighted'), 4),
        "recall":     round(recall_score(y_test, y_pred, average='weighted'), 4),
        "f1_score":   round(f1_score(y_test, y_pred, average='weighted'), 4),
        # Per-class spam recall (most important metric)
        "spam_recall": round(recall_score(y_test, y_pred, average=None)[1], 4)
                       if len(classes) == 2 else None,
    }

    print(f"\n{'='*52}")
    print(f"  {name}")
    print(f"{'='*52}")
    for k, v in metrics.items():
        if k != "model_name" and v is not None:
            print(f"  {k:<14}: {v:.4f}")
    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=classes))

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes, ax=ax)
    ax.set_title(f'Confusion Matrix — {name}')
    ax.set_ylabel('True Label')
    ax.set_xlabel('Predicted Label')
    plt.tight_layout()
    safe = name.replace(' ', '_').replace('+', 'plus').lower()
    fig.savefig(MODEL_DIR / f"confusion_matrix_{safe}.png", dpi=120)
    plt.close(fig)

    return metrics


def plot_comparison(results):
    metric_keys = ['accuracy', 'precision', 'recall', 'f1_score', 'spam_recall']
    names  = [r['model_name'] for r in results]
    x      = np.arange(len(metric_keys))
    width  = 0.15
    colors = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#06b6d4']

    fig, ax = plt.subplots(figsize=(13, 6))
    for i, (r, color) in enumerate(zip(results, colors)):
        vals = [r.get(k) or 0 for k in metric_keys]
        bars = ax.bar(x + i * width, vals, width, label=r['model_name'], color=color, alpha=0.85)
        for bar, val in zip(bars, vals):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.004,
                        f'{val:.3f}', ha='center', va='bottom', fontsize=7, rotation=45)

    ax.set_title('Model Comparison (with class_weight, SMOTE, GridSearchCV)', fontsize=13)
    ax.set_xticks(x + width * (len(results) - 1) / 2)
    ax.set_xticklabels([k.replace('_', ' ').title() for k in metric_keys])
    ax.set_ylim(0, 1.15)
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    fig.savefig(MODEL_DIR / "model_comparison.png", dpi=130)
    plt.close(fig)
    print("  Saved model_comparison.png")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "="*60)
    print("  FAKE NEWS / SPAM DETECTION - IMPROVED TRAINER")
    print("  Fixes: class_weight + LinearSVC + GridSearchCV + SMOTE")
    print("="*60)

    # 1. Load data
    print("\n[1/6] Loading dataset...")
    df = load_dataset().dropna(subset=['text', 'label'])
    df['text'] = df['text'].astype(str)

    unique = sorted(df['label'].unique())
    if set(unique) <= {'ham', 'spam'}:
        df['label'] = df['label'].map({'ham': 0, 'spam': 1})
        classes = ['ham', 'spam']
    elif set(unique) <= {0, 1}:
        classes = ['ham', 'spam']
    elif set(unique) <= {'FAKE', 'REAL', 'fake', 'real'}:
        df['label'] = df['label'].str.upper().map({'REAL': 0, 'FAKE': 1})
        classes = ['real', 'fake']
    else:
        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        df['label'] = le.fit_transform(df['label'])
        classes = list(le.classes_)

    print(f"  Samples   : {len(df)}")
    vc = df['label'].value_counts()
    print(f"  {classes[0]:<6} : {vc.get(0, 0)}  ({vc.get(0,0)/len(df)*100:.1f}%)")
    print(f"  {classes[1]:<6} : {vc.get(1, 0)}  ({vc.get(1,0)/len(df)*100:.1f}%)")
    imbalance = vc.get(0, 1) / max(vc.get(1, 1), 1)
    print(f"  Imbalance ratio: {imbalance:.1f}x  {'(will be fixed by class_weight + SMOTE)' if imbalance > 2 else '(balanced)'}")

    # 2. Preprocess
    print("\n[2/6] Preprocessing text...")
    preprocessor = TextPreprocessor()
    df['processed'] = df['text'].apply(preprocessor.preprocess)
    print("  Done.")

    # 3. Split
    print("\n[3/6] Splitting data (80/20, stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        df['processed'], df['label'],
        test_size=0.2, random_state=42, stratify=df['label']
    )
    print(f"  Train: {len(X_train)} | Test: {len(X_test)}")
    tc = pd.Series(y_train).value_counts()
    print(f"  Train {classes[0]}: {tc.get(0,0)} | {classes[1]}: {tc.get(1,0)}")

    # 4. Train all models
    print("\n[4/6] Training 5 models (class_weight + SMOTE)...")
    pipelines = build_pipelines()
    results   = []
    trained   = {}

    for name, pipe in pipelines.items():
        print(f"\n  Training {name}...")
        pipe.fit(X_train, y_train)
        metrics = evaluate_model(name, pipe, X_test, y_test, classes)
        results.append(metrics)
        trained[name] = pipe

    # 5. GridSearchCV on best model
    print("\n[5/6] GridSearchCV on best model...")
    best_initial = max(results, key=lambda r: r['f1_score'])
    best_name    = best_initial['model_name']
    print(f"  Best so far: {best_name} (F1={best_initial['f1_score']:.4f})")

    tuned_pipe, best_params = tune_best_model(
        best_name, build_pipelines()[best_name], X_train, y_train
    )
    tuned_metrics = evaluate_model(f"{best_name} (Tuned)", tuned_pipe, X_test, y_test, classes)
    results.append(tuned_metrics)
    trained[f"{best_name} (Tuned)"] = tuned_pipe

    plot_comparison(results)

    # 6. Save best overall
    print("\n[6/6] Saving best model...")
    champion = max(results, key=lambda r: r['f1_score'])
    champion_model = trained[champion['model_name']]

    joblib.dump(champion_model, MODEL_DIR / "best_model.joblib")

    info = {
        **champion,
        "classes":       classes,
        "label_map":     {"0": classes[0], "1": classes[1]},
        "best_params":   best_params,
        "train_samples": len(X_train),
        "test_samples":  len(X_test),
        "all_results":   results,
    }
    (MODEL_DIR / "model_info.json").write_text(json.dumps(info, indent=2))

    # Summary table
    print("\n" + "="*60)
    print(f"  {'Model':<30} {'Accuracy':>9} {'F1':>8} {'SpamRecall':>11}")
    print("  " + "-"*56)
    for r in sorted(results, key=lambda x: x['f1_score'], reverse=True):
        marker = " <-- BEST" if r['model_name'] == champion['model_name'] else ""
        sr = f"{r['spam_recall']:.4f}" if r.get('spam_recall') else "  N/A  "
        print(f"  {r['model_name']:<30} {r['accuracy']:>9.4f} {r['f1_score']:>8.4f} {sr:>11}{marker}")

    print("\n" + "="*60)
    print(f"  Best model : {champion['model_name']}")
    print(f"  Accuracy   : {champion['accuracy']:.4f}")
    print(f"  F1-score   : {champion['f1_score']:.4f}")
    if champion.get('spam_recall'):
        print(f"  Spam Recall: {champion['spam_recall']:.4f}")
    print(f"\n  Saved -> models/best_model.joblib")
    print(f"  Saved -> models/model_info.json")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
